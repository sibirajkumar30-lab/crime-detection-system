"""Comprehensive Testing Script for Crime Detection System - QA Expert Analysis"""

import requests
import json
import sys
from datetime import datetime
import time

BASE_URL = "http://127.0.0.1:5000/api"
BUGS_FOUND = []
WARNINGS_FOUND = []

class TestResult:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.warnings = 0

result = TestResult()

def log_test(name, status, message="", severity="info"):
    """Log test result with color coding."""
    result.total += 1
    
    if status == "PASS":
        result.passed += 1
        print(f"✓ PASS: {name}")
    elif status == "FAIL":
        result.failed += 1
        print(f"✗ FAIL: {name}")
        BUGS_FOUND.append({"test": name, "message": message, "severity": severity})
    elif status == "WARN":
        result.warnings += 1
        print(f"⚠ WARN: {name}")
        WARNINGS_FOUND.append({"test": name, "message": message})
    
    if message:
        print(f"   → {message}")
    print()

def test_server_connectivity():
    """Test 1: Server Connectivity"""
    print("\n" + "="*70)
    print("TEST SUITE 1: SERVER CONNECTIVITY & HEALTH")
    print("="*70 + "\n")
    
    try:
        response = requests.get(f"http://127.0.0.1:5000", timeout=5)
        log_test("Server is running", "PASS" if response.status_code == 200 else "FAIL",
                f"Status: {response.status_code}")
    except Exception as e:
        log_test("Server is running", "FAIL", str(e), "critical")
        return False
    
    # Test CORS headers
    try:
        response = requests.options(f"{BASE_URL}/auth/login")
        if 'Access-Control-Allow-Origin' in response.headers:
            log_test("CORS headers present", "PASS")
        else:
            log_test("CORS headers present", "WARN", 
                    "CORS headers might not be configured for all endpoints")
    except:
        pass
    
    return True

