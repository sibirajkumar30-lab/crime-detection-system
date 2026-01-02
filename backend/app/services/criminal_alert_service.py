"""Alert service for criminal management operations."""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

from app import db
from app.models.alert import Alert
from app.models.user import User

logger = logging.getLogger(__name__)


def send_criminal_added_alert(criminal, added_by_user):
    """
    Send alert when a new criminal is added to the database.
    
    Args:
        criminal: Criminal model instance
        added_by_user: User who added the criminal
    """
    try:
        sender_email = os.getenv('SMTP_EMAIL')
        sender_password = os.getenv('SMTP_PASSWORD')
        recipient_email = os.getenv('ALERT_EMAIL', sender_email)
        
        if not sender_email or not sender_password:
            logger.warning("SMTP credentials not configured, skipping criminal added alert")
            return False
        
        # Get all admin users for notification
        admin_users = User.query.filter_by(role='admin').all()
        recipient_emails = [user.email for user in admin_users if user.email]
        
        if not recipient_emails:
            recipient_emails = [recipient_email]
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = ', '.join(recipient_emails)
        msg['Subject'] = f'✅ New Criminal Added: {criminal.name}'
        
        # HTML body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #28a745; color: white; padding: 20px; text-align: center;">
                <h1>✅ NEW CRIMINAL RECORD ADDED</h1>
            </div>
            <div style="padding: 20px;">
                <p>A new criminal record has been added to the Crime Detection System.</p>
                
                <h2>Criminal Information</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Name:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.name}</td>
                    </tr>
                    {f'''<tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Alias:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.alias}</td>
                    </tr>''' if criminal.alias else ''}
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Crime Type:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.crime_type}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Status:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; text-transform: uppercase;">{criminal.status}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Danger Level:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; text-transform: uppercase;">{criminal.danger_level or 'Not Specified'}</td>
                    </tr>
                    {f'''<tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Last Seen:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.last_seen_location}</td>
                    </tr>''' if criminal.last_seen_location else ''}
                </table>
                
                {f'<div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #6c757d;"><strong>Description:</strong><br>{criminal.description}</div>' if criminal.description else ''}
                
                <h2 style="margin-top: 30px;">Action Details</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Added By:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{added_by_user.username} ({added_by_user.email})</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Added At:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.added_date.strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Criminal ID:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">#{criminal.id}</td>
                    </tr>
                </table>
                
                <div style="margin-top: 30px; padding: 15px; background-color: #d1ecf1; border-left: 4px solid #17a2b8;">
                    <strong>ℹ️ Next Steps:</strong>
                    <ul style="margin: 10px 0 0 20px;">
                        <li>Upload photos for face encoding</li>
                        <li>Review and verify criminal details</li>
                        <li>System will start monitoring for this individual</li>
                    </ul>
                </div>
            </div>
            <div style="background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666;">
                <p>This is an automated alert from Crime Detection System</p>
                <p>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        # Log alert in database
        for email in recipient_emails:
            alert = Alert(
                alert_type='criminal_added',
                severity='info',
                category='criminal_mgmt',
                priority=3,
                detection_log_id=None,
                recipient_email=email,
                subject=msg['Subject'],
                message=html_body,
                delivery_method='email',
                status='sent'
            )
            db.session.add(alert)
        
        db.session.commit()
        logger.info(f"Criminal added alert sent for criminal {criminal.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send criminal added alert: {str(e)}")
        return False


def send_criminal_updated_alert(criminal, updated_by_user, changes):
    """
    Send alert when a criminal record is updated.
    
    Args:
        criminal: Criminal model instance
        updated_by_user: User who updated the criminal
        changes: Dictionary of changed fields
    """
    try:
        sender_email = os.getenv('SMTP_EMAIL')
        sender_password = os.getenv('SMTP_PASSWORD')
        recipient_email = os.getenv('ALERT_EMAIL', sender_email)
        
        if not sender_email or not sender_password:
            logger.warning("SMTP credentials not configured, skipping criminal updated alert")
            return False
        
        # Get all admin users for notification
        admin_users = User.query.filter_by(role='admin').all()
        recipient_emails = [user.email for user in admin_users if user.email]
        
        if not recipient_emails:
            recipient_emails = [recipient_email]
        
        # Build changes table
        changes_html = ""
        if changes:
            changes_html = "<h2>Changes Made</h2><table style='border-collapse: collapse; width: 100%;'>"
            for field, (old_value, new_value) in changes.items():
                changes_html += f"""
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; width: 25%;"><strong>{field.replace('_', ' ').title()}:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; width: 35%; color: #dc3545; text-decoration: line-through;">{old_value or 'N/A'}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; width: 5%; text-align: center;">→</td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; width: 35%; color: #28a745; font-weight: bold;">{new_value or 'N/A'}</td>
                </tr>
                """
            changes_html += "</table>"
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = ', '.join(recipient_emails)
        msg['Subject'] = f'📝 Criminal Record Updated: {criminal.name}'
        
        # HTML body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #ffc107; color: #333; padding: 20px; text-align: center;">
                <h1>📝 CRIMINAL RECORD UPDATED</h1>
            </div>
            <div style="padding: 20px;">
                <p>A criminal record has been modified in the Crime Detection System.</p>
                
                <h2>Criminal Information</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Criminal ID:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">#{criminal.id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Name:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Crime Type:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.crime_type}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Current Status:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; text-transform: uppercase;">{criminal.status}</td>
                    </tr>
                </table>
                
                {changes_html}
                
                <h2 style="margin-top: 30px;">Update Details</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Updated By:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{updated_by_user.username} ({updated_by_user.email})</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Updated At:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                </table>
                
                <div style="margin-top: 30px; padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                    <strong>ℹ️ Note:</strong> All detection alerts and monitoring for this criminal will continue with updated information.
                </div>
            </div>
            <div style="background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666;">
                <p>This is an automated alert from Crime Detection System</p>
                <p>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        # Log alert in database
        for email in recipient_emails:
            alert = Alert(
                alert_type='criminal_updated',
                severity='info',
                category='criminal_mgmt',
                priority=3,
                detection_log_id=None,
                recipient_email=email,
                subject=msg['Subject'],
                message=html_body,
                delivery_method='email',
                status='sent'
            )
            db.session.add(alert)
        
        db.session.commit()
        logger.info(f"Criminal updated alert sent for criminal {criminal.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send criminal updated alert: {str(e)}")
        return False


