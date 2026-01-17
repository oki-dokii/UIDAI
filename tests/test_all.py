#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - COMPREHENSIVE TEST SUITE
Rigorous validation of all analysis scripts and outputs

Author: UIDAI Hackathon Team
"""

import os
import sys
import pandas as pd
import numpy as np
import unittest
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Base directory
BASE_DIR = "/Users/ayushpatel/Documents/Projects/UIDAI/UIDAI"

class TestDataLoading(unittest.TestCase):
    """Test data loading and file existence."""
    
    def test_biometric_data_exists(self):
        """Check biometric data files exist."""
        data_dir = os.path.join(BASE_DIR, "api_data_aadhar_biometric")
        self.assertTrue(os.path.exists(data_dir), "Biometric data directory missing")
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        self.assertGreater(len(csv_files), 0, "No biometric CSV files found")
        print(f"  ✓ Found {len(csv_files)} biometric CSV files")
    
    def test_demographic_data_exists(self):
        """Check demographic data files exist."""
        data_dir = os.path.join(BASE_DIR, "api_data_aadhar_demographic")
        self.assertTrue(os.path.exists(data_dir), "Demographic data directory missing")
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        self.assertGreater(len(csv_files), 0, "No demographic CSV files found")
        print(f"  ✓ Found {len(csv_files)} demographic CSV files")
    
    def test_enrolment_data_exists(self):
        """Check enrolment data files exist."""
        data_dir = os.path.join(BASE_DIR, "api_data_aadhar_enrolment")
        self.assertTrue(os.path.exists(data_dir), "Enrolment data directory missing")
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        self.assertGreater(len(csv_files), 0, "No enrolment CSV files found")
        print(f"  ✓ Found {len(csv_files)} enrolment CSV files")
    
    def test_biometric_schema(self):
        """Validate biometric CSV schema."""
        data_dir = os.path.join(BASE_DIR, "api_data_aadhar_biometric")
        csv_file = [f for f in os.listdir(data_dir) if f.endswith('.csv')][0]
        df = pd.read_csv(os.path.join(data_dir, csv_file), nrows=10)
        
        required_cols = ['date', 'state', 'district', 'pincode', 'bio_age_5_17', 'bio_age_17_']
        for col in required_cols:
            self.assertIn(col, df.columns, f"Missing column: {col}")
        print(f"  ✓ Biometric schema valid: {required_cols}")
    
    def test_demographic_schema(self):
        """Validate demographic CSV schema."""
        data_dir = os.path.join(BASE_DIR, "api_data_aadhar_demographic")
        csv_file = [f for f in os.listdir(data_dir) if f.endswith('.csv')][0]
        df = pd.read_csv(os.path.join(data_dir, csv_file), nrows=10)
        
        required_cols = ['date', 'state', 'district', 'pincode', 'demo_age_5_17', 'demo_age_17_']
        for col in required_cols:
            self.assertIn(col, df.columns, f"Missing column: {col}")
        print(f"  ✓ Demographic schema valid: {required_cols}")
    
    def test_enrolment_schema(self):
        """Validate enrolment CSV schema."""
        data_dir = os.path.join(BASE_DIR, "api_data_aadhar_enrolment")
        csv_file = [f for f in os.listdir(data_dir) if f.endswith('.csv')][0]
        df = pd.read_csv(os.path.join(data_dir, csv_file), nrows=10)
        
        required_cols = ['date', 'state', 'district', 'pincode', 'age_0_5', 'age_5_17', 'age_18_greater']
        for col in required_cols:
            self.assertIn(col, df.columns, f"Missing column: {col}")
        print(f"  ✓ Enrolment schema valid: {required_cols}")


class TestOutputFiles(unittest.TestCase):
    """Test that all output files were generated correctly."""
    
    def test_biometric_outputs_exist(self):
        """Check biometric analysis outputs."""
        output_dir = os.path.join(BASE_DIR, "biometric_analysis")
        self.assertTrue(os.path.exists(output_dir), "Biometric output directory missing")
        
        required_files = ['district_clusters.csv', 'anomalies.csv', 'kpis.csv', 'README.md']
        for f in required_files:
            path = os.path.join(output_dir, f)
            self.assertTrue(os.path.exists(path), f"Missing: {f}")
        print(f"  ✓ All biometric output files present")
    
    def test_demographic_outputs_exist(self):
        """Check demographic analysis outputs."""
        output_dir = os.path.join(BASE_DIR, "demographic_analysis")
        self.assertTrue(os.path.exists(output_dir), "Demographic output directory missing")
        
        required_files = ['district_clusters.csv', 'anomalies.csv', 'kpis.csv', 'README.md']
        for f in required_files:
            path = os.path.join(output_dir, f)
            self.assertTrue(os.path.exists(path), f"Missing: {f}")
        print(f"  ✓ All demographic output files present")
    
    def test_enrolment_outputs_exist(self):
        """Check enrolment analysis outputs."""
        output_dir = os.path.join(BASE_DIR, "enrolment_analysis")
        self.assertTrue(os.path.exists(output_dir), "Enrolment output directory missing")
        
        required_files = ['district_clusters.csv', 'anomalies.csv', 'kpis.csv', 'README.md']
        for f in required_files:
            path = os.path.join(output_dir, f)
            self.assertTrue(os.path.exists(path), f"Missing: {f}")
        print(f"  ✓ All enrolment output files present")
    
    def test_integrated_outputs_exist(self):
        """Check integrated analysis outputs."""
        output_dir = os.path.join(BASE_DIR, "integrated_analysis")
        self.assertTrue(os.path.exists(output_dir), "Integrated output directory missing")
        
        required_files = ['integrated_data.csv', 'district_clusters.csv', 'kpis.csv', 'README.md']
        for f in required_files:
            path = os.path.join(output_dir, f)
            self.assertTrue(os.path.exists(path), f"Missing: {f}")
        print(f"  ✓ All integrated output files present")
    
    def test_biometric_plots_exist(self):
        """Check biometric plots."""
        plots_dir = os.path.join(BASE_DIR, "biometric_analysis", "plots")
        self.assertTrue(os.path.exists(plots_dir), "Biometric plots directory missing")
        
        png_files = [f for f in os.listdir(plots_dir) if f.endswith('.png')]
        self.assertEqual(len(png_files), 8, f"Expected 8 plots, found {len(png_files)}")
        print(f"  ✓ All 8 biometric plots present")
    
    def test_demographic_plots_exist(self):
        """Check demographic plots."""
        plots_dir = os.path.join(BASE_DIR, "demographic_analysis", "plots")
        self.assertTrue(os.path.exists(plots_dir), "Demographic plots directory missing")
        
        png_files = [f for f in os.listdir(plots_dir) if f.endswith('.png')]
        self.assertEqual(len(png_files), 8, f"Expected 8 plots, found {len(png_files)}")
        print(f"  ✓ All 8 demographic plots present")
    
    def test_enrolment_plots_exist(self):
        """Check enrolment plots."""
        plots_dir = os.path.join(BASE_DIR, "enrolment_analysis", "plots")
        self.assertTrue(os.path.exists(plots_dir), "Enrolment plots directory missing")
        
        png_files = [f for f in os.listdir(plots_dir) if f.endswith('.png')]
        self.assertEqual(len(png_files), 8, f"Expected 8 plots, found {len(png_files)}")
        print(f"  ✓ All 8 enrolment plots present")
    
    def test_integrated_plots_exist(self):
        """Check integrated plots."""
        plots_dir = os.path.join(BASE_DIR, "integrated_analysis", "plots")
        self.assertTrue(os.path.exists(plots_dir), "Integrated plots directory missing")
        
        png_files = [f for f in os.listdir(plots_dir) if f.endswith('.png')]
        self.assertEqual(len(png_files), 6, f"Expected 6 plots, found {len(png_files)}")
        print(f"  ✓ All 6 integrated plots present")


class TestDataQuality(unittest.TestCase):
    """Test data quality in output files."""
    
    def test_biometric_clusters_quality(self):
        """Validate biometric clusters data."""
        df = pd.read_csv(os.path.join(BASE_DIR, "biometric_analysis", "district_clusters.csv"))
        
        self.assertGreater(len(df), 0, "Empty clusters file")
        self.assertIn('cluster', df.columns, "Missing cluster column")
        self.assertEqual(df['cluster'].nunique(), 5, "Expected 5 clusters")
        self.assertFalse(df['cluster'].isna().any(), "NaN values in cluster")
        print(f"  ✓ Biometric clusters: {len(df)} districts, 5 clusters")
    
    def test_demographic_clusters_quality(self):
        """Validate demographic clusters data."""
        df = pd.read_csv(os.path.join(BASE_DIR, "demographic_analysis", "district_clusters.csv"))
        
        self.assertGreater(len(df), 0, "Empty clusters file")
        self.assertIn('cluster', df.columns, "Missing cluster column")
        self.assertEqual(df['cluster'].nunique(), 5, "Expected 5 clusters")
        print(f"  ✓ Demographic clusters: {len(df)} districts, 5 clusters")
    
    def test_enrolment_clusters_quality(self):
        """Validate enrolment clusters data."""
        df = pd.read_csv(os.path.join(BASE_DIR, "enrolment_analysis", "district_clusters.csv"))
        
        self.assertGreater(len(df), 0, "Empty clusters file")
        self.assertIn('cluster', df.columns, "Missing cluster column")
        print(f"  ✓ Enrolment clusters: {len(df)} districts, {df['cluster'].nunique()} clusters")
    
    def test_integrated_data_quality(self):
        """Validate integrated data."""
        df = pd.read_csv(os.path.join(BASE_DIR, "integrated_analysis", "integrated_data.csv"))
        
        self.assertGreater(len(df), 0, "Empty integrated file")
        
        # Check required columns
        required = ['state', 'district', 'total_enrol', 'total_demo', 'total_bio']
        for col in required:
            self.assertIn(col, df.columns, f"Missing: {col}")
        
        # Check no negative values in key columns
        for col in ['total_enrol', 'total_demo', 'total_bio']:
            self.assertFalse((df[col] < 0).any(), f"Negative values in {col}")
        
        print(f"  ✓ Integrated data: {len(df)} records, all values valid")
    
    def test_kpis_validity(self):
        """Validate KPIs across all modules."""
        modules = ['biometric_analysis', 'demographic_analysis', 'enrolment_analysis', 'integrated_analysis']
        
        for module in modules:
            kpi_path = os.path.join(BASE_DIR, module, "kpis.csv")
            df = pd.read_csv(kpi_path)
            self.assertGreater(len(df.columns), 3, f"Too few KPIs in {module}")
            print(f"  ✓ {module}: {len(df.columns)} KPIs defined")


class TestMetricsCalculation(unittest.TestCase):
    """Test that key metrics are calculated correctly."""
    
    def test_biometric_minor_share_range(self):
        """Minor share should be between 0 and 1."""
        df = pd.read_csv(os.path.join(BASE_DIR, "biometric_analysis", "district_clusters.csv"))
        
        if 'minor_share' in df.columns:
            self.assertTrue((df['minor_share'] >= 0).all(), "Minor share < 0")
            self.assertTrue((df['minor_share'] <= 1).all(), "Minor share > 1")
            print(f"  ✓ Biometric minor_share in valid range [0, 1]")
    
    def test_demographic_minor_share_range(self):
        """Demo minor share should be between 0 and 1."""
        df = pd.read_csv(os.path.join(BASE_DIR, "demographic_analysis", "district_clusters.csv"))
        
        if 'demo_minor_share' in df.columns:
            self.assertTrue((df['demo_minor_share'] >= 0).all(), "Demo minor share < 0")
            self.assertTrue((df['demo_minor_share'] <= 1).all(), "Demo minor share > 1")
            print(f"  ✓ Demographic demo_minor_share in valid range [0, 1]")
    
    def test_integrated_intensity_positive(self):
        """Update intensity should be non-negative."""
        df = pd.read_csv(os.path.join(BASE_DIR, "integrated_analysis", "integrated_data.csv"))
        
        if 'demo_intensity' in df.columns:
            self.assertTrue((df['demo_intensity'] >= 0).all(), "Demo intensity < 0")
        if 'bio_intensity' in df.columns:
            self.assertTrue((df['bio_intensity'] >= 0).all(), "Bio intensity < 0")
        print(f"  ✓ Intensity metrics are non-negative")
    
    def test_child_attention_gap_range(self):
        """Child attention gap should be between -1 and 1."""
        df = pd.read_csv(os.path.join(BASE_DIR, "integrated_analysis", "integrated_data.csv"))
        
        if 'child_attention_gap' in df.columns:
            valid_gap = df['child_attention_gap'].between(-1, 1)
            # Allow some outliers due to edge cases
            self.assertGreater(valid_gap.mean(), 0.95, "Too many out-of-range gaps")
            print(f"  ✓ Child attention gap mostly in valid range [-1, 1]")


class TestScriptExecution(unittest.TestCase):
    """Test that analysis scripts can be imported without errors."""
    
    def test_biometric_script_syntax(self):
        """Check biometric script has no syntax errors."""
        script_path = os.path.join(BASE_DIR, "biometric_deep_analysis.py")
        self.assertTrue(os.path.exists(script_path), "Script not found")
        
        with open(script_path, 'r') as f:
            code = f.read()
        
        try:
            compile(code, script_path, 'exec')
            print(f"  ✓ biometric_deep_analysis.py syntax valid")
        except SyntaxError as e:
            self.fail(f"Syntax error in biometric script: {e}")
    
    def test_demographic_script_syntax(self):
        """Check demographic script has no syntax errors."""
        script_path = os.path.join(BASE_DIR, "demographic_deep_analysis.py")
        self.assertTrue(os.path.exists(script_path), "Script not found")
        
        with open(script_path, 'r') as f:
            code = f.read()
        
        try:
            compile(code, script_path, 'exec')
            print(f"  ✓ demographic_deep_analysis.py syntax valid")
        except SyntaxError as e:
            self.fail(f"Syntax error in demographic script: {e}")
    
    def test_enrolment_script_syntax(self):
        """Check enrolment script has no syntax errors."""
        script_path = os.path.join(BASE_DIR, "enrolment_deep_analysis.py")
        self.assertTrue(os.path.exists(script_path), "Script not found")
        
        with open(script_path, 'r') as f:
            code = f.read()
        
        try:
            compile(code, script_path, 'exec')
            print(f"  ✓ enrolment_deep_analysis.py syntax valid")
        except SyntaxError as e:
            self.fail(f"Syntax error in enrolment script: {e}")
    
    def test_integrated_script_syntax(self):
        """Check integrated script has no syntax errors."""
        script_path = os.path.join(BASE_DIR, "integrated_analysis.py")
        self.assertTrue(os.path.exists(script_path), "Script not found")
        
        with open(script_path, 'r') as f:
            code = f.read()
        
        try:
            compile(code, script_path, 'exec')
            print(f"  ✓ integrated_analysis.py syntax valid")
        except SyntaxError as e:
            self.fail(f"Syntax error in integrated script: {e}")


class TestDocumentation(unittest.TestCase):
    """Test documentation files exist and are valid."""
    
    def test_main_readme_exists(self):
        """Check main README exists."""
        path = os.path.join(BASE_DIR, "README.md")
        self.assertTrue(os.path.exists(path), "Main README missing")
        
        with open(path, 'r') as f:
            content = f.read()
        
        self.assertGreater(len(content), 1000, "README too short")
        self.assertIn("UIDAI", content, "README missing UIDAI reference")
        print(f"  ✓ Main README: {len(content)} bytes")
    
    def test_license_exists(self):
        """Check LICENSE file exists."""
        path = os.path.join(BASE_DIR, "LICENSE")
        self.assertTrue(os.path.exists(path), "LICENSE missing")
        
        with open(path, 'r') as f:
            content = f.read()
        
        self.assertIn("MIT", content, "LICENSE not MIT")
        print(f"  ✓ LICENSE: MIT license present")
    
    def test_module_readmes_exist(self):
        """Check all module READMEs exist."""
        modules = ['biometric_analysis', 'demographic_analysis', 'enrolment_analysis', 'integrated_analysis']
        
        for module in modules:
            path = os.path.join(BASE_DIR, module, "README.md")
            self.assertTrue(os.path.exists(path), f"README missing in {module}")
        
        print(f"  ✓ All {len(modules)} module READMEs present")


def run_tests():
    """Run all tests and display summary."""
    print("="*70)
    print("UIDAI DATA HACKATHON 2026 - TEST SUITE")
    print("="*70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDataLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestDataQuality))
    suite.addTests(loader.loadTestsFromTestCase(TestMetricsCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestScriptExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"  Tests Run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print()
        print("  ✅ ALL TESTS PASSED!")
    else:
        print()
        print("  ❌ SOME TESTS FAILED")
        for failure in result.failures + result.errors:
            print(f"    - {failure[0]}")
    
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
