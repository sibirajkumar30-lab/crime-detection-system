"""Quick test to verify alert email recipient"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("\n" + "="*60)
print("  EMAIL CONFIGURATION CHECK")
print("="*60)

smtp_email = os.getenv('SMTP_EMAIL')
alert_email = os.getenv('ALERT_EMAIL')
smtp_password = os.getenv('SMTP_PASSWORD')

print(f"\n✓ Email FROM (sender): {smtp_email}")
print(f"✓ Email TO (recipient): {alert_email}")
print(f"✓ SMTP Password: {'*' * len(smtp_password) if smtp_password else 'NOT SET'}")

if not alert_email:
    print("\n❌ ERROR: ALERT_EMAIL not configured in .env")
    print("   Emails will be sent to sender address instead!")
elif alert_email == smtp_email:
    print("\n⚠️  WARNING: ALERT_EMAIL is same as SMTP_EMAIL")
    print("   You'll send emails to yourself!")
else:
    print(f"\n✅ Configuration looks good!")
    print(f"   Alerts will be sent to: {alert_email}")

print("\n" + "="*60 + "\n")
