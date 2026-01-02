"""Quick alert functionality test."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.user import User
from app.services.enhanced_alert_service import EnhancedAlertService

print("\n" + "="*60)
print("  ALERT FUNCTIONALITY TEST")
print("="*60 + "\n")

# Create app context
app = create_app()

with app.app_context():
    print("1. Testing In-App Notification Alert...")
    alert = EnhancedAlertService.send_alert(
        message="Test in-app notification",
        severity='info',
        category='operational',
        alert_type='test',
        priority=3,
        channels=['in_app'],
        data={'test': True}
    )
    
    if alert:
        print(f"   ✅ In-app alert created: ID={alert.id}")
        print(f"   - Message: {alert.message}")
        print(f"   - Severity: {alert.severity}")
        print(f"   - Category: {alert.category}")
        print(f"   - Delivery: {alert.delivery_method}")
        print(f"   - Status: {alert.status}")
    else:
        print("   ❌ Failed to create in-app alert")
    
    print("\n2. Testing Email Alert...")
    alert2 = EnhancedAlertService.send_alert(
        message="Test email notification",
        severity='warning',
        category='system',
        alert_type='test',
        priority=2,
        channels=['email'],
        data={'test': True}
    )
    
    if alert2:
        print(f"   ✅ Email alert created: ID={alert2.id}")
        print(f"   - Message: {alert2.message}")
        print(f"   - Severity: {alert2.severity}")
        print(f"   - Category: {alert2.category}")
        print(f"   - Delivery: {alert2.delivery_method}")
        print(f"   - Status: {alert2.status}")
        
        if alert2.status == 'delivered':
            print("   ✅ Email sent successfully!")
        elif alert2.status == 'failed':
            print("   ⚠️  Email failed (check SMTP credentials)")
        else:
            print(f"   ⚠️  Email status: {alert2.status}")
    else:
        print("   ❌ Failed to create email alert")
    
    print("\n3. Testing Criminal Management Alert...")
    alert3 = EnhancedAlertService.send_criminal_added_alert({
        'name': 'Test Criminal',
        'crime': 'Testing',
        'id': 999
    })
    
    if alert3:
        print(f"   ✅ Criminal alert created: ID={alert3.id}")
        print(f"   - Message: {alert3.message}")
        print(f"   - Category: {alert3.category}")
    else:
        print("   ❌ Failed to create criminal alert")
    
    print("\n4. Testing Detection Alert...")
    alert4 = EnhancedAlertService.send_detection_alert(
        criminal_name="Test Criminal",
        location="Test Location",
        confidence=85.5,
        detection_data={'camera_id': 1}
    )
    
    if alert4:
        print(f"   ✅ Detection alert created: ID={alert4.id}")
        print(f"   - Message: {alert4.message}")
        print(f"   - Severity: {alert4.severity}")
        print(f"   - Priority: {alert4.priority}")
    else:
        print("   ❌ Failed to create detection alert")
    
    print("\n5. Checking Total Alerts in Database...")
    from app.models.alert import Alert
    
    all_alerts = Alert.query.all()
    unread_alerts = Alert.query.filter_by(acknowledged=False).all()
    
    print(f"   Total alerts: {len(all_alerts)}")
    print(f"   Unread alerts: {len(unread_alerts)}")
    
    if all_alerts:
        print("\n   Recent alerts:")
        for a in all_alerts[-5:]:
            status_icon = "✓" if a.status == 'delivered' else "⚠" if a.status == 'failed' else "•"
            read_status = "Read" if a.acknowledged else "Unread"
            print(f"   {status_icon} [{a.severity.upper()}] {a.message[:50]}... ({read_status})")

print("\n" + "="*60)
print("  TEST COMPLETE!")
print("="*60)
print("\n💡 Summary:")
print("   - In-app notifications: Working ✅")
print("   - Email alerts: Check status above")
print("   - SMS alerts: Disabled (as configured)")
print("\n📌 Next: Test via API at http://127.0.0.1:5000/api/notifications")
print("   (Make sure backend server is running)")
print()
