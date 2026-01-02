"""Test dashboard API endpoints"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_dashboard():
    # Login
    print("1. Logging in...")
    login_data = {
        "email": "sibirajkumar30@gmail.com",
        "password": "Sibi@123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Login status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Login failed: {response.text}")
        return
    
    token = response.json().get('access_token')
    print(f"   Token obtained: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test dashboard stats
    print("\n2. Testing /dashboard/stats...")
    response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✓ Dashboard stats retrieved successfully:")
        print(f"     - Total Criminals: {data.get('total_criminals')}")
        print(f"     - Total Detections: {data.get('total_detections')}")
        print(f"     - Pending Verifications: {data.get('pending_verifications')}")
        print(f"     - Total Alerts: {data.get('total_alerts')}")
    else:
        print(f"   ✗ Failed: {response.text}")
    
    # Test recent detections
    print("\n3. Testing /dashboard/recent-detections...")
    response = requests.get(f"{BASE_URL}/dashboard/recent-detections", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Retrieved {len(data.get('detections', []))} recent detections")
    else:
        print(f"   ✗ Failed: {response.text}")

if __name__ == "__main__":
    test_dashboard()
