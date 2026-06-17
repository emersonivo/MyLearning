#!/usr/bin/env python3
"""
KVM Security Scanner — Automated security audit for KVM/QEMU environments.
Scans all running domains for security misconfigurations via libvirt API.

Usage:
  python3 vm_scanner.py
  python3 vm_scanner.py --output-dir /tmp/scan_results
"""

import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

try:
    import libvirt
except ImportError:
    print("[!] Install libvirt-python: pip install libvirt-python")
    import sys; sys.exit(1)

class KVMSecurityScanner:
    def __init__(self, output_dir="scan_results"):
        self.conn = libvirt.open('qemu:///system')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = {'scan_time': datetime.now().isoformat(), 'domains': []}

    def get_domain_state(self, domain) -> str:
        states = {0: 'nostate', 1: 'running', 2: 'blocked', 3: 'paused',
                  4: 'shutdown', 5: 'shutoff', 6: 'crashed', 7: 'pmsuspended'}
        state, _ = domain.state()
        return states.get(state, 'unknown')

    def check_isolation(self, domain) -> dict:
        """Check SELinux/AppArmor isolation for domain."""
        result = {'status': 'unknown', 'issues': []}
        try:
            xml = domain.XMLDesc()
            if 'seclabel' not in xml:
                result['issues'].append('No security label configured')
                result['status'] = 'warning'
            else:
                result['status'] = 'ok'
        except Exception as e:
            result['issues'].append(str(e))
            result['status'] = 'error'
        return result

    def check_network_config(self, domain) -> dict:
        """Check network isolation configuration."""
        result = {'status': 'ok', 'networks': [], 'issues': []}
        try:
            xml = domain.XMLDesc()
            # Check for isolated networks (no NAT to host)
            if "network source='default'" in xml:
                result['issues'].append('VM connected to default (non-isolated) network')
                result['status'] = 'warning'
        except Exception as e:
            result['issues'].append(str(e))
            result['status'] = 'error'
        return result

    def check_disk_encryption(self, domain) -> dict:
        """Check if VM disks have encryption configured."""
        result = {'status': 'unknown', 'disks': [], 'issues': []}
        try:
            xml = domain.XMLDesc()
            if 'encryption' not in xml:
                result['issues'].append('No disk encryption configured')
                result['status'] = 'warning'
            else:
                result['status'] = 'ok'
        except Exception as e:
            result['issues'].append(str(e))
            result['status'] = 'error'
        return result

    def check_cpu_pinning(self, domain) -> dict:
        """Check CPU pinning for isolation."""
        result = {'status': 'unknown', 'issues': []}
        try:
            xml = domain.XMLDesc()
            if 'vcpupin' not in xml:
                result['issues'].append('No CPU pinning configured (timing attack risk)')
                result['status'] = 'info'
            else:
                result['status'] = 'ok'
        except Exception as e:
            result['issues'].append(str(e))
        return result

    def run_security_checks(self, domain) -> dict:
        return {
            'isolation': self.check_isolation(domain),
            'network': self.check_network_config(domain),
            'disk_encryption': self.check_disk_encryption(domain),
            'cpu_pinning': self.check_cpu_pinning(domain),
        }

    def scan_all_domains(self) -> dict:
        domains = self.conn.listAllDomains()
        print(f"[*] Scanning {len(domains)} domains...")
        for domain in domains:
            name = domain.name()
            print(f"  [*] {name}...")
            domain_info = {
                'name': name,
                'state': self.get_domain_state(domain),
                'security_checks': self.run_security_checks(domain),
            }
            # Count issues
            issues = sum(len(c.get('issues', [])) for c in domain_info['security_checks'].values())
            domain_info['total_issues'] = issues
            self.results['domains'].append(domain_info)
            status = 'WARN' if issues > 0 else 'OK'
            print(f"    [{status}] {issues} issue(s)")
        return self.results

    def save_results(self) -> Path:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        out_file = self.output_dir / f"scan_{ts}.json"
        out_file.write_text(json.dumps(self.results, indent=2))
        print(f"[+] Results saved: {out_file}")
        return out_file

    def run(self):
        print(f"\n{'='*50}")
        print("KVM Security Scanner")
        print(f"{'='*50}\n")
        results = self.scan_all_domains()
        total_issues = sum(d['total_issues'] for d in results['domains'])
        print(f"\n[+] Scan complete: {len(results['domains'])} VMs, {total_issues} total issues")
        return self.save_results()

def main():
    parser = argparse.ArgumentParser(description="KVM Security Scanner")
    parser.add_argument('--output-dir', default='scan_results')
    args = parser.parse_args()
    scanner = KVMSecurityScanner(args.output_dir)
    scanner.run()

if __name__ == "__main__":
    main()
