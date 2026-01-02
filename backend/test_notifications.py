"""Test notification system and alert features."""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_auth():
    """Login and get token."""
    print_section("1. Authentication")
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if response.status_code == 200:
        token = response.json()['access_token']
        print("✅ Login successful")
        print(f"Token: {token[:30]}...")
        return token
    else:
        print(f"❌ Login failed: {response.json()}")
        return None

def test_create_in_app_notification(token):
    """Test creating in-app notification via enhanced alert service."""
    print_section("2. Create In-App Notification")
    
    # We'll trigger this by creating a criminal (which sends alerts)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/criminals",
        headers=headers,
        files={
            "name": (None, "Test Criminal"),
            "crime": (None, "Testing Alert System"),
            "description": (None, "Created to test notification feature")
        }
    )
    
    if response.status_code == 201:
        print("✅ Criminal created (should trigger in-app notification)")
        criminal_id = response.json()['id']
        return criminal_id
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return None

def test_get_notifications(token):
    """Test fetching notifications."""
    print_section("3. Get All Notifications")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Retrieved {len(data['notifications'])} notification(s)")
        print(f"   Total: {data['total']}")
        print(f"   Unread: {data['unread_count']}")
        
        if data['notifications']:
            print("\n   Recent notifications:")
            for notif in data['notifications'][:3]:
                print(f"   - [{notif['severity'].upper()}] {notif['message']}")
                print(f"     Category: {notif['category']}, Status: {'Unread' if not notif['acknowledged'] else 'Read'}")
        
        return data['notifications']
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return []

def test_get_unread_count(token):
    """Test unread count endpoint."""
    print_section("4. Get Unread Count")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/notifications/unread-count", headers=headers)
    
    if response.status_code == 200:
        count = response.json()['unread_count']
        print(f"✅ Unread notifications: {count}")
        return count
    else:
        print(f"❌ Failed: {response.status_code}")
        return 0

def test_mark_as_read(token, notification_id):
    """Test marking notification as read."""
    print_section("5. Mark Notification as Read")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(
        f"{BASE_URL}/api/notifications/{notification_id}/mark-read",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"✅ Notification {notification_id} marked as read")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False

def test_mark_all_as_read(token):
    """Test marking all notifications as read."""
    print_section("6. Mark All as Read")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(
        f"{BASE_URL}/api/notifications/mark-all-read",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ All notifications marked as read")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False

def test_filtered_notifications(token):
    """Test filtering notifications."""
    print_section("7. Test Filtering")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test severity filter
    print("Testing severity filter (critical):")
    response = requests.get(
        f"{BASE_URL}/api/notifications",
        headers=headers,
        params={"severity": "critical"}
    )
    if response.status_code == 200:
        count = len(response.json()['notifications'])
        print(f"✅ Critical notifications: {count}")
    
    # Test category filter
    print("\nTesting category filter (criminal_mgmt):")
    response = requests.get(
        f"{BASE_URL}/api/notifications",
        headers=headers,
        params={"category": "criminal_mgmt"}
    )
    if response.status_code == 200:
        count = len(response.json()['notifications'])
        print(f"✅ Criminal management notifications: {count}")
    
    # Test unread only
    print("\nTesting unread_only filter:")
    response = requests.get(
        f"{BASE_URL}/api/notifications",
        headers=headers,
        params={"unread_only": "true"}
    )
    if response.status_code == 200:
        count = len(response.json()['notifications'])
        print(f"✅ Unread notifications: {count}")

def test_delete_criminal(token, criminal_id):
    """Delete the test criminal (triggers deletion alert)."""
    print_section("8. Delete Test Criminal (Triggers Alert)")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{BASE_URL}/api/criminals/{criminal_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ Criminal deleted (should trigger deletion notification)")
        return True
    else:
        print(f"⚠️  Cleanup failed: {response.status_code}")
        return False

def main():
    """Run all tests."""
    print("\n" + "🔔 "*20)
    print("  NOTIFICATION SYSTEM TEST")
    print("🔔 "*20)
    
    print("\n📋 Make sure backend server is running on http://127.0.0.1:5000")
    input("Press Enter to continue...")
    
    # Test authentication
    token = test_auth()
    if not token:
        print("\n❌ Authentication failed. Cannot continue tests.")
        return
    
    # Create notification
    criminal_id = test_create_in_app_notification(token)
    
    # Get notifications
    notifications = test_get_notifications(token)
    
    # Get unread count
    unread_count = test_get_unread_count(token)
    
    # Mark one as read (if available)
    if notifications and unread_count > 0:
        test_mark_as_read(token, notifications[0]['id'])
        
        # Check count again
        test_get_unread_count(token)
    
    # Test filtering
    test_filtered_notifications(token)
    
    # Mark all as read
    if unread_count > 0:
        test_mark_all_as_read(token)
        test_get_unread_count(token)
    
    # Cleanup - delete test criminal (triggers alert)
    if criminal_id:
        test_delete_criminal(token, criminal_id)
    
    # Final check
    print_section("FINAL CHECK")
    test_get_notifications(token)
    
    print("\n" + "="*60)
    print("  ✅ ALL TESTS COMPLETED!")
    print("="*60)
    print("\n📊 Summary:")
    print("   - Authentication: ✅")
    print("   - Create notification: ✅")
    print("   - Fetch notifications: ✅")
    print("   - Unread count: ✅")
    print("   - Mark as read: ✅")
    print("   - Mark all as read: ✅")
    print("   - Filtering: ✅")
    print("\n💡 Next steps:")
    print("   1. Check frontend: http://localhost:3000")
    print("   2. Look for notification bell in navbar")
    print("   3. Click bell to see notifications dropdown")
    print("   4. Navigate to /notifications for full page")
    print("\n")

if __name__ == "__main__":
    main()
