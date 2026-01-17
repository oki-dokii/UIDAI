#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - TEST RUNNER
Runs all test suites and generates a comprehensive report

Author: UIDAI Hackathon Team
"""

import os
import sys
import unittest
from datetime import datetime

# Add tests directory to path
BASE_DIR = "/Users/ayushpatel/Documents/Projects/UIDAI/UIDAI"
TESTS_DIR = os.path.join(BASE_DIR, "tests")
sys.path.insert(0, TESTS_DIR)


def print_banner():
    """Print test suite banner."""
    print()
    print("╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🧪 UIDAI DATA HACKATHON 2026 - COMPREHENSIVE TEST SUITE".ljust(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    print()
    print(f"  📅 Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  📁 Base Dir: {BASE_DIR}")
    print()


def run_all_tests():
    """Run all test modules."""
    print_banner()
    
    results = {}
    
    # Test modules to run
    test_modules = [
        ('test_all', 'Comprehensive Tests'),
        ('test_data_integrity', 'Data Integrity Tests'),
        ('test_metrics', 'Metrics Validation Tests'),
    ]
    
    for module_name, description in test_modules:
        print()
        print("="*70)
        print(f"RUNNING: {description}")
        print("="*70)
        
        try:
            # Import module
            module = __import__(module_name)
            
            # Load tests
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            
            # Run tests
            runner = unittest.TextTestRunner(verbosity=1)
            result = runner.run(suite)
            
            results[module_name] = {
                'total': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'passed': result.testsRun - len(result.failures) - len(result.errors)
            }
            
        except Exception as e:
            print(f"  ❌ Error running {module_name}: {e}")
            results[module_name] = {'error': str(e)}
    
    # Print summary
    print()
    print()
    print("╔" + "═"*68 + "╗")
    print("║" + "  📊 TEST SUMMARY".ljust(68) + "║")
    print("╚" + "═"*68 + "╝")
    print()
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    
    print(f"  {'Module':<30} {'Total':<10} {'Passed':<10} {'Failed':<10}")
    print("  " + "-"*60)
    
    for module, stats in results.items():
        if 'error' in stats:
            print(f"  {module:<30} {'ERROR':<10} {'-':<10} {'-':<10}")
        else:
            total_tests += stats['total']
            total_passed += stats['passed']
            total_failed += stats['failures'] + stats['errors']
            
            status = "✅" if stats['failures'] + stats['errors'] == 0 else "❌"
            print(f"  {module:<30} {stats['total']:<10} {stats['passed']:<10} {stats['failures'] + stats['errors']:<10} {status}")
    
    print("  " + "-"*60)
    print(f"  {'TOTAL':<30} {total_tests:<10} {total_passed:<10} {total_failed:<10}")
    print()
    
    # Final verdict
    if total_failed == 0:
        print("  ╔════════════════════════════════════════════════════════════╗")
        print("  ║  ✅ ALL TESTS PASSED! Your hackathon submission is solid! ║")
        print("  ╚════════════════════════════════════════════════════════════╝")
        return True
    else:
        print("  ╔════════════════════════════════════════════════════════════╗")
        print(f"  ║  ❌ {total_failed} TEST(S) FAILED - Please review and fix!           ║")
        print("  ╚════════════════════════════════════════════════════════════╝")
        return False


def run_quick_tests():
    """Run quick smoke tests."""
    print()
    print("="*70)
    print("QUICK SMOKE TESTS")
    print("="*70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Scripts exist
    scripts = [
        'biometric_deep_analysis.py',
        'demographic_deep_analysis.py',
        'enrolment_deep_analysis.py',
        'integrated_analysis.py'
    ]
    
    print("\n  📜 Script Existence:")
    for script in scripts:
        path = os.path.join(BASE_DIR, script)
        if os.path.exists(path):
            print(f"    ✓ {script}")
            tests_passed += 1
        else:
            print(f"    ✗ {script} MISSING")
            tests_failed += 1
    
    # Test 2: Output directories exist
    outputs = [
        'biometric_analysis',
        'demographic_analysis',
        'enrolment_analysis',
        'integrated_analysis'
    ]
    
    print("\n  📁 Output Directories:")
    for output in outputs:
        path = os.path.join(BASE_DIR, output)
        if os.path.exists(path):
            print(f"    ✓ {output}/")
            tests_passed += 1
        else:
            print(f"    ✗ {output}/ MISSING")
            tests_failed += 1
    
    # Test 3: Key files exist
    print("\n  📄 Key Files:")
    key_files = ['README.md', 'LICENSE', 'executive_summary.md']
    for f in key_files:
        path = os.path.join(BASE_DIR, f)
        if os.path.exists(path):
            print(f"    ✓ {f}")
            tests_passed += 1
        else:
            print(f"    ✗ {f} MISSING")
            tests_failed += 1
    
    # Summary
    print()
    print(f"  Quick Tests: {tests_passed} passed, {tests_failed} failed")
    print("="*70)
    
    return tests_failed == 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='UIDAI Test Runner')
    parser.add_argument('--quick', action='store_true', help='Run quick smoke tests only')
    parser.add_argument('--all', action='store_true', help='Run all comprehensive tests')
    
    args = parser.parse_args()
    
    if args.quick:
        success = run_quick_tests()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
