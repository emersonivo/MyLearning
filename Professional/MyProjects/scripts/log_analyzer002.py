#!/usr/bin/env python3
"""
AI Log Analyzer - Enhanced with synthetic log testing
"""

import json
from pathlib import Path
from log_analyzer import AILogAnalyzer

def analyze_generated_logs(log_file: str, markers_file: str):
    """
    Analyze generated logs and compare against ground truth
    """
    analyzer = AILogAnalyzer()
    
    # Load logs
    with open(log_file, 'r') as f:
        logs = f.read()
    
    # Load ground truth
    with open(markers_file, 'r') as f:
        ground_truth = json.load(f)
    
    print("Analyzing logs with AI...")
    analysis = analyzer.analyze_logs(logs)
    
    print("\n" + "="*80)
    print("AI ANALYSIS RESULTS")
    print("="*80)
    print(analysis)
    
    print("\n" + "="*80)
    print("GROUND TRUTH (What was actually injected)")
    print("="*80)
    for marker in ground_truth['anomaly_markers']:
        print(f"\n{marker['type']}:")
        print(f"  Time: {marker['start_time']}")
        print(f"  Severity: {marker['severity']}")
        print(f"  Details: {marker}")
    
    # TODO: Compare AI findings vs ground truth
    # Calculate precision/recall metrics

if __name__ == "__main__":
    # Find latest generated logs
    log_dir = Path("generated_logs")
    log_files = sorted(log_dir.glob("security_logs_*.log"))
    marker_files = sorted(log_dir.glob("anomaly_markers_*.json"))
    
    if log_files and marker_files:
        analyze_generated_logs(str(log_files[-1]), str(marker_files[-1]))
    else:
        print("No generated logs found. Run log_generator.py first!")