#!/usr/bin/env python3
"""
Quick test script for log generator
"""

from log_generator import LogGenerator, LogConfig, AnomalyType
from datetime import datetime, timedelta

def test_basic_generation():
    """Test basic log generation"""
    config = LogConfig(
        start_time=datetime.now() - timedelta(hours=2),
        end_time=datetime.now()
    )
    
    generator = LogGenerator(config)
    
    # Generate 2 hours of logs with anomalies
    logs_data = generator.generate_logs_with_anomalies(
        hours=2,
        anomaly_types=[AnomalyType.BRUTE_FORCE, AnomalyType.PRIVILEGE_ESCALATION],
        anomaly_probability=0.5  # 50% chance per hour
    )
    
    print(f"Generated {len(logs_data['logs'])} log entries")
    print(f"Injected {len(logs_data['anomaly_markers'])} anomalies")
    
    # Print first 10 logs
    print("\nFirst 10 log entries:")
    for log in logs_data['logs'][:10]:
        print(log)
    
    # Print anomaly markers
    print("\nAnomaly markers:")
    for marker in logs_data['anomaly_markers']:
        print(f"- {marker['type']} at {marker['start_time']} (Severity: {marker['severity']})")
    
    # Save
    generator.save_logs(logs_data, output_dir="test_logs")

if __name__ == "__main__":
    test_basic_generation()