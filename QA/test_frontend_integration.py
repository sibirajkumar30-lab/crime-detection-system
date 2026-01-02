"""
Frontend Integration Testing
Tests all API endpoints that the React frontend uses
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000/api"
CREDENTIALS = {"email": "sibirajkumar30@gmail.com", "password": "1234"}

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

results = []
token = None

def log(test_id, name, status, message=""):
    """Log test result"""
    symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⊘"
    color = GREEN if status == "PASS" else RED if status == "FAIL" else YELLOW
    print(f"{color}{symbol} {test_id}: {name}{RESET}")
    if message:
        print(f"  {color}└─ {message}{RESET}")
    results.append({"id": test_id, "name": name, "status": status, "message": message})

print(f"\n{BLUE}{'='*80}")
print("  FRONTEND INTEGRATION TESTING")
print(f"{'='*80}{RESET}\n")
print(f"Backend: {BASE_URL}")
print(f"Frontend: http://localhost:3000")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# AUTHENTICATION
# ============================================================================
print(f"\n{BLUE}[1] AUTHENTICATION TESTS{RESET}\n")

try:
    response = requests.post(f"{BASE_URL}/auth/login", json=CREDENTIALS, timeout=10)
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        user = data.get('user', {})
        log("AUTH-01", "Login with valid credentials", "PASS", 
            f"User: {user.get('username')} ({user.get('role')})")
    else:
        log("AUTH-01", "Login with valid credentials", "FAIL", 
            f"Status {response.status_code}")
except Exception as e:
    log("AUTH-01", "Login with valid credentials", "FAIL", str(e))

if not token:
    print(f"\n{RED}✗ Cannot proceed without authentication token{RESET}\n")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.post(f"{BASE_URL}/auth/login", 
                           json={"email": "wrong@test.com", "password": "wrong"}, 
                           timeout=10)
    if response.status_code in [401, 422]:
        log("AUTH-02", "Reject invalid credentials", "PASS")
    else:
        log("AUTH-02", "Reject invalid credentials", "FAIL", 
            f"Expected 401/422, got {response.status_code}")
except Exception as e:
    log("AUTH-02", "Reject invalid credentials", "FAIL", str(e))

try:
    response = requests.get(f"{BASE_URL}/dashboard/stats", timeout=10)
    if response.status_code in [401, 422]:
        log("AUTH-03", "Block unauthorized access", "PASS")
    else:
        log("AUTH-03", "Block unauthorized access", "FAIL", 
            f"Expected 401/422, got {response.status_code}")
except Exception as e:
    log("AUTH-03", "Block unauthorized access", "FAIL", str(e))

# ============================================================================
# DASHBOARD
# ============================================================================
print(f"\n{BLUE}[2] DASHBOARD TESTS{RESET}\n")

try:
    response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        required = ['total_criminals', 'total_detections', 'pending_verifications', 'total_alerts']
        missing = [k for k in required if k not in data]
        if not missing:
            log("DASH-01", "Get dashboard statistics", "PASS", 
                f"{data['total_criminals']} criminals, {data['total_detections']} detections")
        else:
            log("DASH-01", "Get dashboard statistics", "FAIL", f"Missing: {missing}")
    else:
        log("DASH-01", "Get dashboard statistics", "FAIL", f"Status {response.status_code}")
except Exception as e:
    log("DASH-01", "Get dashboard statistics", "FAIL", str(e))

try:
    response = requests.get(f"{BASE_URL}/dashboard/recent-detections", 
                           headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if 'detections' in data:
            log("DASH-02", "Get recent detections", "PASS", f"{len(data['detections'])} items")
        else:
            log("DASH-02", "Get recent detections", "FAIL", "Missing 'detections' key")
    else:
        log("DASH-02", "Get recent detections", "FAIL", f"Status {response.status_code}")
except Exception as e:
    log("DASH-02", "Get recent detections", "FAIL", str(e))

# ============================================================================
# ANALYTICS
# ============================================================================
print(f"\n{BLUE}[3] ANALYTICS TESTS{RESET}\n")

analytics_endpoints = [
    ("ANLY-01", "analytics/report", "Get analytics report"),
    ("ANLY-02", "detections-timeline?days=7", "Get 7-day detection timeline"),
    ("ANLY-03", "top-criminals?limit=10", "Get top 10 criminals"),
    ("ANLY-04", "location-stats?limit=10", "Get location statistics"),
    ("ANLY-05", "analytics/patterns", "Get detection patterns"),
    ("ANLY-06", "detection-status-breakdown", "Get status breakdown"),
    ("ANLY-07", "alert-stats", "Get alert statistics"),
    ("ANLY-08", "confidence-distribution", "Get confidence distribution"),
]

for test_id, endpoint, name in analytics_endpoints:
    try:
        url = f"{BASE_URL}/dashboard/{endpoint}"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            log(test_id, name, "PASS")
        else:
            log(test_id, name, "FAIL", f"Status {response.status_code}")
    except Exception as e:
        log(test_id, name, "FAIL", str(e))

# ============================================================================
# CRIMINAL MANAGEMENT
# ============================================================================
print(f"\n{BLUE}[4] CRIMINAL MANAGEMENT TESTS{RESET}\n")

try:
    response = requests.get(f"{BASE_URL}/criminals", headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if 'criminals' in data and isinstance(data['criminals'], list):
            log("CRIM-01", "Get all criminals", "PASS", f"{len(data['criminals'])} criminals found")
        else:
            log("CRIM-01", "Get all criminals", "FAIL", "Missing 'criminals' key or not a list")
    else:
        log("CRIM-01", "Get all criminals", "FAIL", f"Status {response.status_code}")
except Exception as e:
    log("CRIM-01", "Get all criminals", "FAIL", str(e))

try:
    response = requests.get(f"{BASE_URL}/criminals?search=test&status=active", 
                           headers=headers, timeout=10)
    if response.status_code == 200:
        log("CRIM-02", "Search and filter criminals", "PASS")
    else:
        log("CRIM-02", "Search and filter criminals", "FAIL", f"Status {response.status_code}")
except Exception as e:
    log("CRIM-02", "Search and filter criminals", "FAIL", str(e))

# ============================================================================
# DETECTION LOGS
# ============================================================================
print(f"\n{BLUE}[5] DETECTION LOGS TESTS{RESET}\n")

try:
    response = requests.get(f"{BASE_URL}/detection/logs", headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if 'detections' in data:
            log("DETECT-01", "Get detection logs", "PASS", f"{len(data['detections'])} logs")
        else:
            log("DETECT-01", "Get detection logs", "FAIL", "Missing 'detections' key")
    else:
        log("DETECT-01", "Get detection logs", "FAIL", f"Status {response.status_code}")
except Exception as e:
    log("DETECT-01", "Get detection logs", "FAIL", str(e))

try:
    response = requests.get(f"{BASE_URL}/detection/logs?status=Confirmed&page=1&per_page=10", 
                           headers=headers, timeout=10)
    if response.status_code == 200:
        log("DETECT-02", "Filter detection logs", "PASS")
    else:
        log("DETECT-02", "Filter detection logs", "FAIL", f"Status {response.status_code}")
except Exception as e:
    log("DETECT-02", "Filter detection logs", "FAIL", str(e))

# ============================================================================
# VIDEO DETECTION
# ============================================================================
print(f"\n{BLUE}[6] VIDEO DETECTION TESTS{RESET}\n")

try:
    response = requests.get(f"{BASE_URL}/video/list", headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if 'videos' in data:
            log("VIDEO-01", "Get video detections", "PASS", f"{len(data['videos'])} videos")
        else:
            log("VIDEO-01", "Get video detections", "FAIL", "Missing 'videos' key")
    else:
        log("VIDEO-01", "Get video detections", "FAIL", f"Status {response.status_code}")
except Exception as e:
    log("VIDEO-01", "Get video detections", "FAIL", str(e))

try:
    response = requests.get(f"{BASE_URL}/video/list?status=completed", 
                           headers=headers, timeout=10)
    if response.status_code == 200:
        log("VIDEO-02", "Filter videos by status", "PASS")
    else:
        log("VIDEO-02", "Filter videos by status", "FAIL", f"Status {response.status_code}")
except Exception as e:
    log("VIDEO-02", "Filter videos by status", "FAIL", str(e))

# ============================================================================
# TEST SUITE 7: ALERTS (via Dashboard)
# ============================================================================
print(f"\n{BLUE}[7] ALERTS TESTS{RESET}\n")

try:
    response = requests.get(f"{BASE_URL}/dashboard/alert-stats", 
                           headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if 'status_breakdown' in data or 'timeline' in data:
            log("ALERT-01", "Get alert statistics", "PASS")
        else:
            log("ALERT-01", "Get alert statistics", "FAIL", "Missing expected keys")
    else:
        log("ALERT-01", "Get alert statistics", "FAIL", f"Status {response.status_code}")
except Exception as e:
    log("ALERT-01", "Get alert statistics", "FAIL", str(e))

# ============================================================================
# SUMMARY
# ============================================================================
print(f"\n{BLUE}{'='*80}")
print("  TEST SUMMARY")
print(f"{'='*80}{RESET}\n")

total = len(results)
passed = sum(1 for r in results if r['status'] == 'PASS')
failed = sum(1 for r in results if r['status'] == 'FAIL')
pass_rate = (passed / total * 100) if total > 0 else 0

print(f"Total Tests:  {total}")
print(f"{GREEN}✓ Passed:     {passed} ({pass_rate:.1f}%){RESET}")
print(f"{RED}✗ Failed:     {failed}{RESET}")

if failed > 0:
    print(f"\n{RED}Failed Tests:{RESET}")
    for r in results:
        if r['status'] == 'FAIL':
            print(f"  {RED}• {r['id']}: {r['name']}{RESET}")
            if r['message']:
                print(f"    {RED}└─ {r['message']}{RESET}")

# Save report
report = {
    "timestamp": datetime.now().isoformat(),
    "summary": {"total": total, "passed": passed, "failed": failed, "pass_rate": pass_rate},
    "results": results
}

with open("QA/frontend_integration_report.json", 'w') as f:
    json.dump(report, f, indent=2)

print(f"\n{GREEN}✓ Report saved: QA/frontend_integration_report.json{RESET}\n")

exit(0 if failed == 0 else 1)
