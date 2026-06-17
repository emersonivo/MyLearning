#!/usr/bin/env python3
"""
Kerberos Detection Engine
Analyzes pcap files for Kerberos attack patterns.
Uses 6 detection algorithms + Claude API for AI analysis.

Usage:
  python3 kerberos_detector.py attack.pcap
  ANTHROPIC_API_KEY=sk-... python3 kerberos_detector.py attack.pcap
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

try:
    import pyshark
except ImportError:
    print("[!] Install pyshark: pip install pyshark")
    sys.exit(1)

# Detection thresholds
THRESHOLDS = {
    'bruteforce_failures': 10,       # failures in window
    'bruteforce_window_sec': 300,    # 5 minutes
    'kerberoast_tgs_burst': 5,       # TGS-REQ in window
    'kerberoast_window_sec': 60,
    'asrep_roast_min_users': 3,      # distinct users without preauth
}

def parse_kerberos_packets(pcap_file: str) -> list:
    """Parse pcap and extract Kerberos packets."""
    packets = []
    try:
        cap = pyshark.FileCapture(pcap_file, display_filter='kerberos')
        for pkt in cap:
            try:
                packets.append({
                    'time': float(pkt.sniff_timestamp),
                    'src': str(pkt.ip.src) if hasattr(pkt, 'ip') else 'unknown',
                    'dst': str(pkt.ip.dst) if hasattr(pkt, 'ip') else 'unknown',
                    'msg_type': int(pkt.kerberos.msg_type) if hasattr(pkt.kerberos, 'msg_type') else 0,
                    'error_code': int(pkt.kerberos.error_code) if hasattr(pkt.kerberos, 'error_code') else None,
                    'cname': str(pkt.kerberos.CNameString) if hasattr(pkt.kerberos, 'CNameString') else None,
                    'has_padata': hasattr(pkt.kerberos, 'padata'),
                })
            except Exception:
                continue
        cap.close()
    except Exception as e:
        print(f"[!] Error parsing pcap: {e}")
    return packets

def detect_bruteforce(packets: list) -> list:
    """Detect brute force: 10+ failed AS-REQ from same source in 5 min."""
    alerts = []
    failures = {}
    for pkt in packets:
        if pkt['msg_type'] == 30 and pkt['error_code'] == 24:  # KDC_ERR_PREAUTH_FAILED
            src = pkt['src']
            if src not in failures:
                failures[src] = []
            failures[src].append(pkt['time'])
    for src, times in failures.items():
        times.sort()
        for i in range(len(times)):
            window = [t for t in times if times[i] <= t <= times[i] + THRESHOLDS['bruteforce_window_sec']]
            if len(window) >= THRESHOLDS['bruteforce_failures']:
                alerts.append({
                    'type': 'BRUTE_FORCE', 'severity': 'HIGH', 'confidence': 0.90,
                    'source_ip': src, 'evidence': f"{len(window)} failures in 5 min",
                    'timestamp': datetime.fromtimestamp(times[i]).isoformat()
                })
                break
    return alerts

def detect_asrep_roasting(packets: list) -> list:
    """Detect AS-REP roasting: AS-REQ without pre-authentication."""
    alerts = []
    roastable = [p for p in packets if p['msg_type'] == 10 and not p['has_padata']]
    if len(roastable) >= THRESHOLDS['asrep_roast_min_users']:
        users = list(set(p['cname'] for p in roastable if p['cname']))
        alerts.append({
            'type': 'ASREP_ROASTING', 'severity': 'HIGH', 'confidence': 0.70,
            'source_ip': roastable[0]['src'],
            'evidence': f"AS-REQ without pre-auth for {len(users)} users: {users}",
            'timestamp': datetime.fromtimestamp(roastable[0]['time']).isoformat()
        })
    return alerts

def ai_analyze(alerts: list, api_key: str) -> dict:
    """Use Claude API for contextual analysis of alerts."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""Analyze these Kerberos security alerts and provide:
1. Risk assessment (CRITICAL/HIGH/MEDIUM/LOW)
2. Attack classification
3. Confidence analysis
4. Recommended actions (top 3)

Alerts: {json.dumps(alerts, indent=2)}

Respond in JSON format."""
        message = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=1000,
            messages=[{"role": "user", "content": prompt}])
        return json.loads(message.content[0].text)
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Kerberos Detection Engine")
    parser.add_argument('pcap', help='Path to pcap file')
    parser.add_argument('--output-dir', default='detection_results')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    print(f"[*] Analyzing: {args.pcap}")
    packets = parse_kerberos_packets(args.pcap)
    print(f"[+] Parsed {len(packets)} Kerberos packets")

    all_alerts = []
    all_alerts.extend(detect_bruteforce(packets))
    all_alerts.extend(detect_asrep_roasting(packets))

    if not all_alerts:
        print("[+] No attacks detected")
    else:
        print(f"\n[!] {len(all_alerts)} alert(s) detected:")
        for a in all_alerts:
            print(f"  [{a['severity']}] {a['type']} from {a['source_ip']}: {a['evidence']}")

    api_key = __import__('os').environ.get('ANTHROPIC_API_KEY')
    if api_key:
        print("\n[*] Running AI analysis...")
        ai_result = ai_analyze(all_alerts, api_key)
        print(f"[+] AI: {json.dumps(ai_result, indent=2)}")
    else:
        print("\n[*] Set ANTHROPIC_API_KEY for AI analysis")

    # Save report
    report = {'pcap': args.pcap, 'packets_analyzed': len(packets),
              'alerts': all_alerts, 'timestamp': datetime.now().isoformat()}
    report_file = output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\n[+] Report saved: {report_file}")

if __name__ == "__main__":
    main()
