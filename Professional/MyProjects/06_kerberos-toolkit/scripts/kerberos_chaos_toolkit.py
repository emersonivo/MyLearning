#!/usr/bin/env python3
"""
Kerberos Chaos Engineering Toolkit
Version: 1.0
Author: Emerson
Date: February 2025

Safely simulate real-world Kerberos infrastructure problems for:
- Testing monitoring systems
- Training incident response
- Validating detection capabilities
- Creating demo scenarios

⚠️  USE ONLY IN ISOLATED LAB ENVIRONMENTS
⚠️  DO NOT RUN IN PRODUCTION

Features:
- Memory leak simulation
- CPU exhaustion
- Disk space filling
- Database corruption
- Network latency injection
- Service degradation
- Connection exhaustion
- Clock skew simulation
"""

import subprocess
import time
import os
import sys
import signal
import random
import argparse
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta
import threading
from colorama import Fore, Style, init

init(autoreset=True)

VERSION = "1.0"


class SafetyCheck:
    """Ensure we're in a safe environment"""
    
    @staticmethod
    def confirm_lab_environment():
        """Verify this is a lab environment"""
        print(f"\n{Fore.RED}{'='*60}")
        print(f"{Fore.RED}⚠️  WARNING: CHAOS ENGINEERING TOOLKIT ⚠️")
        print(f"{Fore.RED}{'='*60}")
        print(f"{Fore.RED}This will intentionally cause problems in your KDC!")
        print(f"{Fore.RED}ONLY use in isolated lab environments!")
        print(f"{Fore.RED}{'='*60}\n")
        
        # Check hostname
        hostname = subprocess.check_output(['hostname']).decode().strip()
        print(f"{Fore.YELLOW}Current hostname: {hostname}")
        
        # Check if production-like names
        production_indicators = ['prod', 'production', 'live', 'corporate', 'corp']
        if any(indicator in hostname.lower() for indicator in production_indicators):
            print(f"{Fore.RED}[!] Hostname suggests production environment!")
            print(f"{Fore.RED}[!] ABORTING for safety")
            sys.exit(1)
        
        # Require explicit confirmation
        print(f"\n{Fore.YELLOW}Type 'I UNDERSTAND THIS IS A LAB' to continue:")
        confirmation = input("> ")
        
        if confirmation != "I UNDERSTAND THIS IS A LAB":
            print(f"{Fore.RED}[!] Confirmation failed. Exiting.")
            sys.exit(1)
        
        print(f"{Fore.GREEN}[+] Lab environment confirmed\n")


