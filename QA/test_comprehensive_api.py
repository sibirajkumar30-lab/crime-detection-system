"""Comprehensive API testing for Crime Detection System."""

import requests
import json
from datetime import datetime
import os

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_RESULTS = []

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_result(test_name, passed, message="", response=None):
    """Log test result."""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} - {test_name}")
    if message:
        print(f"    {message}")
    if response and not passed:
        print(f"    Status: {response.status_code}")
        try:
            print(f"    Response: {response.json()}")
        except:
            print(f"    Response: {response.text[:200]}")
    
    TEST_RESULTS.append({
        'test': test_name,
        'passed': passed,
        'message': message,
        'status_code': response.status_code if response else None
    })
    print()

def test_health_check():
    """Test if server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        log_result("Server Health Check", response.status_code == 200, 
                   f"Server is {'UP' if response.status_code == 200 else 'DOWN'}", response)
        return response.status_code == 200
    except Exception as e:
        log_result("Server Health Check", False, f"Error: {str(e)}")
        return False

def test_authentication():
    """Test authentication endpoints."""
    print(f"\n{Colors.BLUE}=== Testing Authentication ==={Colors.END}\n")
    
    # Test registration (might fail if user exists - that's okay)
    test_user = {
        "username": f"testuser_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
        "password": "TestPass123!",
        "role": "operator"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        if response.status_code == 201:
            log_result("User Registration", True, "New user created successfully", response)
        elif response.status_code == 409:
            log_result("User Registration", True, "User already exists (expected)", response)
            # Try with existing test user
            test_user["username"] = "testuser"
            test_user["email"] = "test@test.com"
        else:
            log_result("User Registration", False, f"Unexpected status code", response)
    except Exception as e:
        log_result("User Registration", False, f"Error: {str(e)}")
        return None
    
    # Test login
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            log_result("User Login", True, "Login successful, token received", response)
            return token
        else:
            # Try with default test user
            login_data["username"] = "testuser"
            login_data["password"] = "password123"
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                token = response.json().get('access_token')
                log_result("User Login", True, "Login with default user successful", response)
                return token
            else:
                log_result("User Login", False, "Login failed", response)
                return None
    except Exception as e:
        log_result("User Login", False, f"Error: {str(e)}")
        return None

def test_dashboard_endpoints(token):
    """Test dashboard API endpoints."""
    print(f"\n{Colors.BLUE}=== Testing Dashboard Endpoints ==={Colors.END}\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("/dashboard/stats", "Dashboard Statistics"),
        ("/dashboard/recent-detections", "Recent Detections"),
        ("/dashboard/top-criminals?limit=5", "Top Criminals"),
        ("/dashboard/detections-timeline?days=7", "Detection Timeline"),
        ("/dashboard/detection-status-breakdown", "Status Breakdown"),
        ("/dashboard/confidence-distribution", "Confidence Distribution"),
        ("/dashboard/location-stats?limit=10", "Location Stats"),
        ("/dashboard/video-analytics", "Video Analytics"),
        ("/dashboard/alert-stats", "Alert Stats"),
        ("/dashboard/analytics/performance", "Performance Metrics"),
        ("/dashboard/analytics/activity", "Criminal Activity"),
        ("/dashboard/analytics/patterns", "Time Patterns"),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                log_result(name, True, f"Data received: {len(str(data))} bytes")
            else:
                log_result(name, False, f"Status: {response.status_code}", response)
        except Exception as e:
            log_result(name, False, f"Error: {str(e)}")

def test_criminal_endpoints(token):
    """Test criminal management endpoints."""
    print(f"\n{Colors.BLUE}=== Testing Criminal Management ==={Colors.END}\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test get all criminals
    try:
        response = requests.get(f"{BASE_URL}/criminals", headers=headers)
        if response.status_code == 200:
            criminals = response.json()
            log_result("Get All Criminals", True, f"Found {len(criminals)} criminals")
            return criminals
        else:
            log_result("Get All Criminals", False, "", response)
            return []
    except Exception as e:
        log_result("Get All Criminals", False, f"Error: {str(e)}")
        return []

def test_detection_endpoints(token):
    """Test face detection endpoints."""
    print(f"\n{Colors.BLUE}=== Testing Face Detection ==={Colors.END}\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test detection history
    try:
        response = requests.get(f"{BASE_URL}/detections", headers=headers)
        if response.status_code == 200:
            detections = response.json()
            log_result("Get Detection History", True, f"Found {len(detections)} detections")
        else:
            log_result("Get Detection History", False, "", response)
    except Exception as e:
        log_result("Get Detection History", False, f"Error: {str(e)}")

def test_video_endpoints(token):
    """Test video detection endpoints."""
    print(f"\n{Colors.BLUE}=== Testing Video Detection ==={Colors.END}\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test get all videos
    try:
        response = requests.get(f"{BASE_URL}/videos", headers=headers)
        if response.status_code == 200:
            videos = response.json()
            log_result("Get All Videos", True, f"Found {len(videos)} videos")
        else:
            log_result("Get All Videos", False, "", response)
    except Exception as e:
        log_result("Get All Videos", False, f"Error: {str(e)}")

def test_alert_endpoints(token):
    """Test alert endpoints."""
    print(f"\n{Colors.BLUE}=== Testing Alert System ==={Colors.END}\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test get alerts (if endpoint exists)
    try:
        response = requests.get(f"{BASE_URL}/alerts", headers=headers)
        if response.status_code == 200:
            alerts = response.json()
            log_result("Get All Alerts", True, f"Found {len(alerts)} alerts")
        elif response.status_code == 404:
            log_result("Get All Alerts", True, "Endpoint not implemented (expected)")
        else:
            log_result("Get All Alerts", False, "", response)
    except Exception as e:
        log_result("Get All Alerts", False, f"Error: {str(e)}")

def test_unauthorized_access():
    """Test that endpoints require authentication."""
    print(f"\n{Colors.BLUE}=== Testing Security (Unauthorized Access) ==={Colors.END}\n")
    
    protected_endpoints = [
        "/dashboard/stats",
        "/criminals",
        "/detections",
        "/videos"
    ]
    
    for endpoint in protected_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                log_result(f"Protected: {endpoint}", True, "Correctly requires authentication")
            else:
                log_result(f"Protected: {endpoint}", False, 
                          f"Should return 401, got {response.status_code}", response)
        except Exception as e:
            log_result(f"Protected: {endpoint}", False, f"Error: {str(e)}")

def print_summary():
    """Print test summary."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    total = len(TEST_RESULTS)
    passed = sum(1 for r in TEST_RESULTS if r['passed'])
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {failed}{Colors.END}")
    print(f"Success Rate: {(passed/total*100):.1f}%\n")
    
    if failed > 0:
        print(f"{Colors.RED}Failed Tests:{Colors.END}")
        for result in TEST_RESULTS:
            if not result['passed']:
                print(f"  ✗ {result['test']}")
                if result['message']:
                    print(f"    {result['message']}")
        print()

def main():
    """Run all tests."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}CRIME DETECTION SYSTEM - COMPREHENSIVE API TESTING{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    print(f"Testing API at: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Test if server is up
    if not test_health_check():
        print(f"\n{Colors.RED}Server is not responding. Please start the backend server.{Colors.END}\n")
        return
    
    # Test authentication and get token
    token = test_authentication()
    if not token:
        print(f"\n{Colors.RED}Authentication failed. Cannot proceed with authenticated tests.{Colors.END}\n")
        print_summary()
        return
    
    # Test all endpoints
    test_dashboard_endpoints(token)
    test_criminal_endpoints(token)
    test_detection_endpoints(token)
    test_video_endpoints(token)
    test_alert_endpoints(token)
    test_unauthorized_access()
    
    # Print summary
    print_summary()
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(TEST_RESULTS, f, indent=2)
    print(f"{Colors.GREEN}Test results saved to test_results.json{Colors.END}\n")

if __name__ == "__main__":
    main()
