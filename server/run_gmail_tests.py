#!/usr/bin/env python3
"""
Test runner for Gmail integration tests.
"""

import sys
import os
import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_tests():
    """Run the Gmail integration tests."""
    print("🧪 Running Gmail Integration Tests")
    print("=" * 50)
    
    # Run the tests
    test_file = os.path.join(os.path.dirname(__file__), 'tests', 'test_gmail_integration.py')
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return 1
    
    # Run pytest
    result = pytest.main([
        'tests/test_gmail_integration.py',  # Use relative path
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--color=yes'  # Colored output
    ])
    
    if result == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {result} test(s) failed!")
    
    return result

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code) 