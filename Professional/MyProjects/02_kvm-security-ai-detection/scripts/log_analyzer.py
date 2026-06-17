#!/usr/bin/env python3
"""
AI-Powered Log Analyzer for KVM Security Events.
Uses Claude API for intelligent log analysis and anomaly detection.

Usage:
  export ANTHROPIC_API_KEY="sk-..."
  python3 log_analyzer.py --log-file /var/log/auth.log
  python3 log_analyzer.py --vm web-server-01
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("[!] Install anthropic: pip install anthropic")
    import sys; sys.exit(1)

class AILogAnalyzer:
    def __init__(self, api_key=None):
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get('ANTHROPIC_API_KEY'))

    def analyze_logs(self, log_content: str, context="KVM security") -> dict:
        """Analyze logs using Claude API."""
        prompt = f"""Analyze these {context} logs for security issues:

{log_content[:4000]}

Provide JSON response with:
{{
  "critical_findings": [],
  "risk_level": "HIGH|MEDIUM|LOW",
  "recommended_actions": [],
  "false_positive_likelihood": "HIGH|MEDIUM|LOW",
  "summary": ""
}}"""
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=1000,
            messages=[{"role": "user", "content": prompt}])
        try:
            return json.loads(message.content[0].text)
        except json.JSONDecodeError:
            return {"raw_response": message.content[0].text}

    def detect_anomalies(self, recent_logs: str, baseline_logs: str) -> dict:
        """Compare recent behavior against baseline."""
        prompt = f"""Compare these log patterns and identify anomalies:

BASELINE (normal behavior):
{baseline_logs[:2000]}

RECENT ACTIVITY:
{recent_logs[:2000]}

Respond in JSON with: unusual_patterns, potential_incidents, performance_anomalies, recommended_investigations"""
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=1000,
            messages=[{"role": "user", "content": prompt}])
        try:
            return json.loads(message.content[0].text)
        except json.JSONDecodeError:
            return {"raw_response": message.content[0].text}

    def analyze_file(self, log_file: str) -> dict:
        print(f"[*] Analyzing {log_file}...")
        content = Path(log_file).read_text(errors='ignore')
        result = self.analyze_logs(content, context=f"file {log_file}")
        print(f"[+] Risk level: {result.get('risk_level', 'UNKNOWN')}")
        return result

def main():
    parser = argparse.ArgumentParser(description="AI-Powered Log Analyzer")
    parser.add_argument('--log-file', help='Log file to analyze')
    parser.add_argument('--output-dir', default='analysis_results')
    args = parser.parse_args()

    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("[!] Set ANTHROPIC_API_KEY environment variable")
        return

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    analyzer = AILogAnalyzer()

    if args.log_file:
        result = analyzer.analyze_file(args.log_file)
    else:
        # Demo with sample data
        sample_logs = """Jun  1 10:23:45 web-server sshd[1234]: Failed password for root from 10.0.0.1
Jun  1 10:23:46 web-server sshd[1234]: Failed password for root from 10.0.0.1
Jun  1 10:23:47 web-server sshd[1234]: Failed password for root from 10.0.0.1
Jun  1 10:23:48 web-server sshd[1234]: Accepted password for admin from 192.168.1.50"""
        result = analyzer.analyze_logs(sample_logs)

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_file = output_dir / f"analysis_{ts}.json"
    out_file.write_text(json.dumps(result, indent=2))
    print(f"[+] Saved: {out_file}")

if __name__ == "__main__":
    main()
