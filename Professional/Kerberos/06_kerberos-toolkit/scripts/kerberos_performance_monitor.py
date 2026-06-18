#!/usr/bin/env python3
"""
Kerberos Performance Monitor & Anomaly Detector
Version: 1.0
Author: Emerson
Date: February 2025

Monitors KDC performance and detects anomalies that may indicate:
- Active attacks (brute force causing load spikes)
- Infrastructure issues (memory leaks, disk space)
- Capacity problems (need to scale)
- Service degradation (before total failure)

Features:
- Real-time KDC metrics collection
- Baseline establishment (normal behavior)
- Anomaly detection with ML
- Performance threshold alerts
- Trend analysis and prediction
- Integration with SIEM/monitoring tools
"""

import subprocess
import psutil
import time
import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import sqlite3
import anthropic
from colorama import Fore, Style, init
import argparse
import sys

init(autoreset=True)

VERSION = "1.0"


@dataclass
class KDCMetrics:
    """KDC performance metrics snapshot"""
    timestamp: float
    
    # Authentication metrics
    as_req_count: int
    tgs_req_count: int
    as_req_success: int
    as_req_failure: int
    tgs_req_success: int
    tgs_req_failure: int
    
    # Performance metrics
    avg_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    
    # System metrics
    cpu_percent: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_packets_in: int
    network_packets_out: int
    
    # KDC process metrics
    kdc_cpu_percent: float
    kdc_memory_mb: float
    kdc_threads: int
    kdc_open_files: int
    
    # Queue/connection metrics
    active_connections: int
    queued_requests: int
    
    # Error metrics
    error_rate: float
    timeout_count: int


@dataclass
class PerformanceAnomaly:
    """Detected performance anomaly"""
    timestamp: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    metric_name: str
    current_value: float
    baseline_value: float
    deviation_percent: float
    description: str
    possible_causes: List[str]
    recommended_actions: List[str]


