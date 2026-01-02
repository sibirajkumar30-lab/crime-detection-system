"""Direct test of criminal alert service"""
from app import create_app, db
from app.models.criminal import Criminal
from app.models.user import User
from app.services.criminal_alert_service import send_criminal_deleted_alert

app = create_app()

with app.app_context():
    # Get admin user
    admin = User.query.filter_by(email='sibirajkumar30@gmail.com').first()
    
    if not admin:
        print("❌ Admin user not found")
        exit(1)
    
    # Create test criminal data
    test_criminal = {
        'id': 999,
        'name': 'Direct Test Criminal',
        'crime_type': 'Testing',
        'status': 'wanted',
        'description': 'Testing direct alert service',
        'added_date': '2025-12-26'
    }
    
    print("📧 Sending test deletion alert...")
    print(f"   To: {admin.email}")
    print(f"   Criminal: {test_criminal['name']}")
    
    result = send_criminal_deleted_alert(test_criminal, admin)
    
    if result:
        print("\n✅ Alert sent successfully!")
        print(f"   Check email at: {admin.email}")
    else:
        print("\n❌ Alert failed to send")
        print("   Check SMTP credentials in .env file")