class MemoryLeakSimulator:
    """Simulate memory leak in KDC or system"""
    
    def __init__(self, rate_mb_per_sec: float = 10.0, max_mb: int = 1024):
        self.rate_mb_per_sec = rate_mb_per_sec
        self.max_mb = max_mb
        self.allocated_memory = []
        self.running = False
        self.thread = None
    
    def start(self):
        """Start memory leak simulation"""
        print(f"{Fore.YELLOW}[*] Starting memory leak simulation")
        print(f"{Fore.YELLOW}    Rate: {self.rate_mb_per_sec} MB/sec")
        print(f"{Fore.YELLOW}    Max: {self.max_mb} MB")
        print(f"{Fore.YELLOW}    Press Ctrl+C to stop\n")
        
        self.running = True
        self.thread = threading.Thread(target=self._leak_memory, daemon=True)
        self.thread.start()
        
        try:
            while self.running:
                allocated_mb = sum(len(chunk) for chunk in self.allocated_memory) / 1024 / 1024
                print(f"{Fore.CYAN}[*] Allocated: {allocated_mb:.1f} MB", end='\r')
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Stopping memory leak...")
            self.stop()
    
    def _leak_memory(self):
        """Allocate memory gradually"""
        while self.running:
            current_mb = sum(len(chunk) for chunk in self.allocated_memory) / 1024 / 1024
            
            if current_mb >= self.max_mb:
                print(f"\n{Fore.YELLOW}[!] Reached max memory ({self.max_mb} MB)")
                self.running = False
                break
            
            # Allocate memory (1MB chunks)
            chunk_size = int(self.rate_mb_per_sec * 1024 * 1024)
            chunk = bytearray(chunk_size)
            self.allocated_memory.append(chunk)
            
            time.sleep(1)
    
    def stop(self):
        """Stop and free memory"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        
        allocated_mb = sum(len(chunk) for chunk in self.allocated_memory) / 1024 / 1024
        print(f"{Fore.GREEN}[+] Released {allocated_mb:.1f} MB")
        self.allocated_memory.clear()


class CPUExhaustionSimulator:
    """Simulate CPU exhaustion"""
    
    def __init__(self, num_threads: int = 4, intensity: float = 0.9):
        self.num_threads = num_threads
        self.intensity = intensity  # 0.0 - 1.0
        self.running = False
        self.threads = []
    
    def start(self, duration: int = 60):
        """Start CPU exhaustion"""
        print(f"{Fore.YELLOW}[*] Starting CPU exhaustion simulation")
        print(f"{Fore.YELLOW}    Threads: {self.num_threads}")
        print(f"{Fore.YELLOW}    Intensity: {self.intensity * 100:.0f}%")
        print(f"{Fore.YELLOW}    Duration: {duration}s\n")
        
        self.running = True
        
        # Start worker threads
        for i in range(self.num_threads):
            t = threading.Thread(target=self._burn_cpu, args=(i,), daemon=True)
            t.start()
            self.threads.append(t)
        
        # Run for duration
        try:
            for remaining in range(duration, 0, -1):
                print(f"{Fore.CYAN}[*] CPU burning... ({remaining}s remaining)", end='\r')
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Interrupted")
        
        self.stop()
    
    def _burn_cpu(self, thread_id: int):
        """CPU-intensive calculation"""
        while self.running:
            # Compute-heavy operation
            _ = sum(i * i for i in range(100000))
            
            # Intensity control (0.9 = burn 90% of time, sleep 10%)
            if self.intensity < 1.0:
                time.sleep((1.0 - self.intensity) * 0.01)
    
    def stop(self):
        """Stop CPU burn"""
        self.running = False
        for t in self.threads:
            t.join(timeout=1)
        print(f"\n{Fore.GREEN}[+] CPU exhaustion stopped")


class DiskSpaceSimulator:
    """Fill disk space gradually"""
    
    def __init__(self, target_path: str = "/tmp/kdc_chaos", fill_mb: int = 1024):
        self.target_path = Path(target_path)
        self.fill_mb = fill_mb
        self.created_files = []
    
    def start(self):
        """Fill disk space"""
        print(f"{Fore.YELLOW}[*] Starting disk space fill simulation")
        print(f"{Fore.YELLOW}    Path: {self.target_path}")
        print(f"{Fore.YELLOW}    Size: {self.fill_mb} MB\n")
        
        # Create directory
        self.target_path.mkdir(exist_ok=True, parents=True)
        
        # Fill with files
        chunk_size = 10 * 1024 * 1024  # 10 MB chunks
        total_written = 0
        
        try:
            while total_written < self.fill_mb * 1024 * 1024:
                filename = self.target_path / f"filler_{len(self.created_files)}.dat"
                
                # Write chunk
                with open(filename, 'wb') as f:
                    f.write(os.urandom(chunk_size))
                
                self.created_files.append(filename)
                total_written += chunk_size
                
                print(f"{Fore.CYAN}[*] Written: {total_written / 1024 / 1024:.1f} MB", end='\r')
                
                time.sleep(0.5)  # Gradual fill
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Interrupted")
        
        print(f"\n{Fore.GREEN}[+] Filled {total_written / 1024 / 1024:.1f} MB")
        print(f"{Fore.YELLOW}[!] Run cleanup() to remove files")
    
    def cleanup(self):
        """Remove created files"""
        print(f"{Fore.YELLOW}[*] Cleaning up disk space...")
        
        for filename in self.created_files:
            try:
                filename.unlink()
            except:
                pass
        
        try:
            self.target_path.rmdir()
        except:
            pass
        
        print(f"{Fore.GREEN}[+] Cleanup complete")


class NetworkLatencySimulator:
    """Inject network latency using tc (traffic control)"""
    
    def __init__(self, interface: str = "eth0", delay_ms: int = 100, variance_ms: int = 20):
        self.interface = interface
        self.delay_ms = delay_ms
        self.variance_ms = variance_ms
    
    def start(self):
        """Add network latency"""
        print(f"{Fore.YELLOW}[*] Adding network latency")
        print(f"{Fore.YELLOW}    Interface: {self.interface}")
        print(f"{Fore.YELLOW}    Delay: {self.delay_ms}ms ± {self.variance_ms}ms\n")
        
        # Requires root
        if os.geteuid() != 0:
            print(f"{Fore.RED}[!] Requires root privileges")
            return
        
        try:
            # Add qdisc
            subprocess.run([
                'tc', 'qdisc', 'add', 'dev', self.interface,
                'root', 'netem',
                'delay', f'{self.delay_ms}ms', f'{self.variance_ms}ms'
            ], check=True)
            
            print(f"{Fore.GREEN}[+] Network latency added")
            print(f"{Fore.YELLOW}[!] Run cleanup() to remove")
        
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[!] Failed to add latency: {e}")
        except FileNotFoundError:
            print(f"{Fore.RED}[!] tc command not found. Install: apt install iproute2")
    
    def cleanup(self):
        """Remove network latency"""
        if os.geteuid() != 0:
            print(f"{Fore.RED}[!] Requires root privileges")
            return
        
        try:
            subprocess.run([
                'tc', 'qdisc', 'del', 'dev', self.interface, 'root'
            ], check=True)
            
            print(f"{Fore.GREEN}[+] Network latency removed")
        
        except subprocess.CalledProcessError:
            print(f"{Fore.YELLOW}[!] No latency to remove")


class DatabaseCorruptionSimulator:
    """Simulate KDC database issues"""
    
    def __init__(self, kdc_db_path: str = "/var/kerberos/krb5kdc/principal"):
        self.kdc_db_path = Path(kdc_db_path)
        self.backup_path = None
    
    def corrupt_lightly(self):
        """Add delays to database operations (simulates lock contention)"""
        print(f"{Fore.YELLOW}[*] Simulating database lock contention")
        print(f"{Fore.YELLOW}    This adds artificial delays to DB operations\n")
        
        # Would need to patch KDC or use LD_PRELOAD tricks
        # For safety, just document what would happen
        
        print(f"{Fore.CYAN}[INFO] In production, this would:")
        print(f"{Fore.CYAN}  • Slow down authentication")
        print(f"{Fore.CYAN}  • Increase response times")
        print(f"{Fore.CYAN}  • Cause timeouts under load")
        print(f"{Fore.CYAN}  • Trigger 'database busy' errors\n")
        
        print(f"{Fore.YELLOW}[SIMULATION] Creating artificial load instead...")
        
        # Alternative: Create many concurrent DB accesses
        self._concurrent_db_access(num_requests=50)
    
    def _concurrent_db_access(self, num_requests: int):
        """Simulate concurrent database access"""
        
        def make_request():
            # Attempt authentication (will hit database)
            subprocess.run(
                ['kinit', '-n', 'testuser@LAB.LOCAL'],
                capture_output=True,
                timeout=10
            )
        
        threads = []
        for i in range(num_requests):
            t = threading.Thread(target=make_request, daemon=True)
            t.start()
            threads.append(t)
            time.sleep(0.1)  # Stagger slightly
        
        print(f"{Fore.CYAN}[*] Sent {num_requests} concurrent requests")
        
        for t in threads:
            t.join(timeout=15)
        
        print(f"{Fore.GREEN}[+] Database stress test complete")


class ConnectionExhaustionSimulator:
    """Exhaust KDC connection pool"""
    
    def __init__(self, kdc_host: str = "localhost", kdc_port: int = 88, max_conns: int = 500):
        self.kdc_host = kdc_host
        self.kdc_port = kdc_port
        self.max_conns = max_conns
        self.sockets = []
    
    def start(self):
        """Open many connections to KDC"""
        print(f"{Fore.YELLOW}[*] Starting connection exhaustion")
        print(f"{Fore.YELLOW}    Target: {self.kdc_host}:{self.kdc_port}")
        print(f"{Fore.YELLOW}    Connections: {self.max_conns}\n")
        
        import socket
        
        successful = 0
        failed = 0
        
        try:
            for i in range(self.max_conns):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    sock.connect((self.kdc_host, self.kdc_port))
                    self.sockets.append(sock)
                    successful += 1
                    
                    if (i + 1) % 50 == 0:
                        print(f"{Fore.CYAN}[*] Connections: {successful}", end='\r')
                
                except Exception as e:
                    failed += 1
                    if failed > 50:  # Too many failures
                        break
                
                time.sleep(0.01)  # Slight delay
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Interrupted")
        
        print(f"\n{Fore.GREEN}[+] Opened {successful} connections")
        print(f"{Fore.YELLOW}[!] Run cleanup() to close connections")
    
    def cleanup(self):
        """Close all connections"""
        print(f"{Fore.YELLOW}[*] Closing connections...")
        
        for sock in self.sockets:
            try:
                sock.close()
            except:
                pass
        
        self.sockets.clear()
        print(f"{Fore.GREEN}[+] All connections closed")


class ClockSkewSimulator:
    """Simulate clock skew issues"""
    
    def __init__(self, skew_minutes: int = 10):
        self.skew_minutes = skew_minutes
        self.original_time = None
    
    def start(self):
        """Change system time"""
        if os.geteuid() != 0:
            print(f"{Fore.RED}[!] Requires root privileges")
            return
        
        print(f"{Fore.YELLOW}[*] Simulating clock skew")
        print(f"{Fore.YELLOW}    Skew: {self.skew_minutes} minutes\n")
        
        # Save original time
        self.original_time = datetime.now()
        
        # Calculate new time
        new_time = self.original_time + timedelta(minutes=self.skew_minutes)
        
        # Set system time
        try:
            subprocess.run([
                'date', '-s', new_time.strftime('%Y-%m-%d %H:%M:%S')
            ], check=True)
            
            print(f"{Fore.GREEN}[+] Clock skewed by {self.skew_minutes} minutes")
            print(f"{Fore.GREEN}    Old time: {self.original_time}")
            print(f"{Fore.GREEN}    New time: {new_time}")
            print(f"{Fore.YELLOW}[!] Run cleanup() to restore time")
        
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[!] Failed to set time: {e}")
    
    def cleanup(self):
        """Restore original time"""
        if os.geteuid() != 0:
            print(f"{Fore.RED}[!] Requires root privileges")
            return
        
        if not self.original_time:
            print(f"{Fore.YELLOW}[!] No original time saved")
            return
        
        try:
            subprocess.run([
                'date', '-s', self.original_time.strftime('%Y-%m-%d %H:%M:%S')
            ], check=True)
            
            print(f"{Fore.GREEN}[+] Time restored to {self.original_time}")
        
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[!] Failed to restore time: {e}")


class ResponseDegradationSimulator:
    """Simulate gradual KDC response degradation"""
    
    def __init__(self, kdc_host: str = "localhost"):
        self.kdc_host = kdc_host
        self.running = False
        self.thread = None
    
    def start(self, duration: int = 300):
        """Start gradual degradation over time"""
        print(f"{Fore.YELLOW}[*] Starting response degradation simulation")
        print(f"{Fore.YELLOW}    Duration: {duration}s")
        print(f"{Fore.YELLOW}    Pattern: Gradually increasing delays\n")
        
        self.running = True
        self.thread = threading.Thread(
            target=self._gradual_degradation,
            args=(duration,),
            daemon=True
        )
        self.thread.start()
        
        try:
            self.thread.join()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[*] Interrupted")
            self.stop()
    
    def _gradual_degradation(self, duration: int):
        """Gradually increase load on KDC"""
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < duration:
            elapsed = time.time() - start_time
            progress = elapsed / duration
            
            # Increase request rate over time
            requests_per_sec = int(1 + progress * 20)  # 1 -> 21 req/sec
            
            # Send burst of requests
            for _ in range(requests_per_sec):
                if not self.running:
                    break
                
                threading.Thread(
                    target=self._send_request,
                    daemon=True
                ).start()
            
            print(f"{Fore.CYAN}[*] Load: {requests_per_sec} req/s | Progress: {progress*100:.1f}%", end='\r')
            time.sleep(1)
        
        print(f"\n{Fore.GREEN}[+] Degradation simulation complete")
    
    def _send_request(self):
        """Send single authentication request"""
        try:
            subprocess.run(
                ['kinit', '-n', f'user{random.randint(1,100)}@LAB.LOCAL'],
                capture_output=True,
                timeout=5
            )
        except:
            pass
    
    def stop(self):
        """Stop degradation"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)


