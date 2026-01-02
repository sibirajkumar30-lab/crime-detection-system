"""Test criminal alert service"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_criminal_alerts():
    # Login
    print("1. Logging in as admin...")
    login_data = {
        "email": "sibirajkumar30@gmail.com",
        "password": "Sibi@123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"   Login failed: {response.text}")
        return
    
    token = response.json().get('access_token')
    print(f"   ✓ Logged in successfully")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test criminal
    print("\n2. Creating a test criminal...")
    criminal_data = {
        "name": "Test Alert Criminal",
        "age": 30,
        "gender": "Male",
        "crime_type": "Testing",
        "description": "This is a test criminal for alert testing",
        "status": "wanted",
        "last_known_location": "Test Location"
    }
    
    response = requests.post(f"{BASE_URL}/criminals", json=criminal_data, headers=headers)
    if response.status_code not in [200, 201]:
        print(f"   Failed to create criminal: {response.text}")
        return
    
    response_data = response.json()
    criminal_id = response_data.get('criminal', {}).get('id') or response_data.get('id')
    print(f"   ✓ Criminal created with ID: {criminal_id}")
    print(f"   Response: {response_data}")
    print(f"   📧 Check email at sibirajkumar30@gmail.com for 'New Criminal Added' alert")
    
    input("\n   Press Enter after checking email to continue with deletion test...")
    
    # Delete the criminal
    print("\n3. Deleting the test criminal...")
    response = requests.delete(f"{BASE_URL}/criminals/{criminal_id}", headers=headers)
    if response.status_code != 200:
        print(f"   Failed to delete criminal: {response.text}")
        return
    
    print(f"   ✓ Criminal deleted successfully")
    print(f"   📧 Check email at sibirajkumar30@gmail.com for 'Criminal Deleted' alert")
    
    print("\n✅ Test completed!")
    print("You should have received 2 emails:")
    print("  1. 'New Criminal Added' (green theme)")
    print("  2. 'Criminal Deleted from Database' (red theme)")

if __name__ == "__main__":
    test_criminal_alerts()
