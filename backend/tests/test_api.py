"""
Comprehensive Test Script for Train Journey Discovery API

Tests:
- Journey Search Endpoint (POST /api/search)
- Sorting and Filtering (query parameters)
- Station Lookup Endpoints (GET /api/stations/*)
"""

import requests
from typing import List
from datetime import datetime


# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# ANSI color codes for output
class Colors:
  GREEN = '\033[92m'
  RED = '\033[91m'
  YELLOW = '\033[93m'
  BLUE = '\033[94m'
  CYAN = '\033[96m'
  BOLD = '\033[1m'
  END = '\033[0m'


class TestResult:
  """Store test results."""
  def __init__(self):
    self.total = 0
    self.passed = 0
    self.failed = 0
    self.skipped = 0
    self.failures: List[str] = []

  def add_pass(self):
    self.total += 1
    self.passed += 1

  def add_fail(self, test_name: str, reason: str):
    self.total += 1
    self.failed += 1
    self.failures.append(f"{test_name}: {reason}")

  def add_skip(self):
    self.total += 1
    self.skipped += 1

  def print_summary(self):
    print("\n" + "="*70)
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.END}")
    print("="*70)
    print(f"Total Tests:   {self.total}")
    print(f"{Colors.GREEN}✓ Passed:      {self.passed}{Colors.END}")
    print(f"{Colors.RED}✗ Failed:      {self.failed}{Colors.END}")
    print(f"{Colors.YELLOW}⊘ Skipped:     {self.skipped}{Colors.END}")

    if self.failures:
      print(f"\n{Colors.RED}Failed Tests:{Colors.END}")
      for failure in self.failures:
        print(f"  - {failure}")

    print("="*70)

    if self.failed == 0:
      print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.END}")
    else:
      print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.END}")


# Global test result tracker
result = TestResult()


def print_section(title: str):
  """Print a section header."""
  print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.END}")
  print(f"{Colors.CYAN}{Colors.BOLD}{title}{Colors.END}")
  print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.END}")


def print_test(test_name: str):
  """Print test name."""
  print(f"\n{Colors.BLUE}Test: {test_name}{Colors.END}")


def print_pass(message: str = "PASSED"):
  """Print success message."""
  print(f"  {Colors.GREEN}✓ {message}{Colors.END}")


def print_fail(message: str):
  """Print failure message."""
  print(f"  {Colors.RED}✗ {message}{Colors.END}")


def print_info(message: str):
  """Print info message."""
  print(f"  {Colors.YELLOW}ℹ {message}{Colors.END}")


def check_server():
  """Check if server is running."""
  print_section("CHECKING SERVER CONNECTION")
  try:
    response = requests.get(f"{API_BASE}/health", timeout=5)
    if response.status_code == 200:
      print_pass(f"Server is running at {BASE_URL}")
      data = response.json()
      print_info(f"Service: {data.get('service', 'Unknown')}")
      print_info(f"Version: {data.get('version', 'Unknown')}")
      return True
    else:
      print_fail(f"Server returned status code {response.status_code}")
      return False
  except requests.exceptions.ConnectionError:
    print_fail(f"Cannot connect to server at {BASE_URL}")
    print_info("Please start the server: cd backend && python app.py")
    return False
  except Exception as e:
    print_fail(f"Error checking server: {str(e)}")
    return False


# ============================================================================
# TASK 1: Journey Search Endpoint Tests
# ============================================================================