class ChaosOrchestrator:
    """Run chaos scenarios"""
    
    SCENARIOS = {
        'memory_leak': {
            'name': 'Memory Leak',
            'description': 'Gradually allocate memory to simulate leak',
            'simulator': MemoryLeakSimulator
        },
        'cpu_exhaustion': {
            'name': 'CPU Exhaustion',
            'description': 'Max out CPU cores',
            'simulator': CPUExhaustionSimulator
        },
        'disk_fill': {
            'name': 'Disk Space Fill',
            'description': 'Fill disk space gradually',
            'simulator': DiskSpaceSimulator
        },
        'network_latency': {
            'name': 'Network Latency',
            'description': 'Add network delays',
            'simulator': NetworkLatencySimulator
        },
        'db_contention': {
            'name': 'Database Contention',
            'description': 'Simulate database lock issues',
            'simulator': DatabaseCorruptionSimulator
        },
        'connection_exhaustion': {
            'name': 'Connection Exhaustion',
            'description': 'Exhaust connection pool',
            'simulator': ConnectionExhaustionSimulator
        },
        'clock_skew': {
            'name': 'Clock Skew',
            'description': 'Introduce time synchronization issues',
            'simulator': ClockSkewSimulator
        },
        'degradation': {
            'name': 'Gradual Degradation',
            'description': 'Slowly increase load over time',
            'simulator': ResponseDegradationSimulator
        }
    }
    
    @classmethod
    def list_scenarios(cls):
        """List available scenarios"""
        print(f"\n{Fore.CYAN}Available Chaos Scenarios:")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        for key, scenario in cls.SCENARIOS.items():
            print(f"{Fore.GREEN}{key}")
            print(f"  {scenario['description']}\n")
    
    @classmethod
    def run_scenario(cls, scenario_name: str, **kwargs):
        """Run a chaos scenario"""
        if scenario_name not in cls.SCENARIOS:
            print(f"{Fore.RED}[!] Unknown scenario: {scenario_name}")
            cls.list_scenarios()
            return
        
        scenario = cls.SCENARIOS[scenario_name]
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Chaos Scenario: {scenario['name']}")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        simulator = scenario['simulator'](**kwargs)
        simulator.start()
        
        if hasattr(simulator, 'cleanup'):
            print(f"\n{Fore.YELLOW}[*] Running cleanup...")
            simulator.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description=f"Kerberos Chaos Engineering Toolkit v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Scenarios:
  memory_leak          - Gradually consume memory
  cpu_exhaustion       - Max out CPU cores
  disk_fill            - Fill disk space
  network_latency      - Add network delays (requires root)
  db_contention        - Simulate database issues
  connection_exhaustion - Exhaust connection pool
  clock_skew           - Introduce time sync issues (requires root)
  degradation          - Gradual performance degradation