def send_criminal_deleted_alert(criminal_data, deleted_by_user):
    """
    Send alert when a criminal record is deleted.
    
    Args:
        criminal_data: Dictionary with criminal information (since object is deleted)
        deleted_by_user: User who deleted the criminal
    """
    try:
        sender_email = os.getenv('SMTP_EMAIL')
        sender_password = os.getenv('SMTP_PASSWORD')
        recipient_email = os.getenv('ALERT_EMAIL', sender_email)
        
        if not sender_email or not sender_password:
            logger.warning("SMTP credentials not configured, skipping criminal deleted alert")
            return False
        
        # Get all admin users for notification
        admin_users = User.query.filter_by(role='admin').all()
        recipient_emails = [user.email for user in admin_users if user.email]
        
        if not recipient_emails:
            recipient_emails = [recipient_email]
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = ', '.join(recipient_emails)
        msg['Subject'] = f'🗑️ Criminal Record Deleted: {criminal_data["name"]}'
        
        # HTML body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #dc3545; color: white; padding: 20px; text-align: center;">
                <h1>🗑️ CRIMINAL RECORD DELETED</h1>
            </div>
            <div style="padding: 20px;">
                <p>A criminal record has been permanently removed from the Crime Detection System.</p>
                
                <div style="padding: 15px; background-color: #f8d7da; border-left: 4px solid #dc3545; margin-bottom: 20px;">
                    <strong>⚠️ WARNING:</strong> This action is permanent. All associated data including face encodings and detection history have been removed.
                </div>
                
                <h2>Deleted Criminal Information</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Criminal ID:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">#{criminal_data["id"]}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Name:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal_data["name"]}</td>
                    </tr>
                    {f'''<tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Alias:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal_data.get("alias", "N/A")}</td>
                    </tr>''' if criminal_data.get("alias") else ''}
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Crime Type:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal_data["crime_type"]}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Status:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; text-transform: uppercase;">{criminal_data["status"]}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Danger Level:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; text-transform: uppercase;">{criminal_data.get("danger_level", "N/A")}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Total Detections:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal_data.get("detection_count", 0)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Face Encodings:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal_data.get("encodings_count", 0)}</td>
                    </tr>
                </table>
                
                <h2 style="margin-top: 30px;">Deletion Details</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Deleted By:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{deleted_by_user.username} ({deleted_by_user.email})</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Deleted At:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Reason:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal_data.get("deletion_reason", "Not specified")}</td>
                    </tr>
                </table>
                
                <div style="margin-top: 30px; padding: 15px; background-color: #d1ecf1; border-left: 4px solid #17a2b8;">
                    <strong>ℹ️ Impact:</strong>
                    <ul style="margin: 10px 0 0 20px;">
                        <li>System will no longer monitor for this individual</li>
                        <li>All face encodings have been removed</li>
                        <li>Historical detection logs are preserved for audit purposes</li>
                        <li>Associated alerts remain in the system</li>
                    </ul>
                </div>
            </div>
            <div style="background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666;">
                <p>This is an automated alert from Crime Detection System</p>
                <p>Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        # Log alert in database
        for email in recipient_emails:
            alert = Alert(
                alert_type='criminal_deleted',
                severity='warning',
                category='criminal_mgmt',
                priority=4,
                detection_log_id=None,
                recipient_email=email,
                subject=msg['Subject'],
                message=html_body,
                delivery_method='email',
                status='sent'
            )
            db.session.add(alert)
        
        db.session.commit()
        logger.info(f"Criminal deleted alert sent for criminal {criminal_data['id']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send criminal deleted alert: {str(e)}")
        return False
