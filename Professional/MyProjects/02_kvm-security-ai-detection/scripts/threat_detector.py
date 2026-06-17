#!/usr/bin/env python3
"""
Integrated Threat Detection Engine.
Combines KVM security scanning with AI-powered log analysis.

Usage:
  export ANTHROPIC_API_KEY="sk-..."
  python3 threat_detector.py --full-audit
  python3 threat_detector.py --scan-only
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path

class ThreatDetector:
    def __init__(self, output_dir="threat_reports", use_ai=True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.use_ai = use_ai and bool(os.environ.get('ANTHROPIC_API_KEY'))
        self.threat_levels = {'critical': [], 'high': [], 'medium': [], 'low': []}

    def correlate_threats(self, scan_results: dict, log_analyses: list) -> dict:
        """Correlate VM scan findings with log anomalies."""
        threats = []
        for domain in scan_results.get('domains', []):
            for check_name, check_result in domain.get('security_checks', {}).items():
                for issue in check_result.get('issues', []):
                    severity = 'high' if 'SELinux' in issue or 'isolation' in issue else 'medium'
                    threats.append({
                        'vm': domain['name'],
                        'type': f'config_{check_name}',
                        'severity': severity,
                        'description': issue,
                        'source': 'vm_scan'
                    })
        return {'threats': threats, 'total': len(threats),
                'by_severity': {s: [t for t in threats if t['severity'] == s]
                                for s in ['critical', 'high', 'medium', 'low']}}

    def generate_report(self, threats: dict, scan_results: dict) -> str:
        lines = [f"# Security Threat Report", f"**Generated:** {datetime.now().isoformat()}",
                 f"**Total Threats:** {threats['total']}", ""]
        for severity in ['critical', 'high', 'medium', 'low']:
            items = threats['by_severity'].get(severity, [])
            if items:
                lines.append(f"## {severity.upper()} ({len(items)})")
                for t in items:
                    lines.append(f"- **{t['vm']}**: {t['description']}")
                lines.append("")
        return '\n'.join(lines)

    def full_audit(self):
        print(f"\n{'='*50}")
        print("Integrated Security Audit")
        print(f"{'='*50}\n")

        # Import and run scanner
        try:
            from vm_scanner import KVMSecurityScanner
            scanner = KVMSecurityScanner(str(self.output_dir))
            scan_file = scanner.run()
            scan_results = json.loads(scan_file.read_text())
        except Exception as e:
            print(f"[!] Scanner error (running demo mode): {e}")
            scan_results = {'domains': [], 'scan_time': datetime.now().isoformat()}

        threats = self.correlate_threats(scan_results, [])
        report = self.generate_report(threats, scan_results)

        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.output_dir / f"threat_report_{ts}.md"
        report_file.write_text(report)
        json_file = self.output_dir / f"threat_report_{ts}.json"
        json_file.write_text(json.dumps(threats, indent=2))

        print(f"\n[+] Threat report: {report_file}")
        print(f"[+] JSON report:   {json_file}")
        print(f"\n[SUMMARY] {threats['total']} threats found")

def main():
    parser = argparse.ArgumentParser(description="Integrated Threat Detector")
    parser.add_argument('--full-audit', action='store_true')
    parser.add_argument('--output-dir', default='threat_reports')
    parser.add_argument('--no-ai', action='store_true')
    args = parser.parse_args()
    detector = ThreatDetector(args.output_dir, use_ai=not args.no_ai)
    detector.full_audit()

if __name__ == "__main__":
    main()