Examples:
  # List scenarios
  python3 kerberos_chaos_toolkit.py --list
  
  # Memory leak (1024 MB)
  python3 kerberos_chaos_toolkit.py memory_leak --max-mb 1024
  
  # CPU exhaustion (4 cores, 90% intensity, 60 seconds)
  python3 kerberos_chaos_toolkit.py cpu_exhaustion --threads 4 --duration 60
  
  # Network latency (100ms delay)
  sudo python3 kerberos_chaos_toolkit.py network_latency --delay-ms 100
  
  # Connection exhaustion
  python3 kerberos_chaos_toolkit.py connection_exhaustion --max-conns 500

⚠️  USE ONLY IN LAB ENVIRONMENTS!
        """
    )
    
    parser.add_argument('scenario', nargs='?', help='Chaos scenario to run')
    parser.add_argument('--list', action='store_true', help='List available scenarios')
    
    # Memory leak options
    parser.add_argument('--rate-mb', type=float, default=10.0, help='Memory leak rate (MB/s)')
    parser.add_argument('--max-mb', type=int, default=1024, help='Maximum memory to allocate (MB)')
    
    # CPU options
    parser.add_argument('--threads', type=int, default=4, help='Number of CPU threads')
    parser.add_argument('--intensity', type=float, default=0.9, help='CPU intensity (0.0-1.0)')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')
    
    # Disk options
    parser.add_argument('--fill-mb', type=int, default=1024, help='Disk space to fill (MB)')
    
    # Network options
    parser.add_argument('--delay-ms', type=int, default=100, help='Network delay (ms)')
    parser.add_argument('--interface', default='eth0', help='Network interface')
    
    # Connection options
    parser.add_argument('--max-conns', type=int, default=500, help='Maximum connections')
    parser.add_argument('--kdc-host', default='localhost', help='KDC hostname')
    
    # Clock options
    parser.add_argument('--skew-minutes', type=int, default=10, help='Clock skew (minutes)')
    
    args = parser.parse_args()
    
    # Safety check
    SafetyCheck.confirm_lab_environment()
    
    # List scenarios
    if args.list or not args.scenario:
        ChaosOrchestrator.list_scenarios()
        return
    
    # Prepare kwargs based on scenario
    kwargs = {}
    
    if args.scenario == 'memory_leak':
        kwargs = {'rate_mb_per_sec': args.rate_mb, 'max_mb': args.max_mb}
    elif args.scenario == 'cpu_exhaustion':
        kwargs = {'num_threads': args.threads, 'intensity': args.intensity}
        ChaosOrchestrator.run_scenario(args.scenario, **kwargs)
        # Special case: pass duration separately
        simulator = CPUExhaustionSimulator(**kwargs)
        simulator.start(args.duration)
        return
    elif args.scenario == 'disk_fill':
        kwargs = {'fill_mb': args.fill_mb}
    elif args.scenario == 'network_latency':
        kwargs = {'interface': args.interface, 'delay_ms': args.delay_ms}
    elif args.scenario == 'connection_exhaustion':
        kwargs = {'kdc_host': args.kdc_host, 'max_conns': args.max_conns}
    elif args.scenario == 'clock_skew':
        kwargs = {'skew_minutes': args.skew_minutes}
    elif args.scenario == 'degradation':
        kwargs = {'kdc_host': args.kdc_host}
        ChaosOrchestrator.run_scenario(args.scenario, **kwargs)
        simulator = ResponseDegradationSimulator(**kwargs)
        simulator.start(args.duration)
        return
    
    # Run scenario
    ChaosOrchestrator.run_scenario(args.scenario, **kwargs)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
