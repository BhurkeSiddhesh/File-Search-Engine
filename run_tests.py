#!/usr/bin/env python3
"""
Test runner for the file search engine project.
This script discovers and runs all unit tests in the tests directory.
"""

import unittest
import sys
import os

# Add the workspace directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

if __name__ == '__main__':
    # Discover and run all tests in the tests directory
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    result = runner.run(suite)
    
    # Exit with error code if tests failed
    if result.failures or result.errors:
        sys.exit(1)
    else:
        print("\nAll tests passed!")