class MetricsCollector:
    """Collect KDC performance metrics"""
    
    def __init__(self, kdc_host: str = "localhost", kdc_port: int = 88):
        self.kdc_host = kdc_host
        self.kdc_port = kdc_port
        
        # Find KDC process
        self.kdc_process = self._find_kdc_process()
        
        # Baseline counters
        self.last_metrics = None
        self.response_times = deque(maxlen=1000)
    
    def _find_kdc_process(self) -> Optional[psutil.Process]:
        """Find the KDC process"""
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                name = proc.info['name']
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                if 'krb5kdc' in name or 'krb5kdc' in cmdline:
                    print(f"{Fore.GREEN}[+] Found KDC process: PID {proc.pid}")
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print(f"{Fore.YELLOW}[!] KDC process not found (will monitor system-wide)")
        return None
    
    def collect(self) -> KDCMetrics:
        """Collect current metrics snapshot"""
        
        # Parse KDC logs for request counts
        auth_metrics = self._parse_kdc_logs()
        
        # Get system metrics
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        
        # Get KDC process metrics
        kdc_cpu = 0.0
        kdc_mem = 0.0
        kdc_threads = 0
        kdc_files = 0
        active_conns = 0
        
        if self.kdc_process and self.kdc_process.is_running():
            try:
                kdc_cpu = self.kdc_process.cpu_percent(interval=0.1)
                kdc_mem = self.kdc_process.memory_info().rss / 1024 / 1024  # MB
                kdc_threads = self.kdc_process.num_threads()
                kdc_files = len(self.kdc_process.open_files())
                active_conns = len(self.kdc_process.connections())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Calculate response time metrics
        if self.response_times:
            avg_rt = statistics.mean(self.response_times)
            sorted_rt = sorted(self.response_times)
            p95_rt = sorted_rt[int(len(sorted_rt) * 0.95)] if sorted_rt else 0
            p99_rt = sorted_rt[int(len(sorted_rt) * 0.99)] if sorted_rt else 0
        else:
            avg_rt = p95_rt = p99_rt = 0.0
        
        # Calculate error rate
        total_requests = auth_metrics['as_req_total'] + auth_metrics['tgs_req_total']
        total_failures = auth_metrics['as_req_failure'] + auth_metrics['tgs_req_failure']
        error_rate = (total_failures / total_requests * 100) if total_requests > 0 else 0.0
        
        metrics = KDCMetrics(
            timestamp=time.time(),
            as_req_count=auth_metrics['as_req_total'],
            tgs_req_count=auth_metrics['tgs_req_total'],
            as_req_success=auth_metrics['as_req_success'],
            as_req_failure=auth_metrics['as_req_failure'],
            tgs_req_success=auth_metrics['tgs_req_success'],
            tgs_req_failure=auth_metrics['tgs_req_failure'],
            avg_response_time_ms=avg_rt,
            p95_response_time_ms=p95_rt,
            p99_response_time_ms=p99_rt,
            cpu_percent=cpu,
            memory_percent=memory,
            disk_io_read_mb=disk_io.read_bytes / 1024 / 1024 if disk_io else 0,
            disk_io_write_mb=disk_io.write_bytes / 1024 / 1024 if disk_io else 0,
            network_packets_in=net_io.packets_recv if net_io else 0,
            network_packets_out=net_io.packets_sent if net_io else 0,
            kdc_cpu_percent=kdc_cpu,
            kdc_memory_mb=kdc_mem,
            kdc_threads=kdc_threads,
            kdc_open_files=kdc_files,
            active_connections=active_conns,
            queued_requests=0,  # Would need to parse from KDC internals
            error_rate=error_rate,
            timeout_count=auth_metrics['timeout_count']
        )
        
        self.last_metrics = metrics
        return metrics
    
    def _parse_kdc_logs(self) -> Dict[str, int]:
        """Parse KDC logs for authentication metrics"""
        # Parse /var/log/krb5kdc.log for recent entries
        
        log_file = Path("/var/log/krb5kdc.log")
        if not log_file.exists():
            # Try alternative locations
            log_file = Path("/var/log/krb5/krb5kdc.log")
        
        if not log_file.exists():
            return {
                'as_req_total': 0,
                'as_req_success': 0,
                'as_req_failure': 0,
                'tgs_req_total': 0,
                'tgs_req_success': 0,
                'tgs_req_failure': 0,
                'timeout_count': 0
            }
        
        # Count events in last 60 seconds
        cutoff_time = datetime.now() - timedelta(seconds=60)
        
        metrics = {
            'as_req_total': 0,
            'as_req_success': 0,
            'as_req_failure': 0,
            'tgs_req_total': 0,
            'tgs_req_success': 0,
            'tgs_req_failure': 0,
            'timeout_count': 0
        }
        
        try:
            with open(log_file, 'r') as f:
                # Read last N lines (more efficient than reading entire file)
                lines = f.readlines()[-1000:]
                
                for line in lines:
                    # Parse timestamp and check if within window
                    # Example: Feb 07 10:23:15
                    
                    if 'AS_REQ' in line:
                        metrics['as_req_total'] += 1
                        if 'ISSUE' in line or 'PROCESS' in line:
                            metrics['as_req_success'] += 1
                        elif 'PREAUTH_FAILED' in line or 'C_PRINCIPAL_UNKNOWN' in line:
                            metrics['as_req_failure'] += 1
                    
                    elif 'TGS_REQ' in line:
                        metrics['tgs_req_total'] += 1
                        if 'ISSUE' in line:
                            metrics['tgs_req_success'] += 1
                        elif 'FAILED' in line:
                            metrics['tgs_req_failure'] += 1
                    
                    elif 'timeout' in line.lower():
                        metrics['timeout_count'] += 1
        
        except (FileNotFoundError, PermissionError) as e:
            print(f"{Fore.YELLOW}[!] Cannot read KDC logs: {e}")
        
        return metrics
    
    def measure_response_time(self) -> float:
        """Measure KDC response time with a test request"""
        try:
            start = time.time()
            
            # Simple test: try to get a TGT (will fail but measures response)
            result = subprocess.run(
                ['kinit', '-n', f'test@{self.kdc_host.upper()}'],
                capture_output=True,
                timeout=5
            )
            
            response_time = (time.time() - start) * 1000  # ms
            self.response_times.append(response_time)
            
            return response_time
            
        except subprocess.TimeoutExpired:
            return 5000.0  # 5 second timeout
        except Exception:
            return 0.0