def test_authentication():
    """Test 2: Authentication Flow"""
    print("\n" + "="*70)
    print("TEST SUITE 2: AUTHENTICATION & AUTHORIZATION")
    print("="*70 + "\n")
    
    # Test login with existing user
    login_data = {
        "email": "sibirajkumar30@gmail.com",
        "password": "password123"  # Assuming default password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                log_test("User login successful", "PASS", "Token received")
                return data['access_token']
            else:
                log_test("User login successful", "FAIL", "No access_token in response", "high")
        else:
            log_test("User login with existing user", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text[:200]}", "high")
            
            # Try to create a test user
            print("Attempting to create test user...")
            register_data = {
                "username": f"testuser_{int(time.time())}",
                "email": f"test_{int(time.time())}@test.com",
                "password": "TestPass123!",
                "role": "operator"
            }
            
            reg_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
            if reg_response.status_code == 201:
                # Try login with new user
                login_data = {
                    "email": register_data['email'],
                    "password": register_data['password']
                }
                login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
                if login_response.status_code == 200:
                    return login_response.json()['access_token']
    except Exception as e:
        log_test("Authentication process", "FAIL", str(e), "critical")
        return None
    
    return None

def test_dashboard_api(token):
    """Test 3: Dashboard Analytics"""
    print("\n" + "="*70)
    print("TEST SUITE 3: DASHBOARD & ANALYTICS API")
    print("="*70 + "\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("/dashboard/stats", "GET", "Dashboard Statistics"),
        ("/dashboard/recent-detections", "GET", "Recent Detections"),
        ("/dashboard/top-criminals?limit=5", "GET", "Top Criminals"),
        ("/dashboard/detections-timeline?days=7", "GET", "Detection Timeline"),
        ("/dashboard/detection-status-breakdown", "GET", "Status Breakdown"),
        ("/dashboard/confidence-distribution", "GET", "Confidence Distribution"),
        ("/dashboard/location-stats", "GET", "Location Statistics"),
        ("/dashboard/video-analytics", "GET", "Video Analytics"),
        ("/dashboard/alert-stats", "GET", "Alert Statistics"),
        ("/dashboard/analytics/performance", "GET", "Performance Metrics"),
        ("/dashboard/analytics/activity", "GET", "Criminal Activity Report"),
        ("/dashboard/analytics/patterns", "GET", "Time-based Patterns"),
        ("/dashboard/analytics/locations", "GET", "Location Heatmap"),
        ("/dashboard/analytics/video-stats", "GET", "Video Processing Stats"),
        ("/dashboard/analytics/report?days=30", "GET", "Comprehensive Report"),
    ]
    
    for endpoint, method, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Validate response structure
                if isinstance(data, (dict, list)):
                    log_test(f"API: {name}", "PASS", f"Response size: {len(json.dumps(data))} bytes")
                else:
                    log_test(f"API: {name}", "WARN", "Unexpected response format")
            elif response.status_code == 404:
                log_test(f"API: {name}", "FAIL", "Endpoint not found", "medium")
            elif response.status_code == 500:
                log_test(f"API: {name}", "FAIL", f"Server error: {response.text[:200]}", "high")
            else:
                log_test(f"API: {name}", "FAIL", f"Status: {response.status_code}", "medium")
        except requests.Timeout:
            log_test(f"API: {name}", "FAIL", "Request timeout (>10s)", "medium")
        except Exception as e:
            log_test(f"API: {name}", "FAIL", str(e), "medium")

def test_criminal_management(token):
    """Test 4: Criminal Management"""
    print("\n" + "="*70)
    print("TEST SUITE 4: CRIMINAL MANAGEMENT")
    print("="*70 + "\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all criminals
    try:
        response = requests.get(f"{BASE_URL}/criminals", headers=headers)
        if response.status_code == 200:
            criminals = response.json()
            log_test("Get all criminals", "PASS", f"Found {len(criminals)} criminals")
            
            # Test pagination if many criminals
            if len(criminals) > 10:
                log_test("Large dataset handling", "WARN", 
                        f"{len(criminals)} records without pagination", "low")
            
            # Test individual criminal details if any exist
            if len(criminals) > 0:
                criminal_id = criminals[0]['id']
                detail_response = requests.get(f"{BASE_URL}/criminals/{criminal_id}", headers=headers)
                if detail_response.status_code == 200:
                    log_test("Get criminal details", "PASS")
                else:
                    log_test("Get criminal details", "FAIL", 
                            f"Status: {detail_response.status_code}", "medium")
        else:
            log_test("Get all criminals", "FAIL", f"Status: {response.status_code}", "high")
    except Exception as e:
        log_test("Criminal management API", "FAIL", str(e), "high")

def test_detection_system(token):
    """Test 5: Face Detection System"""
    print("\n" + "="*70)
    print("TEST SUITE 5: FACE DETECTION SYSTEM")
    print("="*70 + "\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test detection history
    try:
        response = requests.get(f"{BASE_URL}/detections", headers=headers)
        if response.status_code == 200:
            detections = response.json()
            log_test("Get detection history", "PASS", f"Found {len(detections)} detections")
            
            # Validate detection structure
            if len(detections) > 0:
                detection = detections[0]
                required_fields = ['id', 'criminal_id', 'detected_at', 'confidence_score']
                missing_fields = [f for f in required_fields if f not in detection]
                if missing_fields:
                    log_test("Detection data structure", "FAIL", 
                            f"Missing fields: {missing_fields}", "medium")
                else:
                    log_test("Detection data structure", "PASS")
                    
                    # Validate confidence score range
                    conf = detection.get('confidence_score', 0)
                    if 0 <= conf <= 1:
                        log_test("Confidence score validation", "PASS", f"Score: {conf:.3f}")
                    else:
                        log_test("Confidence score validation", "FAIL", 
                                f"Invalid score: {conf}", "medium")
        elif response.status_code == 404:
            log_test("Get detection history", "FAIL", "Endpoint not found", "high")
        else:
            log_test("Get detection history", "FAIL", f"Status: {response.status_code}", "medium")
    except Exception as e:
        log_test("Detection system API", "FAIL", str(e), "high")

def test_video_detection(token):
    """Test 6: Video Detection"""
    print("\n" + "="*70)
    print("TEST SUITE 6: VIDEO DETECTION SYSTEM")
    print("="*70 + "\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get video list
    try:
        response = requests.get(f"{BASE_URL}/videos", headers=headers)
        if response.status_code == 200:
            videos = response.json()
            log_test("Get video list", "PASS", f"Found {len(videos)} videos")
            
            # Test individual video details if any exist
            if len(videos) > 0:
                video_id = videos[0]['id']
                detail_response = requests.get(f"{BASE_URL}/videos/{video_id}", headers=headers)
                if detail_response.status_code == 200:
                    video_data = detail_response.json()
                    log_test("Get video details", "PASS")
                    
                    # Validate video metadata
                    required_fields = ['id', 'video_filename', 'processing_status']
                    missing = [f for f in required_fields if f not in video_data]
                    if missing:
                        log_test("Video metadata completeness", "FAIL", 
                                f"Missing: {missing}", "low")
                    else:
                        log_test("Video metadata completeness", "PASS")
                else:
                    log_test("Get video details", "FAIL", 
                            f"Status: {detail_response.status_code}", "medium")
        else:
            log_test("Get video list", "FAIL", f"Status: {response.status_code}", "medium")
    except Exception as e:
        log_test("Video detection API", "FAIL", str(e), "high")

def test_security(token):
    """Test 7: Security & Authorization"""
    print("\n" + "="*70)
    print("TEST SUITE 7: SECURITY & AUTHORIZATION")
    print("="*70 + "\n")
    
    # Test endpoints without token
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
                log_test(f"Protected endpoint: {endpoint}", "PASS", "Requires authentication")
            else:
                log_test(f"Protected endpoint: {endpoint}", "FAIL", 
                        f"Should return 401, got {response.status_code}", "critical")
        except Exception as e:
            log_test(f"Protected endpoint: {endpoint}", "FAIL", str(e), "high")
    
    # Test with invalid token
    headers = {"Authorization": "Bearer invalid_token_xyz"}
    response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
    if response.status_code == 422:
        log_test("Invalid token rejection", "PASS")
    else:
        log_test("Invalid token rejection", "WARN", f"Status: {response.status_code}")

def test_data_validation():
    """Test 8: Input Validation"""
    print("\n" + "="*70)
    print("TEST SUITE 8: INPUT VALIDATION & ERROR HANDLING")
    print("="*70 + "\n")
    
    # Test registration with invalid data
    invalid_registrations = [
        ({}, "Empty payload"),
        ({"username": "test"}, "Missing required fields"),
        ({"username": "a", "email": "test@test.com", "password": "123"}, "Weak password"),
    ]
    
    for data, description in invalid_registrations:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        if response.status_code in [400, 422]:
            log_test(f"Registration validation: {description}", "PASS")
        else:
            log_test(f"Registration validation: {description}", "FAIL", 
                    f"Should return 400/422, got {response.status_code}", "medium")
    
    # Test login with invalid data
    response = requests.post(f"{BASE_URL}/auth/login", json={})
    if response.status_code == 400:
        log_test("Login validation: Empty payload", "PASS")
    else:
        log_test("Login validation: Empty payload", "FAIL", 
                f"Should return 400, got {response.status_code}", "medium")

def print_summary():
    """Print comprehensive test summary and bug report"""
    print("\n" + "="*70)
    print("QA TEST SUMMARY")
    print("="*70 + "\n")
    
    print(f"Total Tests Run: {result.total}")
    print(f"✓ Passed: {result.passed} ({result.passed/result.total*100:.1f}%)")
    print(f"✗ Failed: {result.failed} ({result.failed/result.total*100:.1f}%)")
    print(f"⚠ Warnings: {result.warnings} ({result.warnings/result.total*100:.1f}%)")
    
    # Bugs by severity
    if BUGS_FOUND:
        print("\n" + "="*70)
        print("BUGS FOUND (By Severity)")
        print("="*70 + "\n")
        
        critical = [b for b in BUGS_FOUND if b.get('severity') == 'critical']
        high = [b for b in BUGS_FOUND if b.get('severity') == 'high']
        medium = [b for b in BUGS_FOUND if b.get('severity') == 'medium']
        low = [b for b in BUGS_FOUND if b.get('severity') == 'low']
        
        if critical:
            print(f"🔴 CRITICAL ({len(critical)}):")
            for bug in critical:
                print(f"  - {bug['test']}: {bug['message']}")
        
        if high:
            print(f"\n🟠 HIGH ({len(high)}):")
            for bug in high:
                print(f"  - {bug['test']}: {bug['message']}")
        
        if medium:
            print(f"\n🟡 MEDIUM ({len(medium)}):")
            for bug in medium:
                print(f"  - {bug['test']}: {bug['message']}")
        
        if low:
            print(f"\n🟢 LOW ({len(low)}):")
            for bug in low:
                print(f"  - {bug['test']}: {bug['message']}")
    
    if WARNINGS_FOUND:
        print("\n" + "="*70)
        print("WARNINGS & RECOMMENDATIONS")
        print("="*70 + "\n")
        for warn in WARNINGS_FOUND:
            print(f"  ⚠ {warn['test']}: {warn['message']}")
    
    # Save detailed report
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total': result.total,
            'passed': result.passed,
            'failed': result.failed,
            'warnings': result.warnings
        },
        'bugs': BUGS_FOUND,
        'warnings': WARNINGS_FOUND
    }
    
    with open('qa_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✓ Detailed report saved to: qa_test_report.json")

def main():
    """Main test execution"""
    print("\n" + "="*70)
    print("CRIME DETECTION SYSTEM - COMPREHENSIVE QA TESTING")
    print("="*70)
    print(f"Testing Target: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Run all test suites
    if not test_server_connectivity():
        print("\n❌ Server not accessible. Aborting tests.")
        return
    
    token = test_authentication()
    if not token:
        print("\n❌ Authentication failed. Some tests will be skipped.")
        test_data_validation()
        print_summary()
        return
    
    # Run authenticated tests
    test_dashboard_api(token)
    test_criminal_management(token)
    test_detection_system(token)
    test_video_detection(token)
    test_security(token)
    test_data_validation()
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    main()
