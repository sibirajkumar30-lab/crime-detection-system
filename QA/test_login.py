"""Frontend & Integration Testing Script"""
import requests
import json

# Test credentials
EMAIL = "sibirajkumar30@gmail.com"
PASSWORD = "1234"
BASE_URL = "http://127.0.0.1:5000/api"

print("="*70)
print("FRONTEND INTEGRATION TESTING")
print("="*70)
print()

# Test 1: Login
print("Test 1: User Login")
response = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    token = data.get('access_token')
    user = data.get('user', {})
    print(f"✓ Login successful!")
    print(f"  Token: {token[:50]}...")
    print(f"  User: {user.get('username')} ({user.get('role')})")
    print(f"  Email: {user.get('email')}")
    
    # Save token for frontend testing
    with open('test_token.txt', 'w') as f:
        f.write(token)
    print(f"\n✓ Token saved to test_token.txt")
    print(f"\nYou can now use this token in frontend by:")
    print(f"  localStorage.setItem('token', '{token[:20]}...')")
else:
    print(f"✗ Login failed: {response.text}")
