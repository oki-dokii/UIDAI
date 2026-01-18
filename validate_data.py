#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - Data Validation Script
Checks data quality and consistency across all three datasets.

Key check: Validates that updates don't exceed enrolments baseline.
"""

import os
import glob
import pandas as pd
from datetime import datetime


def count_rows_per_dataset():
    """Count rows in each dataset."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    datasets = {
        'biometric': os.path.join(base_dir, 'api_data_aadhar_biometric'),
        'demographic': os.path.join(base_dir, 'api_data_aadhar_demographic'),
        'enrolment': os.path.join(base_dir, 'api_data_aadhar_enrolment'),
    }
    
    row_counts = {}
    for name, path in datasets.items():
        files = glob.glob(os.path.join(path, '*.csv'))
        total = 0
        for f in files:
            with open(f, 'r') as fp:
                total += sum(1 for _ in fp) - 1  # Subtract header
        row_counts[name] = total
    
    return row_counts


def check_date_ranges():
    """Check date ranges for each dataset."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    datasets = {
        'biometric': os.path.join(base_dir, 'api_data_aadhar_biometric'),
        'demographic': os.path.join(base_dir, 'api_data_aadhar_demographic'),
        'enrolment': os.path.join(base_dir, 'api_data_aadhar_enrolment'),
    }
    
    date_ranges = {}
    for name, path in datasets.items():
        files = glob.glob(os.path.join(path, '*.csv'))
        all_dates = []
        for f in files:
            try:
                df = pd.read_csv(f, usecols=['date'])
                df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
                all_dates.extend(df['date'].dropna().tolist())
            except:
                pass
        
        if all_dates:
            date_ranges[name] = {
                'min': min(all_dates),
                'max': max(all_dates),
                'days': (max(all_dates) - min(all_dates)).days
            }
        else:
            date_ranges[name] = None
    
    return date_ranges


def check_value_scale():
    """Check sum of values in each dataset."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    datasets = {
        'biometric': (
            os.path.join(base_dir, 'api_data_aadhar_biometric'),
            ['bio_age_5_17', 'bio_age_17_']
        ),
        'demographic': (
            os.path.join(base_dir, 'api_data_aadhar_demographic'),
            ['demo_age_5_17', 'demo_age_17_']
        ),
        'enrolment': (
            os.path.join(base_dir, 'api_data_aadhar_enrolment'),
            ['age_0_5', 'age_5_17', 'age_18_greater']
        ),
    }
    
    totals = {}
    for name, (path, cols) in datasets.items():
        files = glob.glob(os.path.join(path, '*.csv'))
        total = 0
        for f in files:
            try:
                df = pd.read_csv(f, usecols=cols)
                total += df[cols].sum().sum()
            except:
                pass
        totals[name] = int(total)
    
    return totals


def validate_data():
    """Run all validation checks and print report."""
    print("=" * 70)
    print("UIDAI DATA VALIDATION REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Row counts
    print("📊 ROW COUNTS")
    print("-" * 40)
    rows = count_rows_per_dataset()
    for name, count in sorted(rows.items(), key=lambda x: -x[1]):
        print(f"  {name:15}: {count:>12,} rows")
    print()
    
    # Check for imbalance
    max_rows = max(rows.values())
    min_rows = min(rows.values())
    ratio = max_rows / min_rows if min_rows > 0 else float('inf')
    
    if ratio > 1.5:
        print(f"  ⚠️ WARNING: Row count imbalance detected!")
        print(f"     Ratio of largest to smallest: {ratio:.2f}x")
        print(f"     This may indicate incomplete data collection.")
    print()
    
    # Date ranges
    print("📅 DATE RANGES")
    print("-" * 40)
    dates = check_date_ranges()
    for name, info in dates.items():
        if info:
            print(f"  {name:15}: {info['min'].date()} to {info['max'].date()} ({info['days']} days)")
        else:
            print(f"  {name:15}: No valid dates found")
    print()
    
    # Value totals
    print("💰 TOTAL VALUES (Sum of all numeric columns)")
    print("-" * 40)
    totals = check_value_scale()
    for name, total in sorted(totals.items(), key=lambda x: -x[1]):
        print(f"  {name:15}: {total:>15,}")
    print()
    
    # Check for scale inversion
    enrol_total = totals.get('enrolment', 0)
    bio_total = totals.get('biometric', 0)
    demo_total = totals.get('demographic', 0)
    update_total = bio_total + demo_total
    
    print("🔍 SCALE CHECK")
    print("-" * 40)
    print(f"  Total Enrolments: {enrol_total:,}")
    print(f"  Total Updates: {update_total:,}")
    
    if update_total > enrol_total:
        ratio = update_total / enrol_total if enrol_total > 0 else float('inf')
        print()
        print(f"  ⚠️ CRITICAL: Updates ({update_total:,}) > Enrolments ({enrol_total:,})")
        print(f"     Update-to-Enrolment Ratio: {ratio:.1f}x")
        print()
        print("  POSSIBLE CAUSES:")
        print("    1. Enrolment data is incomplete/sampled")
        print("    2. Enrolment data covers shorter date range")
        print("    3. Updates include historical Aadhaar holders not in this enrolment data")
        print("    4. Data collection methodology differs between sources")
        print()
        print("  RECOMMENDATION:")
        print("    - Document this limitation in analysis conclusions")
        print("    - Focus on relative patterns rather than absolute ratios")
        print("    - Request complete enrolment data if available")
    else:
        ratio = enrol_total / update_total if update_total > 0 else float('inf')
        print(f"  ✅ Scale is reasonable (Enrolment:Update ratio = {ratio:.1f}:1)")
    
    print()
    print("=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)
    
    return {
        'rows': rows,
        'dates': dates,
        'totals': totals,
        'has_scale_issue': update_total > enrol_total
    }


if __name__ == '__main__':
    validate_data()
