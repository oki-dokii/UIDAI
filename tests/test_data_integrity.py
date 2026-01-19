#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - DATA INTEGRITY TESTS
Validates raw data files and consistency across datasets

Author: UIDAI Hackathon Team
"""

import os
import pandas as pd
import numpy as np
import unittest
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestBiometricDataIntegrity(unittest.TestCase):
    """Test biometric data integrity."""
    
    @classmethod
    def setUpClass(cls):
        """Load biometric data once."""
        import glob
        data_dir = os.path.join(BASE_DIR, "data", "api_data_aadhar_biometric")
        files = glob.glob(os.path.join(data_dir, "*.csv"))
        dfs = [pd.read_csv(f) for f in files]
        cls.df = pd.concat(dfs, ignore_index=True)
        print(f"\n  Loaded {len(cls.df):,} biometric records")
    
    def test_no_null_dates(self):
        """Check for null dates."""
        null_count = self.df['date'].isna().sum()
        self.assertEqual(null_count, 0, f"Found {null_count} null dates")
        print(f"  ✓ No null dates")
    
    def test_date_format_valid(self):
        """Check date format is DD-MM-YYYY."""
        sample = self.df['date'].head(100)
        for date in sample:
            try:
                datetime.strptime(str(date), '%d-%m-%Y')
            except ValueError:
                self.fail(f"Invalid date format: {date}")
        print(f"  ✓ Date format valid (DD-MM-YYYY)")
    
    def test_no_negative_counts(self):
        """Check no negative counts."""
        for col in ['bio_age_5_17', 'bio_age_17_']:
            neg_count = (self.df[col] < 0).sum()
            self.assertEqual(neg_count, 0, f"Found {neg_count} negative values in {col}")
        print(f"  ✓ No negative counts")
    
    def test_pincode_valid(self):
        """Check pincode is 6 digits."""
        valid = self.df['pincode'].astype(str).str.match(r'^\d{6}$', na=False)
        invalid_count = (~valid).sum()
        self.assertLess(invalid_count / len(self.df), 0.01, f"Too many invalid pincodes: {invalid_count}")
        print(f"  ✓ Pincodes valid (< 1% invalid)")
    
    def test_states_not_empty(self):
        """Check state column not empty."""
        empty = self.df['state'].isna() | (self.df['state'] == '')
        self.assertEqual(empty.sum(), 0, "Found empty state values")
        print(f"  ✓ No empty states")
    
    def test_reasonable_counts(self):
        """Check counts are reasonable (< 10M per record)."""
        max_bio = self.df[['bio_age_5_17', 'bio_age_17_']].max().max()
        self.assertLess(max_bio, 10_000_000, f"Unreasonably high count: {max_bio}")
        print(f"  ✓ Counts within reasonable range (max: {max_bio:,})")


class TestDemographicDataIntegrity(unittest.TestCase):
    """Test demographic data integrity."""
    
    @classmethod
    def setUpClass(cls):
        """Load demographic data once."""
        import glob
        data_dir = os.path.join(BASE_DIR, "data", "api_data_aadhar_demographic")
        files = glob.glob(os.path.join(data_dir, "*.csv"))
        dfs = [pd.read_csv(f) for f in files]
        cls.df = pd.concat(dfs, ignore_index=True)
        print(f"\n  Loaded {len(cls.df):,} demographic records")
    
    def test_no_null_dates(self):
        """Check for null dates."""
        null_count = self.df['date'].isna().sum()
        self.assertEqual(null_count, 0, f"Found {null_count} null dates")
        print(f"  ✓ No null dates")
    
    def test_no_negative_counts(self):
        """Check no negative counts."""
        for col in ['demo_age_5_17', 'demo_age_17_']:
            neg_count = (self.df[col] < 0).sum()
            self.assertEqual(neg_count, 0, f"Found {neg_count} negative values in {col}")
        print(f"  ✓ No negative counts")
    
    def test_districts_exist(self):
        """Check districts column exists and has values."""
        self.assertIn('district', self.df.columns)
        empty = self.df['district'].isna() | (self.df['district'] == '')
        # Allow some missing districts but not too many
        self.assertLess(empty.sum() / len(self.df), 0.05, "Too many empty districts")
        print(f"  ✓ Districts column valid")


class TestEnrolmentDataIntegrity(unittest.TestCase):
    """Test enrolment data integrity."""
    
    @classmethod
    def setUpClass(cls):
        """Load enrolment data once."""
        import glob
        data_dir = os.path.join(BASE_DIR, "data", "api_data_aadhar_enrolment")
        files = glob.glob(os.path.join(data_dir, "*.csv"))
        dfs = [pd.read_csv(f) for f in files]
        cls.df = pd.concat(dfs, ignore_index=True)
        print(f"\n  Loaded {len(cls.df):,} enrolment records")
    
    def test_age_bands_exist(self):
        """Check all age bands exist."""
        required = ['age_0_5', 'age_5_17', 'age_18_greater']
        for col in required:
            self.assertIn(col, self.df.columns, f"Missing: {col}")
        print(f"  ✓ All age bands present")
    
    def test_no_negative_counts(self):
        """Check no negative counts."""
        for col in ['age_0_5', 'age_5_17', 'age_18_greater']:
            neg_count = (self.df[col] < 0).sum()
            self.assertEqual(neg_count, 0, f"Found {neg_count} negative values in {col}")
        print(f"  ✓ No negative counts")
    
    def test_child_enrolment_dominant(self):
        """Verify children dominate enrolments."""
        total_child = self.df['age_0_5'].sum() + self.df['age_5_17'].sum()
        total_adult = self.df['age_18_greater'].sum()
        total = total_child + total_adult
        
        child_share = total_child / total
        self.assertGreater(child_share, 0.9, f"Child share too low: {child_share:.1%}")
        print(f"  ✓ Child enrolment share: {child_share:.1%}")


class TestCrossDatasetConsistency(unittest.TestCase):
    """Test consistency across datasets."""
    
    def test_overlapping_date_ranges(self):
        """Check date ranges overlap."""
        import glob
        
        date_ranges = {}
        for dataset in ['biometric', 'demographic', 'enrolment']:
            data_dir = os.path.join(BASE_DIR, "data", f"api_data_aadhar_{dataset}")
            files = glob.glob(os.path.join(data_dir, "*.csv"))
            df = pd.read_csv(files[0])
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
            date_ranges[dataset] = (df['date'].min(), df['date'].max())
        
        # Check all are in 2025
        for name, (start, end) in date_ranges.items():
            self.assertEqual(start.year, 2025, f"{name} doesn't start in 2025")
            self.assertGreaterEqual(end, start, f"{name} has invalid date range")
        
        print(f"  ✓ All datasets are in 2025")
    
    def test_common_states(self):
        """Check state overlap across datasets."""
        import glob
        
        state_sets = {}
        for dataset in ['biometric', 'demographic', 'enrolment']:
            data_dir = os.path.join(BASE_DIR, "data", f"api_data_aadhar_{dataset}")
            files = glob.glob(os.path.join(data_dir, "*.csv"))
            df = pd.read_csv(files[0])
            state_sets[dataset] = set(df['state'].dropna().unique())
        
        # Find common states
        common = state_sets['biometric'] & state_sets['demographic'] & state_sets['enrolment']
        self.assertGreater(len(common), 20, f"Too few common states: {len(common)}")
        print(f"  ✓ Common states across datasets: {len(common)}")


def run_integrity_tests():
    """Run all integrity tests."""
    print("="*70)
    print("UIDAI DATA HACKATHON 2026 - DATA INTEGRITY TESTS")
    print("="*70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestBiometricDataIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestDemographicDataIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestEnrolmentDataIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossDatasetConsistency))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("="*70)
    if result.wasSuccessful():
        print("✅ ALL DATA INTEGRITY TESTS PASSED!")
    else:
        print("❌ SOME DATA INTEGRITY TESTS FAILED")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_integrity_tests()
    sys.exit(0 if success else 1)
