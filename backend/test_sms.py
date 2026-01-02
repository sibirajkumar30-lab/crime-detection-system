"""Test SMS configuration and send test message."""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

def test_twilio_config():
    """Test Twilio configuration."""
    print("\n" + "="*60)
    print(" SMS CONFIGURATION TEST")
    print("="*60 + "\n")
    
    # Check environment variables
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    phone_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    print("1. Checking environment variables...")
    if not account_sid:
        print("   ❌ TWILIO_ACCOUNT_SID not found in .env")
        return False
    print(f"   ✅ TWILIO_ACCOUNT_SID: {account_sid[:10]}...")
    
    if not auth_token:
        print("   ❌ TWILIO_AUTH_TOKEN not found in .env")
        return False
    print(f"   ✅ TWILIO_AUTH_TOKEN: {auth_token[:10]}...")
    
    if not phone_number:
        print("   ❌ TWILIO_PHONE_NUMBER not found in .env")
        return False
    print(f"   ✅ TWILIO_PHONE_NUMBER: {phone_number}")
    
    # Try to import twilio
    print("\n2. Checking Twilio library...")
    try:
        from twilio.rest import Client
        print("   ✅ Twilio library installed")
    except ImportError:
        print("   ❌ Twilio library not installed")
        print("   Run: pip install twilio==8.10.0")
        return False
    
    # Try to initialize client
    print("\n3. Initializing Twilio client...")
    try:
        client = Client(account_sid, auth_token)
        print("   ✅ Client initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize client: {str(e)}")
        return False
    
    # Validate account
    print("\n4. Validating Twilio account...")
    try:
        account = client.api.accounts(account_sid).fetch()
        print(f"   ✅ Account Status: {account.status}")
        print(f"   ✅ Account Name: {account.friendly_name}")
    except Exception as e:
        print(f"   ❌ Failed to validate account: {str(e)}")
        return False
    
    # Get admin users with phone numbers
    print("\n5. Checking for users with phone numbers...")
    try:
        from app import create_app, db
        from app.models.user import User
        
        app = create_app()
        with app.app_context():
            users_with_phones = User.query.filter(User.phone.isnot(None)).all()
            
            if not users_with_phones:
                print("   ⚠️  No users have phone numbers configured")
                print("   Add phone numbers to user profiles to receive SMS")
                return True
            
            print(f"   ✅ Found {len(users_with_phones)} user(s) with phone numbers:")
            for user in users_with_phones:
                print(f"      - {user.username} ({user.role}): {user.phone}")
    except Exception as e:
        print(f"   ⚠️  Could not check database: {str(e)}")
    
    # Offer to send test SMS
    print("\n6. Send test SMS?")
    send_test = input("   Send a test SMS to admin users? (y/n): ").lower().strip()
    
    if send_test == 'y':
        try:
            from app import create_app, db
            from app.models.user import User
            from app.services.sms_service import send_sms_alert
            
            app = create_app()
            with app.app_context():
                admins = User.query.filter(
                    User.role == 'admin',
                    User.phone.isnot(None)
                ).all()
                
                if not admins:
                    print("   ⚠️  No admin users with phone numbers found")
                    return True
                
                for admin in admins:
                    print(f"\n   Sending test SMS to {admin.username} ({admin.phone})...")
                    success = send_sms_alert(
                        phone=admin.phone,
                        message="🔔 Test alert from Crime Detection System. SMS notifications are working!",
                        priority=3,
                        alert_data={'test': True}
                    )
                    
                    if success:
                        print(f"   ✅ SMS sent successfully to {admin.phone}")
                    else:
                        print(f"   ❌ Failed to send SMS to {admin.phone}")
        
        except Exception as e:
            print(f"   ❌ Failed to send test SMS: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n" + "="*60)
    print(" SMS CONFIGURATION SUCCESSFUL! ")
    print("="*60 + "\n")
    return True


if __name__ == '__main__':
    success = test_twilio_config()
    sys.exit(0 if success else 1)
