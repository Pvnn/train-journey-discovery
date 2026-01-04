"""
Master Test Runner - Runs all tests in sequence.
Run this to verify complete Day 4 implementation.
"""

import sys
import os
# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
  sys.path.insert(0, project_root)

def run_all_tests():
  print("INTEGRATION TEST SUITE")
  
  print("Testing: Schemas, Data Loader, Journey Service, Flask API")
  print("Using: Mock MCRaptor (real algorithm not needed)")
  

  results = []

  # Test 1: Data Loader
  from backend.tests.test_01_data_loader import test_data_loader
  result1 = test_data_loader()
  results.append(("Data Loader", result1))

  # Test 2: Schema Validation
  from backend.tests.test_02_schema import test_schema_validation
  result2 = test_schema_validation()
  results.append(("Schema Validation", result2))

  # Test 3: Journey Service
  from backend.tests.test_03_journey_service import test_journey_service
  result3 = test_journey_service()
  results.append(("Journey Service", result3))

  # Test 4: Flask API
  from backend.tests.test_04_flask_api import test_flask_api
  result4 = test_flask_api()
  results.append(("Flask API", result4))

  # Print summary
  
  print("TEST SUMMARY")
  

  passed = 0
  failed = 0

  for name, result in results:
    status = "PASSED" if result else "FAILED"
    print(f"{name:<25} : {status}")
    if result:
      passed += 1
    else:
      failed += 1

  
  print(f"Total: {len(results)} tests")
  print(f"Passed: {passed}")
  print(f"Failed: {failed}")
  

  if failed == 0:
    print("\nALL TESTS PASSED!")
    return 0
  else:
    print(f"\n{failed} test(s) failed. Please fix issues before proceeding.")
    return 1

if __name__ == "__main__":
  sys.exit(run_all_tests())
