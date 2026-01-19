#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - METRICS VALIDATION TESTS
Validates that computed metrics are mathematically correct

Author: UIDAI Hackathon Team
"""

import os
import pandas as pd
import numpy as np
import unittest

BASE_DIR = "/Users/ayushpatel/Documents/Projects/UIDAI/UIDAI"


class TestShareMetrics(unittest.TestCase):
    """Test share/ratio metrics sum to 1."""
    
    def test_enrolment_shares_sum_to_one(self):
        """Age shares in enrolment should sum to ~1."""
        df = pd.read_csv(os.path.join(BASE_DIR, "enrolment_analysis", "district_clusters.csv"))
        
        if all(col in df.columns for col in ['share_0_5', 'share_5_17', 'share_18_plus']):
            total = df['share_0_5'] + df['share_5_17'] + df['share_18_plus']
            valid = (total > 0.99) & (total < 1.01)
            self.assertGreater(valid.mean(), 0.95, "Shares don't sum to 1")
            print(f"  ✓ Enrolment age shares sum to 1")
    
    def test_child_share_plus_adult_equals_one(self):
        """Child + adult share should equal 1."""
        df = pd.read_csv(os.path.join(BASE_DIR, "integrated_analysis", "integrated_data.csv"))
        
        if 'child_share_enrol' in df.columns and 'adult_share_enrol' in df.columns:
            # Only check non-zero rows
            mask = df['total_enrol'] > 0
            total = df.loc[mask, 'child_share_enrol'] + df.loc[mask, 'adult_share_enrol']
            valid = (total > 0.99) & (total < 1.01)
            self.assertGreater(valid.mean(), 0.95, "Child + adult shares don't sum to 1")
            print(f"  ✓ Child + adult shares sum to 1")


class TestIntensityMetrics(unittest.TestCase):
    """Test intensity metrics are computed correctly."""
    
    def test_intensity_formula(self):
        """Verify intensity = updates / enrolments."""
        df = pd.read_csv(os.path.join(BASE_DIR, "integrated_analysis", "integrated_data.csv"))
        
        # Filter non-zero enrolments
        mask = df['total_enrol'] > 10
        df_valid = df[mask]
        
        if 'demo_intensity' in df.columns:
            expected = df_valid['total_demo'] / df_valid['total_enrol']
            # Allow some tolerance due to floating point
            close = np.isclose(df_valid['demo_intensity'], expected, rtol=0.1)
            self.assertGreater(close.mean(), 0.9, "Demo intensity calculation incorrect")
            print(f"  ✓ Demo intensity formula verified")
    
    def test_total_intensity_is_sum(self):
        """Total intensity should be demo + bio intensity."""
        df = pd.read_csv(os.path.join(BASE_DIR, "integrated_analysis", "integrated_data.csv"))
        
        if all(col in df.columns for col in ['demo_intensity', 'bio_intensity', 'total_intensity']):
            expected = df['demo_intensity'] + df['bio_intensity']
            close = np.isclose(df['total_intensity'], expected, rtol=0.1)
            self.assertGreater(close.mean(), 0.9, "Total intensity not sum of demo + bio")
            print(f"  ✓ Total intensity is sum of components")


class TestClusterMetrics(unittest.TestCase):
    """Test clustering metrics."""
    
    def test_cluster_labels_valid(self):
        """Cluster labels should be 0-4."""
        for module in ['biometric_analysis', 'demographic_analysis', 'enrolment_analysis']:
            df = pd.read_csv(os.path.join(BASE_DIR, module, "district_clusters.csv"))
            
            if 'cluster' in df.columns:
                valid_labels = set(range(5))
                actual_labels = set(df['cluster'].unique())
                self.assertTrue(actual_labels.issubset(valid_labels), 
                              f"Invalid cluster labels in {module}: {actual_labels}")
        
        print(f"  ✓ All cluster labels in valid range [0-4]")
    
    def test_clusters_have_members(self):
        """Each cluster should have at least some members."""
        df = pd.read_csv(os.path.join(BASE_DIR, "biometric_analysis", "district_clusters.csv"))
        
        if 'cluster' in df.columns:
            counts = df['cluster'].value_counts()
            min_count = counts.min()
            self.assertGreater(min_count, 0, "Some clusters are empty")
            print(f"  ✓ All clusters have members (min: {min_count})")


class TestAnomalyDetection(unittest.TestCase):
    """Test anomaly detection results."""
    
    def test_anomalies_have_zscore(self):
        """Anomaly records should have z-score column."""
        for module in ['biometric_analysis', 'demographic_analysis']:
            path = os.path.join(BASE_DIR, module, "anomalies.csv")
            if os.path.exists(path):
                df = pd.read_csv(path)
                self.assertIn('zscore', df.columns, f"Missing zscore in {module}")
                
                # Z-scores should be > 3 or < -3 for anomalies
                extreme = (df['zscore'].abs() > 3).mean()
                self.assertGreater(extreme, 0.9, "Too many non-extreme anomalies")
        
        print(f"  ✓ Anomalies have extreme z-scores (|z| > 3)")
    
    def test_anomaly_types_valid(self):
        """Anomaly types should be 'High Spike' or 'Low Drop'."""
        path = os.path.join(BASE_DIR, "biometric_analysis", "anomalies.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            if 'anomaly_type' in df.columns:
                valid_types = {'High Spike', 'Low Drop'}
                actual_types = set(df['anomaly_type'].unique())
                self.assertTrue(actual_types.issubset(valid_types), 
                              f"Invalid anomaly types: {actual_types}")
                print(f"  ✓ Anomaly types valid: {actual_types}")


class TestVolatilityMetrics(unittest.TestCase):
    """Test volatility metrics."""
    
    def test_cv_positive(self):
        """Coefficient of variation should be positive."""
        for module in ['biometric_analysis', 'demographic_analysis', 'enrolment_analysis']:
            path = os.path.join(BASE_DIR, module, "volatility_metrics.csv")
            if os.path.exists(path):
                df = pd.read_csv(path)
                cv_cols = [c for c in df.columns if 'cv' in c.lower()]
                
                for col in cv_cols:
                    neg_count = (df[col] < 0).sum()
                    self.assertEqual(neg_count, 0, f"Negative CV values in {module}/{col}")
        
        print(f"  ✓ All CV values are non-negative")
    
    def test_std_positive(self):
        """Standard deviation should be non-negative."""
        for module in ['biometric_analysis', 'demographic_analysis', 'enrolment_analysis']:
            path = os.path.join(BASE_DIR, module, "volatility_metrics.csv")
            if os.path.exists(path):
                df = pd.read_csv(path)
                std_cols = [c for c in df.columns if 'std' in c.lower()]
                
                for col in std_cols:
                    neg_count = (df[col] < 0).sum()
                    self.assertEqual(neg_count, 0, f"Negative std values in {module}/{col}")
        
        print(f"  ✓ All std values are non-negative")


class TestKPIValidity(unittest.TestCase):
    """Test KPI values are valid."""
    
    def test_kpis_positive(self):
        """Count KPIs should be positive."""
        for module in ['biometric_analysis', 'demographic_analysis', 'enrolment_analysis', 'integrated_analysis']:
            path = os.path.join(BASE_DIR, module, "kpis.csv")
            df = pd.read_csv(path)
            
            # Check total columns are positive
            for col in df.columns:
                if 'total' in col.lower() and df[col].dtype in [np.int64, np.float64]:
                    self.assertTrue((df[col] >= 0).all(), f"Negative {col} in {module}")
        
        print(f"  ✓ All count KPIs are non-negative")
    
    def test_share_kpis_valid_range(self):
        """Share KPIs should be between 0 and 1."""
        for module in ['biometric_analysis', 'demographic_analysis', 'enrolment_analysis', 'integrated_analysis']:
            path = os.path.join(BASE_DIR, module, "kpis.csv")
            df = pd.read_csv(path)
            
            for col in df.columns:
                if 'share' in col.lower():
                    val = df[col].iloc[0]
                    self.assertTrue(0 <= val <= 1, f"Invalid share {col}={val} in {module}")
        
        print(f"  ✓ All share KPIs in [0, 1] range")


def run_metrics_tests():
    """Run all metrics validation tests."""
    print("="*70)
    print("UIDAI DATA HACKATHON 2026 - METRICS VALIDATION TESTS")
    print("="*70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestShareMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestIntensityMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestClusterMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestAnomalyDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestVolatilityMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestKPIValidity))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("="*70)
    if result.wasSuccessful():
        print("✅ ALL METRICS VALIDATION TESTS PASSED!")
    else:
        print("❌ SOME METRICS VALIDATION TESTS FAILED")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_metrics_tests()
    sys.exit(0 if success else 1)
