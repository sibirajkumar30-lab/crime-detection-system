"""Test sending alert email to configured recipient"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_criminal_alert():
    print("\n" + "="*60)
    print("  TESTING CRIMINAL ALERT EMAIL")
    print("="*60)
    
    # 1. Login
    print("\n1. Logging in as admin...")
    login_data = {
        "email": "sibirajkumar30@gmail.com",
        "password": "Sibi@123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"   ❌ Login failed: {response.text}")
        return
    
    token = response.json().get('access_token')
    print(f"   ✓ Logged in successfully")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create a test criminal
    print("\n2. Creating test criminal...")
    criminal_data = {
        "name": "Test Alert Criminal",
        "alias": "Alert Test",
        "crime_type": "Testing",
        "description": "Created to test alert email system",
        "status": "wanted"
    }
    
    response = requests.post(f"{BASE_URL}/criminals", json=criminal_data, headers=headers)
    if response.status_code != 201:
        print(f"   ❌ Failed to create criminal: {response.text}")
        return
    
    criminal_id = response.json().get('criminal', {}).get('id')
    print(f"   ✓ Criminal created with ID: {criminal_id}")
    print(f"   📧 Alert email should be sent to: sibirajkumar30@gmail.com")
    
    # 3. Delete the test criminal (triggers another alert)
    print("\n3. Deleting test criminal...")
    response = requests.delete(f"{BASE_URL}/criminals/{criminal_id}", headers=headers)
    if response.status_code != 200:
        print(f"   ❌ Failed to delete criminal: {response.text}")
        return
    
    print(f"   ✓ Criminal deleted")
    print(f"   📧 Deletion alert should be sent to: sibirajkumar30@gmail.com")
    
    print("\n" + "="*60)
    print("  ✅ TEST COMPLETE")
    print("="*60)
    print("\nCheck your inbox at: sibirajkumar30@gmail.com")
    print("(Check spam folder if you don't see the emails)")
    print("\nYou should receive 2 emails:")
    print("  1. '✅ New Criminal Added: Test Alert Criminal'")
    print("  2. '🗑️ Criminal Deleted: Test Alert Criminal'")
    print()

if __name__ == "__main__":
    test_criminal_alert()