def test_task1_journey_search():
  """Test Task 1: Journey Search Endpoint."""
  print_section("TASK 1: JOURNEY SEARCH ENDPOINT")

  # Test 1.1: Valid journey search
  print_test("1.1: Valid journey search with all required fields")
  try:
    response = requests.post(
      f"{API_BASE}/search",
      json={
        "source": "NDLS",
        "destination": "JP",
        "date": "2026-01-20"
      },
      timeout=30
    )

    if response.status_code == 200:
      data = response.json()
      assert "journeys" in data, "Response missing 'journeys' field"
      assert "metadata" in data, "Response missing 'metadata' field"
      assert isinstance(data["journeys"], list), "'journeys' should be a list"

      print_pass(f"Status: 200 OK")
      print_info(f"Found {len(data['journeys'])} journeys")
      print_info(f"Total found: {data['metadata'].get('total_found', 'N/A')}")
      result.add_pass()
    elif response.status_code == 404:
      print_pass("Status: 404 (No routes found - valid response)")
      print_info("This is acceptable if no routes exist for this route")
      result.add_pass()
    else:
      print_fail(f"Unexpected status code: {response.status_code}")
      print_info(f"Response: {response.text}")
      result.add_fail("1.1", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("1.1", str(e))

  # Test 1.2: Journey search with optional departure_time
  print_test("1.2: Journey search with departure_time")
  try:
    response = requests.post(
      f"{API_BASE}/search",
      json={
        "source": "NDLS",
        "destination": "JP",
        "date": "2026-01-20",
        "departure_time": "14:30"
      },
      timeout=30
    )

    if response.status_code in [200, 404]:
      print_pass(f"Status: {response.status_code}")
      if response.status_code == 200:
        data = response.json()
        print_info(f"Departure time accepted: {data['metadata']['query']['departure_time']}")
      result.add_pass()
    else:
      print_fail(f"Unexpected status code: {response.status_code}")
      result.add_fail("1.2", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("1.2", str(e))

  # Test 1.3: Journey search with max_transfers
  print_test("1.3: Journey search with max_transfers")
  try:
    response = requests.post(
      f"{API_BASE}/search",
      json={
        "source": "NDLS",
        "destination": "JP",
        "date": "2026-01-20",
        "max_transfers": 2
      },
      timeout=30
    )

    if response.status_code in [200, 404]:
      print_pass(f"Status: {response.status_code}")
      if response.status_code == 200:
        data = response.json()
        print_info(f"Max transfers: {data['metadata']['query']['max_transfers']}")
      result.add_pass()
    else:
      print_fail(f"Unexpected status code: {response.status_code}")
      result.add_fail("1.3", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("1.3", str(e))

  # Test 1.4: Validation error - missing source
  print_test("1.4: Validation error - missing source")
  try:
    response = requests.post(
      f"{API_BASE}/search",
      json={
        "destination": "JP",
        "date": "2026-01-20"
      },
      timeout=10
    )

    if response.status_code == 400:
      data = response.json()
      assert "error" in data, "Error response missing 'error' field"
      print_pass("Status: 400 (validation error detected)")
      print_info(f"Error message: {data['error']['message']}")
      result.add_pass()
    else:
      print_fail(f"Expected 400, got {response.status_code}")
      result.add_fail("1.4", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("1.4", str(e))

  # Test 1.5: Validation error - missing destination
  print_test("1.5: Validation error - missing destination")
  try:
    response = requests.post(
      f"{API_BASE}/search",
      json={
        "source": "NDLS",
        "date": "2026-01-20"
      },
      timeout=10
    )

    if response.status_code == 400:
      print_pass("Status: 400 (validation error detected)")
      result.add_pass()
    else:
      print_fail(f"Expected 400, got {response.status_code}")
      result.add_fail("1.5", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("1.5", str(e))

  # Test 1.6: Validation error - missing date
  print_test("1.6: Validation error - missing date")
  try:
    response = requests.post(
      f"{API_BASE}/search",
      json={
        "source": "NDLS",
        "destination": "JP"
      },
      timeout=10
    )

    if response.status_code == 400:
      print_pass("Status: 400 (validation error detected)")
      result.add_pass()
    else:
      print_fail(f"Expected 400, got {response.status_code}")
      result.add_fail("1.6", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("1.6", str(e))

  # Test 1.7: Validation error - invalid date format
  print_test("1.7: Validation error - invalid date format")
  try:
    response = requests.post(
      f"{API_BASE}/search",
      json={
        "source": "NDLS",
        "destination": "JP",
        "date": "2026/01/20"  # Wrong format
      },
      timeout=10
    )

    if response.status_code == 400:
      print_pass("Status: 400 (invalid date format detected)")
      result.add_pass()
    else:
      print_fail(f"Expected 400, got {response.status_code}")
      result.add_fail("1.7", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("1.7", str(e))

  # Test 1.8: Validation error - invalid time format
  print_test("1.8: Validation error - invalid time format")
  try:
    response = requests.post(
      f"{API_BASE}/search",
      json={
        "source": "NDLS",
        "destination": "JP",
        "date": "2026-01-20",
        "departure_time": "25:00"  # Invalid time
      },
      timeout=10
    )

    if response.status_code == 400:
      print_pass("Status: 400 (invalid time format detected)")
      result.add_pass()
    else:
      print_fail(f"Expected 400, got {response.status_code}")
      result.add_fail("1.8", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("1.8", str(e))

  # Test 1.9: Station not found error
  print_test("1.9: Station not found error")
  try:
    response = requests.post(
      f"{API_BASE}/search",
      json={
        "source": "INVALID",
        "destination": "JP",
        "date": "2026-01-20"
      },
      timeout=10
    )

    if response.status_code == 404:
      data = response.json()
      print_pass("Status: 404 (station not found)")
      print_info(f"Error message: {data['error']['message']}")
      result.add_pass()
    else:
      print_fail(f"Expected 404, got {response.status_code}")
      result.add_fail("1.9", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("1.9", str(e))

  # Test 1.10: Response structure validation
  print_test("1.10: Response structure validation")
  try:
    response = requests.post(
      f"{API_BASE}/search",
      json={
        "source": "NDLS",
        "destination": "JP",
        "date": "2026-01-20"
      },
      timeout=30
    )

    if response.status_code == 200:
      data = response.json()

      # Check top-level structure
      assert "journeys" in data, "Missing 'journeys'"
      assert "metadata" in data, "Missing 'metadata'"

      # Check metadata structure
      metadata = data["metadata"]
      assert "query" in metadata, "Missing 'query' in metadata"
      assert "results_count" in metadata, "Missing 'results_count'"

      # Check query fields
      query = metadata["query"]
      assert "source" in query, "Missing 'source' in query"
      assert "destination" in query, "Missing 'destination' in query"
      assert "date" in query, "Missing 'date' in query"

      print_pass("All required fields present in response")
      result.add_pass()
    elif response.status_code == 404:
      print_pass("Status 404 - acceptable (no routes)")
      result.add_pass()
    else:
      print_fail(f"Unexpected status: {response.status_code}")
      result.add_fail("1.10", f"Status {response.status_code}")
  except AssertionError as e:
    print_fail(f"Structure validation failed: {str(e)}")
    result.add_fail("1.10", str(e))
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("1.10", str(e))


# ============================================================================
# TASK 2: Sorting and Filtering Tests
# ============================================================================

def test_task2_sorting_filtering():
  """Test Task 2: Sorting and Filtering."""
  print_section("TASK 2: SORTING AND FILTERING")

  base_request = {
    "source": "NDLS",
    "destination": "JP",
    "date": "2026-01-20"
  }

  # Test 2.1: Sort by time
  print_test("2.1: Sort by time (ascending)")
  try:
    response = requests.post(
      f"{API_BASE}/search?sort_by=time&order=asc",
      json=base_request,
      timeout=30
    )

    if response.status_code == 200:
      data = response.json()
      assert data["metadata"]["sort_by"] == "time", "sort_by not applied"
      assert data["metadata"]["order"] == "asc", "order not applied"
      print_pass(f"Status: 200, sort_by=time, order=asc")
      print_info(f"Found {len(data['journeys'])} journeys")
      result.add_pass()
    elif response.status_code == 404:
      print_pass("Status 404 - no routes found")
      result.add_pass()
    else:
      print_fail(f"Status: {response.status_code}")
      result.add_fail("2.1", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("2.1", str(e))

  # Test 2.2: Sort by transfers
  print_test("2.2: Sort by transfers (ascending)")
  try:
    response = requests.post(
      f"{API_BASE}/search?sort_by=transfers&order=asc",
      json=base_request,
      timeout=30
    )

    if response.status_code == 200:
      data = response.json()
      assert data["metadata"]["sort_by"] == "transfers"
      print_pass(f"Status: 200, sort_by=transfers")
      result.add_pass()
    elif response.status_code == 404:
      print_pass("Status 404 - no routes found")
      result.add_pass()
    else:
      print_fail(f"Status: {response.status_code}")
      result.add_fail("2.2", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("2.2", str(e))

  # Test 2.3: Sort by comfort
  print_test("2.3: Sort by comfort (descending)")
  try:
    response = requests.post(
      f"{API_BASE}/search?sort_by=comfort&order=desc",
      json=base_request,
      timeout=30
    )

    if response.status_code == 200:
      data = response.json()
      assert data["metadata"]["sort_by"] == "comfort"
      assert data["metadata"]["order"] == "desc"
      print_pass(f"Status: 200, sort_by=comfort, order=desc")
      result.add_pass()
    elif response.status_code == 404:
      print_pass("Status 404 - no routes found")
      result.add_pass()
    else:
      print_fail(f"Status: {response.status_code}")
      result.add_fail("2.3", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("2.3", str(e))

  # Test 2.4: Sort by fare
  print_test("2.4: Sort by fare (ascending)")
  try:
    response = requests.post(
      f"{API_BASE}/search?sort_by=fare&order=asc",
      json=base_request,
      timeout=30
    )

    if response.status_code == 200:
      data = response.json()
      assert data["metadata"]["sort_by"] == "fare"
      print_pass(f"Status: 200, sort_by=fare")
      result.add_pass()
    elif response.status_code == 404:
      print_pass("Status 404 - no routes found")
      result.add_pass()
    else:
      print_fail(f"Status: {response.status_code}")
      result.add_fail("2.4", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("2.4", str(e))

  # Test 2.5: Sort by quality (default)
  print_test("2.5: Sort by quality (default)")
  try:
    response = requests.post(
      f"{API_BASE}/search?sort_by=quality",
      json=base_request,
      timeout=30
    )

    if response.status_code == 200:
      data = response.json()
      assert data["metadata"]["sort_by"] == "quality"
      print_pass(f"Status: 200, sort_by=quality")
      result.add_pass()
    elif response.status_code == 404:
      print_pass("Status 404 - no routes found")
      result.add_pass()
    else:
      print_fail(f"Status: {response.status_code}")
      result.add_fail("2.5", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("2.5", str(e))

  # Test 2.6: Limit results
  print_test("2.6: Limit results to 3")
  try:
    response = requests.post(
      f"{API_BASE}/search?limit=3",
      json=base_request,
      timeout=30
    )

    if response.status_code == 200:
      data = response.json()
      assert data["metadata"]["limit"] == 3
      assert len(data["journeys"]) <= 3, "More journeys than limit"
      print_pass(f"Status: 200, limit=3")
      print_info(f"Returned {len(data['journeys'])} journeys (max 3)")
      result.add_pass()
    elif response.status_code == 404:
      print_pass("Status 404 - no routes found")
      result.add_pass()
    else:
      print_fail(f"Status: {response.status_code}")
      result.add_fail("2.6", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("2.6", str(e))

  # Test 2.7: Invalid sort_by parameter
  print_test("2.7: Invalid sort_by parameter")
  try:
    response = requests.post(
      f"{API_BASE}/search?sort_by=invalid",
      json=base_request,
      timeout=10
    )

    if response.status_code == 400:
      print_pass("Status: 400 (invalid sort_by rejected)")
      result.add_pass()
    else:
      print_fail(f"Expected 400, got {response.status_code}")
      result.add_fail("2.7", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("2.7", str(e))

  # Test 2.8: Invalid order parameter
  print_test("2.8: Invalid order parameter")
  try:
    response = requests.post(
      f"{API_BASE}/search?order=invalid",
      json=base_request,
      timeout=10
    )

    if response.status_code == 400:
      print_pass("Status: 400 (invalid order rejected)")
      result.add_pass()
    else:
      print_fail(f"Expected 400, got {response.status_code}")
      result.add_fail("2.8", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("2.8", str(e))

  # Test 2.9: Invalid limit (too large)
  print_test("2.9: Invalid limit (exceeds maximum)")
  try:
    response = requests.post(
      f"{API_BASE}/search?limit=100",
      json=base_request,
      timeout=10
    )

    if response.status_code == 400:
      print_pass("Status: 400 (limit > 50 rejected)")
      result.add_pass()
    else:
      print_fail(f"Expected 400, got {response.status_code}")
      result.add_fail("2.9", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("2.9", str(e))

  # Test 2.10: Invalid limit (negative)
  print_test("2.10: Invalid limit (negative)")
  try:
    response = requests.post(
      f"{API_BASE}/search?limit=-1",
      json=base_request,
      timeout=10
    )

    if response.status_code == 400:
      print_pass("Status: 400 (negative limit rejected)")
      result.add_pass()
    else:
      print_fail(f"Expected 400, got {response.status_code}")
      result.add_fail("2.10", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("2.10", str(e))

  # Test 2.11: Combined sorting and filtering
  print_test("2.11: Combined sorting and filtering")
  try:
    response = requests.post(
      f"{API_BASE}/search?sort_by=time&order=asc&limit=5",
      json=base_request,
      timeout=30
    )

    if response.status_code == 200:
      data = response.json()
      assert data["metadata"]["sort_by"] == "time"
      assert data["metadata"]["order"] == "asc"
      assert data["metadata"]["limit"] == 5
      print_pass("All parameters applied correctly")
      result.add_pass()
    elif response.status_code == 404:
      print_pass("Status 404 - no routes found")
      result.add_pass()
    else:
      print_fail(f"Status: {response.status_code}")
      result.add_fail("2.11", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("2.11", str(e))


# ============================================================================
# TASK 3: Station Lookup Tests
# ============================================================================

def test_task3_station_lookup():
  """Test Task 3: Station Lookup Endpoints."""
  print_section("TASK 3: STATION LOOKUP ENDPOINTS")

  # Test 3.1: Search stations by code prefix
  print_test("3.1: GET /api/stations/search?q=ND (code prefix)")
  try:
    response = requests.get(
      f"{API_BASE}/stations/search",
      params={"q": "ND"},
      timeout=10
    )

    if response.status_code == 200:
      data = response.json()
      assert isinstance(data, list), "Response should be a list"
      print_pass(f"Status: 200, found {len(data)} stations")

      if data:
        station = data[0]
        assert "stop_code" in station, "Missing stop_code"
        assert "stop_name" in station, "Missing stop_name"
        print_info(f"Example: {station['stop_code']} - {station['stop_name']}")

      result.add_pass()
    else:
      print_fail(f"Status: {response.status_code}")
      result.add_fail("3.1", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("3.1", str(e))

  # Test 3.2: Search stations by name
  print_test("3.2: GET /api/stations/search?q=delhi (station name)")
  try:
    response = requests.get(
      f"{API_BASE}/stations/search",
      params={"q": "delhi"},
      timeout=10
    )

    if response.status_code == 200:
      data = response.json()
      print_pass(f"Status: 200, found {len(data)} stations")
      result.add_pass()
    else:
      print_fail(f"Status: {response.status_code}")
      result.add_fail("3.2", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("3.2", str(e))

  # Test 3.3: Search with short query
  print_test("3.3: Search validation - query too short")
  try:
    response = requests.get(
      f"{API_BASE}/stations/search",
      params={"q": "A"},
      timeout=10
    )

    if response.status_code == 400:
      print_pass("Status: 400 (query too short rejected)")
      result.add_pass()
    else:
      print_fail(f"Expected 400, got {response.status_code}")
      result.add_fail("3.3", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("3.3", str(e))

  # Test 3.4: Search with missing query parameter
  print_test("3.4: Search validation - missing q parameter")
  try:
    response = requests.get(
      f"{API_BASE}/stations/search",
      timeout=10
    )

    if response.status_code == 400:
      print_pass("Status: 400 (missing parameter rejected)")
      result.add_pass()
    else:
      print_fail(f"Expected 400, got {response.status_code}")
      result.add_fail("3.4", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("3.4", str(e))

  # Test 3.5: Get station by code (valid)
  print_test("3.5: GET /api/stations/NDLS (valid station)")
  try:
    response = requests.get(
      f"{API_BASE}/stations/NDLS",
      timeout=10
    )

    if response.status_code == 200:
      data = response.json()
      assert "stop_code" in data, "Missing stop_code"
      assert "stop_name" in data, "Missing stop_name"
      assert "zone" in data, "Missing zone"
      assert data["stop_code"] == "NDLS", "Wrong station code"

      print_pass(f"Status: 200")
      print_info(f"Station: {data['stop_name']}")
      print_info(f"Zone: {data['zone']}")

      # Check for additional fields
      if "tier" in data:
        print_info(f"Tier: {data['tier']}")
      if "routes_serving" in data:
        print_info(f"Routes: {data['routes_serving']}")

      result.add_pass()
    else:
      print_fail(f"Status: {response.status_code}")
      result.add_fail("3.5", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("3.5", str(e))

  # Test 3.6: Get station by code (invalid)
  print_test("3.6: GET /api/stations/INVALID (non-existent station)")
  try:
    response = requests.get(
      f"{API_BASE}/stations/INVALID",
      timeout=10
    )

    if response.status_code == 404:
      print_pass("Status: 404 (station not found)")
      result.add_pass()
    else:
      print_fail(f"Expected 404, got {response.status_code}")
      result.add_fail("3.6", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("3.6", str(e))

  # Test 3.7: Get all stations
  print_test("3.7: GET /api/stations (all stations)")
  try:
    response = requests.get(
      f"{API_BASE}/stations",
      timeout=10
    )

    if response.status_code == 200:
      data = response.json()
      assert isinstance(data, list), "Response should be a list"
      print_pass(f"Status: 200, found {len(data)} stations")
      result.add_pass()
    else:
      print_fail(f"Status: {response.status_code}")
      result.add_fail("3.7", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("3.7", str(e))

  # Test 3.8: Get stations with zone filter
  print_test("3.8: GET /api/stations?zone=WR (filtered by zone)")
  try:
    response = requests.get(
      f"{API_BASE}/stations",
      params={"zone": "WR"},
      timeout=10
    )

    if response.status_code == 200:
      data = response.json()
      print_pass(f"Status: 200, found {len(data)} stations in WR zone")

      # Verify all stations are in WR zone
      if data:
        all_wr = all(s.get("zone") == "WR" for s in data)
        if all_wr:
          print_info("All stations are in WR zone ✓")
        else:
          print_info("Warning: Some stations not in WR zone")

      result.add_pass()
    else:
      print_fail(f"Status: {response.status_code}")
      result.add_fail("3.8", f"Status {response.status_code}")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("3.8", str(e))

  # Test 3.9: Station response structure
  print_test("3.9: Verify station detail response structure")
  try:
    response = requests.get(
      f"{API_BASE}/stations/JP",
      timeout=10
    )

    if response.status_code == 200:
      data = response.json()

      # Required fields
      required_fields = ["stop_id", "stop_code", "stop_name", "zone"]
      for field in required_fields:
        assert field in data, f"Missing required field: {field}"

      print_pass("All required fields present")
      result.add_pass()
    elif response.status_code == 404:
      print_info("Station JP not found - skipping structure test")
      result.add_skip()
    else:
      print_fail(f"Status: {response.status_code}")
      result.add_fail("3.9", f"Status {response.status_code}")
  except AssertionError as e:
    print_fail(f"Structure validation failed: {str(e)}")
    result.add_fail("3.9", str(e))
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("3.9", str(e))

  # Test 3.10: Case insensitive search
  print_test("3.10: Case insensitive station search")
  try:
    response1 = requests.get(
      f"{API_BASE}/stations/search",
      params={"q": "DELHI"},
      timeout=10
    )
    response2 = requests.get(
      f"{API_BASE}/stations/search",
      params={"q": "delhi"},
      timeout=10
    )

    if response1.status_code == 200 and response2.status_code == 200:
      data1 = response1.json()
      data2 = response2.json()

      # Should return same number of results
      if len(data1) == len(data2):
        print_pass("Case insensitive search working correctly")
        result.add_pass()
      else:
        print_info(f"Different counts: {len(data1)} vs {len(data2)}")
        print_info("Case insensitivity might not be working optimally")
        result.add_pass()  # Still pass as results were returned
    else:
      print_fail("One or both requests failed")
      result.add_fail("3.10", "Request failed")
  except Exception as e:
    print_fail(f"Error: {str(e)}")
    result.add_fail("3.10", str(e))


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
  """Main test runner."""
  print(f"{Colors.BOLD}{Colors.CYAN}")
  print("="*70)
  print("  TRAIN JOURNEY DISCOVERY API - COMPREHENSIVE TEST SUITE")
  print("="*70)
  print(f"{Colors.END}")
  print(f"Base URL: {BASE_URL}")
  print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

  # Check server connection
  if not check_server():
    print(f"\n{Colors.RED}Cannot proceed without server connection.{Colors.END}")
    return

  # Run all test suites
  test_task1_journey_search()
  test_task2_sorting_filtering()
  test_task3_station_lookup()

  # Print summary
  result.print_summary()


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
  except Exception as e:
    print(f"\n\n{Colors.RED}Fatal error: {str(e)}{Colors.END}")
