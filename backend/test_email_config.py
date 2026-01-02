"""
Test Email Configuration
Run this to verify your SMTP settings work before using the system.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_config():
    """Test SMTP email configuration."""
    
    print("\n" + "="*60)
    print("  TESTING EMAIL CONFIGURATION")
    print("="*60 + "\n")
    
    # Get credentials from environment
    sender_email = os.getenv('SMTP_EMAIL')
    sender_password = os.getenv('SMTP_PASSWORD')
    recipient_email = os.getenv('ALERT_EMAIL', sender_email)
    
    # Validate credentials exist
    print("Step 1: Checking environment variables...")
    if not sender_email:
        print("❌ SMTP_EMAIL not found in .env file")
        return False
    else:
        print(f"✓ SMTP_EMAIL: {sender_email}")
    
    if not sender_password:
        print("❌ SMTP_PASSWORD not found in .env file")
        return False
    else:
        print(f"✓ SMTP_PASSWORD: {'*' * len(sender_password)} (hidden)")
    
    if recipient_email:
        print(f"✓ ALERT_EMAIL: {recipient_email}")
    
    # Try to send test email
    print("\nStep 2: Connecting to SMTP server...")
    try:
        # Create test message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = '✅ Test Email - Crime Detection System'
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #28a745; color: white; padding: 20px; text-align: center;">
                <h1>✅ Email Configuration Successful!</h1>
            </div>
            <div style="padding: 20px;">
                <p>Congratulations! Your SMTP email configuration is working correctly.</p>
                
                <h2>Configuration Details:</h2>
                <ul>
                    <li><strong>From:</strong> {sender_email}</li>
                    <li><strong>To:</strong> {recipient_email}</li>
                    <li><strong>SMTP Server:</strong> smtp.gmail.com:587</li>
                    <li><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                </ul>
                
                <p style="padding: 15px; background-color: #d4edda; border-left: 4px solid #28a745;">
                    <strong>✓ Your Crime Detection System is ready to send alerts!</strong>
                </p>
                
                <h3>Next Steps:</h3>
                <ol>
                    <li>Start your backend server</li>
                    <li>Add, update, or delete a criminal</li>
                    <li>Check this email address for alert notifications</li>
                </ol>
            </div>
            <div style="background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666;">
                <p>This is a test email from Crime Detection System</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        print(f"✓ Connecting to smtp.gmail.com:587...")
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=10) as server:
            print("✓ Starting TLS encryption...")
            server.starttls()
            
            print("✓ Logging in...")
            server.login(sender_email, sender_password)
            
            print(f"✓ Sending test email to {recipient_email}...")
            server.send_message(msg)
        
        print("\n" + "="*60)
        print("  ✅ SUCCESS! Email sent successfully!")
        print("="*60)
        print(f"\nCheck your inbox at: {recipient_email}")
        print("(Don't forget to check spam folder if you don't see it)")
        print("\nYour Crime Detection System is ready to send alerts! 🎉\n")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print("\n" + "="*60)
        print("  ❌ AUTHENTICATION ERROR")
        print("="*60)
        print("\nPossible issues:")
        print("1. Wrong email or password")
        print("2. Using regular password instead of App Password")
        print("3. 2-Step Verification not enabled on Gmail")
        print("\nHow to fix:")
        print("1. Go to https://myaccount.google.com/security")
        print("2. Enable 2-Step Verification")
        print("3. Click 'App passwords'")
        print("4. Generate a new app password for 'Mail'")
        print("5. Copy it to SMTP_PASSWORD in .env (remove spaces)")
        print(f"\nError details: {str(e)}\n")
        return False
        
    except smtplib.SMTPException as e:
        print("\n" + "="*60)
        print("  ❌ SMTP ERROR")
        print("="*60)
        print(f"\nError: {str(e)}")
        print("\nPossible issues:")
        print("1. SMTP server blocked by firewall")
        print("2. Network connectivity issues")
        print("3. Gmail security settings")
        print("\nTry:")
        print("1. Check your internet connection")
        print("2. Disable antivirus/firewall temporarily")
        print("3. Verify Gmail allows less secure apps\n")
        return False
        
    except Exception as e:
        print("\n" + "="*60)
        print("  ❌ UNEXPECTED ERROR")
        print("="*60)
        print(f"\nError: {str(e)}")
        print(f"Type: {type(e).__name__}\n")
        return False


if __name__ == "__main__":
    test_email_config()