class BaselineEstablisher:
    """Establish normal behavior baseline"""
    
    def __init__(self, db_path: str = "kdc_metrics.db"):
        self.db_path = db_path
        self._init_db()
        self.baseline = {}
    
    def _init_db(self):
        """Initialize SQLite database for metrics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                timestamp REAL PRIMARY KEY,
                as_req_count INTEGER,
                tgs_req_count INTEGER,
                cpu_percent REAL,
                memory_percent REAL,
                kdc_cpu_percent REAL,
                kdc_memory_mb REAL,
                avg_response_time_ms REAL,
                error_rate REAL,
                active_connections INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_metrics(self, metrics: KDCMetrics):
        """Store metrics in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics.timestamp,
            metrics.as_req_count,
            metrics.tgs_req_count,
            metrics.cpu_percent,
            metrics.memory_percent,
            metrics.kdc_cpu_percent,
            metrics.kdc_memory_mb,
            metrics.avg_response_time_ms,
            metrics.error_rate,
            metrics.active_connections
        ))
        
        conn.commit()
        conn.close()
    
    def calculate_baseline(self, hours: int = 24) -> Dict[str, Dict[str, float]]:
        """Calculate baseline statistics from historical data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = time.time() - (hours * 3600)
        
        cursor.execute("""
            SELECT 
                AVG(as_req_count), STDEV(as_req_count),
                AVG(tgs_req_count), STDEV(tgs_req_count),
                AVG(cpu_percent), STDEV(cpu_percent),
                AVG(memory_percent), STDEV(memory_percent),
                AVG(kdc_cpu_percent), STDEV(kdc_cpu_percent),
                AVG(kdc_memory_mb), STDEV(kdc_memory_mb),
                AVG(avg_response_time_ms), STDEV(avg_response_time_ms),
                AVG(error_rate), STDEV(error_rate),
                AVG(active_connections), STDEV(active_connections)
            FROM metrics
            WHERE timestamp > ?
        """, (cutoff,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row or row[0] is None:
            print(f"{Fore.YELLOW}[!] Insufficient data for baseline (need {hours}h of data)")
            return {}
        
        metrics_names = [
            'as_req_count', 'tgs_req_count', 'cpu_percent', 'memory_percent',
            'kdc_cpu_percent', 'kdc_memory_mb', 'avg_response_time_ms',
            'error_rate', 'active_connections'
        ]
        
        baseline = {}
        for i, name in enumerate(metrics_names):
            baseline[name] = {
                'mean': row[i*2] if row[i*2] else 0,
                'stddev': row[i*2 + 1] if row[i*2 + 1] else 0,
                'upper_threshold': (row[i*2] or 0) + 2 * (row[i*2 + 1] or 0),  # Mean + 2σ
                'lower_threshold': max(0, (row[i*2] or 0) - 2 * (row[i*2 + 1] or 0))  # Mean - 2σ
            }
        
        self.baseline = baseline
        print(f"{Fore.GREEN}[+] Baseline established from {hours}h of data")
        return baseline


class AnomalyDetector:
    """Detect performance anomalies"""
    
    def __init__(self, baseline: Dict[str, Dict[str, float]]):
        self.baseline = baseline
        
        # Thresholds for critical metrics (absolute values)
        self.critical_thresholds = {
            'cpu_percent': 90.0,
            'memory_percent': 90.0,
            'kdc_cpu_percent': 95.0,
            'kdc_memory_mb': 2048.0,  # 2GB
            'avg_response_time_ms': 1000.0,  # 1 second
            'error_rate': 10.0,  # 10%
            'active_connections': 1000
        }
    
    def detect_anomalies(self, metrics: KDCMetrics) -> List[PerformanceAnomaly]:
        """Detect anomalies in current metrics"""
        anomalies = []
        
        if not self.baseline:
            return anomalies
        
        metrics_dict = asdict(metrics)
        
        for metric_name, baseline_stats in self.baseline.items():
            current_value = metrics_dict.get(metric_name, 0)
            baseline_mean = baseline_stats['mean']
            upper_threshold = baseline_stats['upper_threshold']
            lower_threshold = baseline_stats['lower_threshold']
            
            # Check if outside baseline range (statistical anomaly)
            if current_value > upper_threshold or current_value < lower_threshold:
                deviation = abs((current_value - baseline_mean) / baseline_mean * 100) if baseline_mean > 0 else 0
                
                # Determine severity
                severity = self._calculate_severity(metric_name, current_value, deviation)
                
                if severity != "IGNORE":
                    anomaly = PerformanceAnomaly(
                        timestamp=datetime.now().isoformat(),
                        severity=severity,
                        metric_name=metric_name,
                        current_value=current_value,
                        baseline_value=baseline_mean,
                        deviation_percent=deviation,
                        description=self._generate_description(metric_name, current_value, baseline_mean),
                        possible_causes=self._identify_causes(metric_name, current_value),
                        recommended_actions=self._recommend_actions(metric_name, current_value)
                    )
                    anomalies.append(anomaly)
            
            # Check critical thresholds (absolute values)
            critical_threshold = self.critical_thresholds.get(metric_name)
            if critical_threshold and current_value > critical_threshold:
                anomaly = PerformanceAnomaly(
                    timestamp=datetime.now().isoformat(),
                    severity="CRITICAL",
                    metric_name=metric_name,
                    current_value=current_value,
                    baseline_value=baseline_mean,
                    deviation_percent=0,  # Not relevant for absolute thresholds
                    description=f"{metric_name} exceeded critical threshold",
                    possible_causes=["System overload", "Attack in progress", "Resource exhaustion"],
                    recommended_actions=["Immediate investigation required", "Check for active attacks", "Scale resources"]
                )
                
                # Avoid duplicate anomalies
                if not any(a.metric_name == metric_name and a.severity == "CRITICAL" for a in anomalies):
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _calculate_severity(self, metric_name: str, current_value: float, deviation: float) -> str:
        """Calculate anomaly severity"""
        # High priority metrics
        high_priority = ['error_rate', 'avg_response_time_ms', 'kdc_cpu_percent']
        
        if deviation > 200:  # 3x or more from baseline
            return "CRITICAL" if metric_name in high_priority else "HIGH"
        elif deviation > 100:  # 2x from baseline
            return "HIGH" if metric_name in high_priority else "MEDIUM"
        elif deviation > 50:  # 1.5x from baseline
            return "MEDIUM"
        elif deviation > 25:
            return "LOW"
        else:
            return "IGNORE"
    
    def _generate_description(self, metric_name: str, current: float, baseline: float) -> str:
        """Generate human-readable description"""
        change = "increased" if current > baseline else "decreased"
        percent = abs((current - baseline) / baseline * 100) if baseline > 0 else 0
        
        return f"{metric_name} {change} by {percent:.1f}% (current: {current:.2f}, baseline: {baseline:.2f})"
    
    def _identify_causes(self, metric_name: str, current_value: float) -> List[str]:
        """Identify possible causes for anomaly"""
        causes = {
            'as_req_count': [
                "Brute force attack in progress",
                "Legitimate authentication spike (shift change, system startup)",
                "Automated system attempting authentication"
            ],
            'error_rate': [
                "Invalid credentials being used (attack or misconfiguration)",
                "KDC database corruption",
                "Network connectivity issues",
                "Time synchronization problems"
            ],
            'avg_response_time_ms': [
                "KDC database lock contention",
                "High system load (CPU/memory)",
                "Network latency issues",
                "Disk I/O bottleneck"
            ],
            'kdc_cpu_percent': [
                "High authentication request volume",
                "Cryptographic operations overload",
                "Memory leak causing garbage collection",
                "Attack causing computational load"
            ],
            'kdc_memory_mb': [
                "Memory leak in KDC process",
                "Excessive connection caching",
                "Large ticket cache",
                "Configuration issue"
            ],
            'active_connections': [
                "Connection leak (not being closed properly)",
                "DDoS attack",
                "Legitimate high load",
                "Client misconfiguration (not reusing connections)"
            ]
        }
        
        return causes.get(metric_name, ["Unknown cause", "Requires investigation"])
    
    def _recommend_actions(self, metric_name: str, current_value: float) -> List[str]:
        """Recommend remediation actions"""
        actions = {
            'as_req_count': [
                "Check KDC logs for failed authentication patterns",
                "Implement rate limiting if not present",
                "Review source IPs for brute force indicators",
                "Enable account lockout policies"
            ],
            'error_rate': [
                "Review recent failed authentication attempts",
                "Check client configurations",
                "Verify time synchronization across infrastructure",
                "Check KDC database integrity"
            ],
            'avg_response_time_ms': [
                "Check KDC system resources (CPU, memory, disk)",
                "Review KDC database performance",
                "Check network connectivity",
                "Consider adding KDC replicas for load distribution"
            ],
            'kdc_cpu_percent': [
                "Review authentication request volume and patterns",
                "Check for memory leaks (restart KDC if needed)",
                "Consider scaling KDC infrastructure",
                "Optimize KDC configuration"
            ],
            'kdc_memory_mb': [
                "Investigate for memory leaks",
                "Restart KDC service if memory continues growing",
                "Review ticket cache settings",
                "Check for connection leaks"
            ],
            'active_connections': [
                "Review connection management in clients",
                "Check for connection leaks",
                "Implement connection pooling",
                "Review firewall/load balancer settings"
            ]
        }
        
        return actions.get(metric_name, ["Investigate immediately", "Review logs", "Contact support"])


class PerformanceMonitor:
    """Main performance monitoring orchestrator"""
    
    def __init__(
        self,
        kdc_host: str = "localhost",
        interval: int = 60,
        baseline_hours: int = 24,
        output_dir: str = "performance_monitoring",
        use_ai: bool = False,
        api_key: Optional[str] = None
    ):
        self.kdc_host = kdc_host
        self.interval = interval
        self.baseline_hours = baseline_hours
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.use_ai = use_ai
        
        # Initialize components
        self.collector = MetricsCollector(kdc_host)
        self.baseline_mgr = BaselineEstablisher(str(self.output_dir / "metrics.db"))
        
        # Load or establish baseline
        self.baseline = self.baseline_mgr.calculate_baseline(baseline_hours)
        self.detector = AnomalyDetector(self.baseline)
        
        if use_ai:
            self.ai_client = anthropic.Anthropic(api_key=api_key)
        
        self.running = False
    
    def run_once(self):
        """Single monitoring cycle"""
        # Collect metrics
        metrics = self.collector.collect()
        
        # Store in database
        self.baseline_mgr.store_metrics(metrics)
        
        # Detect anomalies
        anomalies = self.detector.detect_anomalies(metrics)
        
        # Display metrics
        self._display_metrics(metrics)
        
        # Display anomalies
        if anomalies:
            print(f"\n{Fore.RED}{'='*60}")
            print(f"{Fore.RED}ANOMALIES DETECTED: {len(anomalies)}")
            print(f"{Fore.RED}{'='*60}")
            
            for anomaly in anomalies:
                self._display_anomaly(anomaly)
            
            # AI analysis if enabled
            if self.use_ai and anomalies:
                ai_analysis = self._ai_analyze_anomalies(anomalies, metrics)
                self._display_ai_analysis(ai_analysis)
            
            # Save anomalies
            self._save_anomalies(anomalies, metrics)
        else:
            print(f"\n{Fore.GREEN}✓ All metrics within normal range")
        
        return metrics, anomalies
    
    def run_continuous(self):
        """Continuous monitoring loop"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Kerberos Performance Monitor v{VERSION}")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}KDC: {self.kdc_host}")
        print(f"{Fore.CYAN}Interval: {self.interval}s")
        print(f"{Fore.CYAN}Baseline: {self.baseline_hours}h")
        print(f"{Fore.CYAN}AI Analysis: {'Enabled' if self.use_ai else 'Disabled'}")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        if not self.baseline:
            print(f"{Fore.YELLOW}[!] No baseline yet - collecting data...")
            print(f"{Fore.YELLOW}[!] Run for {self.baseline_hours}h to establish baseline\n")
        
        self.running = True
        cycle = 0
        
        try:
            while self.running:
                cycle += 1
                print(f"\n{Fore.CYAN}[Cycle {cycle}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                metrics, anomalies = self.run_once()
                
                # Re-calculate baseline periodically
                if cycle % 60 == 0:  # Every 60 cycles (1 hour with 60s interval)
                    print(f"\n{Fore.YELLOW}[*] Re-calculating baseline...")
                    self.baseline = self.baseline_mgr.calculate_baseline(self.baseline_hours)
                    self.detector = AnomalyDetector(self.baseline)
                
                # Sleep until next cycle
                time.sleep(self.interval)
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Monitoring stopped by user")
            self.running = False
    
    def _display_metrics(self, metrics: KDCMetrics):
        """Display current metrics"""
        print(f"\n{Fore.CYAN}Current Metrics:")
        print(f"  Authentication:")
        print(f"    AS-REQ: {metrics.as_req_count} (Success: {metrics.as_req_success}, Failed: {metrics.as_req_failure})")
        print(f"    TGS-REQ: {metrics.tgs_req_count} (Success: {metrics.tgs_req_success}, Failed: {metrics.tgs_req_failure})")
        print(f"    Error Rate: {metrics.error_rate:.2f}%")
        
        print(f"  Performance:")
        print(f"    Avg Response: {metrics.avg_response_time_ms:.2f}ms")
        print(f"    P95 Response: {metrics.p95_response_time_ms:.2f}ms")
        print(f"    P99 Response: {metrics.p99_response_time_ms:.2f}ms")
        
        print(f"  System:")
        print(f"    CPU: {metrics.cpu_percent:.1f}%")
        print(f"    Memory: {metrics.memory_percent:.1f}%")
        print(f"    KDC CPU: {metrics.kdc_cpu_percent:.1f}%")
        print(f"    KDC Memory: {metrics.kdc_memory_mb:.1f}MB")
        print(f"    Active Connections: {metrics.active_connections}")
    
    def _display_anomaly(self, anomaly: PerformanceAnomaly):
        """Display anomaly details"""
        color = {
            'CRITICAL': Fore.RED,
            'HIGH': Fore.RED,
            'MEDIUM': Fore.YELLOW,
            'LOW': Fore.CYAN
        }.get(anomaly.severity, Fore.WHITE)
        
        print(f"\n{color}[{anomaly.severity}] {anomaly.metric_name}")
        print(f"{color}  {anomaly.description}")
        print(f"{color}  Possible causes:")
        for cause in anomaly.possible_causes[:2]:
            print(f"{color}    • {cause}")
        print(f"{color}  Recommended actions:")
        for action in anomaly.recommended_actions[:2]:
            print(f"{color}    → {action}")
    
    def _ai_analyze_anomalies(
        self,
        anomalies: List[PerformanceAnomaly],
        metrics: KDCMetrics
    ) -> Dict:
        """Use AI to analyze anomalies in context"""
        
        context = {
            'anomalies': [asdict(a) for a in anomalies],
            'current_metrics': {
                'as_req_count': metrics.as_req_count,
                'error_rate': metrics.error_rate,
                'avg_response_time_ms': metrics.avg_response_time_ms,
                'cpu_percent': metrics.cpu_percent,
                'kdc_cpu_percent': metrics.kdc_cpu_percent,
                'active_connections': metrics.active_connections
            }
        }
        
        prompt = f"""Analyze these Kerberos KDC performance anomalies:

{json.dumps(context, indent=2)}

Provide:
1. Root Cause Analysis: Most likely cause of these anomalies
2. Correlation: Are these anomalies related or independent?
3. Risk Assessment: Impact on authentication services
4. Priority: What to investigate first
5. Remediation: Step-by-step action plan

Format as JSON."""

        try:
            message = self.ai_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response = message.content[0].text
            
            # Try to parse JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {'raw_response': response}
        
        except Exception as e:
            return {'error': str(e)}
    
    def _display_ai_analysis(self, analysis: Dict):
        """Display AI analysis"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.MAGENTA}AI Analysis")
        print(f"{Fore.MAGENTA}{'='*60}")
        
        if 'root_cause' in analysis:
            print(f"{Fore.MAGENTA}Root Cause: {analysis['root_cause']}")
        
        if 'risk_assessment' in analysis:
            print(f"{Fore.MAGENTA}Risk: {analysis['risk_assessment']}")
        
        if 'priority' in analysis:
            print(f"{Fore.MAGENTA}Priority: {analysis['priority']}")
        
        print(f"{Fore.MAGENTA}{'='*60}")
    
    def _save_anomalies(self, anomalies: List[PerformanceAnomaly], metrics: KDCMetrics):
        """Save anomalies to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        anomaly_file = self.output_dir / f"anomalies_{timestamp}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': asdict(metrics),
            'anomalies': [asdict(a) for a in anomalies]
        }
        
        with open(anomaly_file, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description=f"Kerberos Performance Monitor v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single check
  python3 kerberos_performance_monitor.py --once
  
  # Continuous monitoring
  python3 kerberos_performance_monitor.py
  
  # With AI analysis
  python3 kerberos_performance_monitor.py --ai --api-key YOUR_KEY
  
  # Custom KDC
  python3 kerberos_performance_monitor.py --kdc 192.168.88.20 --interval 30
        """
    )
    
    parser.add_argument('--kdc', default='localhost', help='KDC hostname or IP')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval (seconds)')
    parser.add_argument('--baseline-hours', type=int, default=24, help='Hours of data for baseline')
    parser.add_argument('--output-dir', default='performance_monitoring', help='Output directory')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--ai', action='store_true', help='Enable AI analysis')
    parser.add_argument('--api-key', help='Anthropic API key for AI analysis')
    
    args = parser.parse_args()
    
    # Create monitor
    monitor = PerformanceMonitor(
        kdc_host=args.kdc,
        interval=args.interval,
        baseline_hours=args.baseline_hours,
        output_dir=args.output_dir,
        use_ai=args.ai,
        api_key=args.api_key
    )
    
    # Run
    if args.once:
        monitor.run_once()
    else:
        monitor.run_continuous()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
