"""Enhanced alert service with multi-channel support (email, SMS, in-app)."""

import os
from datetime import datetime
from flask import current_app
from app import db
from app.models.alert import Alert
from app.models.user import User
from app.services.sms_service import send_sms_alert
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EnhancedAlertService:
    """Service for sending multi-channel alerts."""
    
    @staticmethod
    def send_alert(
        message,
        severity='info',
        category='operational',
        alert_type='general',
        priority=3,
        user_id=None,
        channels=['email', 'in_app'],
        data=None
    ):
        """
        Send alert through multiple channels.
        
        Args:
            message: Alert message
            severity: 'info', 'warning', 'critical'
            category: 'detection', 'criminal_mgmt', 'system', 'operational', 'audit', 'schedule'
            alert_type: Specific alert type (e.g., 'criminal_detected', 'system_error')
            priority: 1 (highest) to 5 (lowest)
            user_id: Specific user to notify (None = all admins)
            channels: List of channels ['email', 'sms', 'in_app']
            data: Additional data dictionary
        
        Returns:
            Alert object
        """
        try:
            # Get recipients
            if user_id:
                recipients = [User.query.get(user_id)]
            else:
                # Notify all admin users
                recipients = User.query.filter_by(role='admin').all()
            
            if not recipients:
                print("No recipients found for alert")
                return None
            
            # Create alert record(s)
            alerts = []
            for channel in channels:
                for recipient in recipients:
                    alert = Alert(
                        message=message,
                        severity=severity,
                        category=category,
                        alert_type=alert_type,
                        priority=priority,
                        # user_id=recipient.id,  # Column not in DB yet
                        delivery_method=channel,
                        data=data or {},
                        status='pending'
                    )
                    db.session.add(alert)
                    alerts.append(alert)
            
            db.session.commit()
            
            # Send through each channel
            for alert in alerts:
                recipient = User.query.get(alert.user_id)
                
                if alert.delivery_method == 'email':
                    EnhancedAlertService._send_email(alert, recipient)
                elif alert.delivery_method == 'sms':
                    EnhancedAlertService._send_sms(alert, recipient)
                elif alert.delivery_method == 'in_app':
                    # In-app notifications are stored in DB, no action needed
                    alert.status = 'delivered'
                    db.session.commit()
            
            return alerts[0] if alerts else None
            
        except Exception as e:
            db.session.rollback()
            print(f"Failed to send alert: {str(e)}")
            return None
    
    @staticmethod
    def _send_email(alert, recipient):
        """Send email alert."""
        try:
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_username = os.getenv('SMTP_EMAIL')  # Using SMTP_EMAIL from .env
            smtp_password = os.getenv('SMTP_PASSWORD')
            sender_email = smtp_username  # Sender is same as username
            
            if not all([smtp_server, smtp_username, smtp_password]):
                print("SMTP not configured, skipping email")
                alert.status = 'failed'
                db.session.commit()
                return
            
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{alert.severity.upper()}] {alert.category.replace('_', ' ').title()}"
            msg['From'] = sender_email
            msg['To'] = recipient.email
            
            # Email body
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto;">
                  <div style="background: {'#d32f2f' if alert.severity == 'critical' else '#ed6c02' if alert.severity == 'warning' else '#0288d1'}; 
                              color: white; padding: 15px; border-radius: 5px 5px 0 0;">
                    <h2 style="margin: 0;">{alert.severity.upper()} Alert</h2>
                  </div>
                  <div style="background: #f5f5f5; padding: 20px; border-radius: 0 0 5px 5px;">
                    <p style="font-size: 16px; line-height: 1.5;">
                      {alert.message}
                    </p>
                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd;">
                      <p style="font-size: 12px; color: #666; margin: 5px 0;">
                        <strong>Category:</strong> {alert.category.replace('_', ' ').title()}
                      </p>
                      <p style="font-size: 12px; color: #666; margin: 5px 0;">
                        <strong>Priority:</strong> {alert.priority}
                      </p>
                      <p style="font-size: 12px; color: #666; margin: 5px 0;">
                        <strong>Time:</strong> {alert.created_at.strftime('%Y-%m-%d %I:%M %p')}
                      </p>
                    </div>
                  </div>
                </div>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            alert.status = 'delivered'
            db.session.commit()
            print(f"Email alert sent to {recipient.email}")
            
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")
            alert.status = 'failed'
            db.session.commit()
    
    @staticmethod
    def _send_sms(alert, recipient):
        """Send SMS alert."""
        try:
            # Check if SMS is enabled
            sms_enabled = os.getenv('ENABLE_SMS_ALERTS', 'false').lower() == 'true'
            if not sms_enabled:
                print("SMS alerts disabled (ENABLE_SMS_ALERTS=false)")
                alert.status = 'skipped'
                db.session.commit()
                return
            
            if not recipient.phone:
                print(f"User {recipient.username} has no phone number")
                alert.status = 'failed'
                db.session.commit()
                return
            
            # Send SMS using SMS service
            result = send_sms_alert(
                phone_number=recipient.phone,
                message_text=alert.message,
                alert_type=alert.alert_type
            )
            
            if result.get('success'):
                alert.status = 'delivered'
                alert.recipient_phone = recipient.phone
            else:
                alert.status = 'failed'
            
            db.session.commit()
            
        except Exception as e:
            print(f"Failed to send SMS alert: {str(e)}")
            alert.status = 'failed'
            db.session.commit()
    
    @staticmethod
    def send_detection_alert(criminal_name, location, confidence, detection_data=None):
        """Send criminal detection alert through all critical channels."""
        message = f"Criminal detected: {criminal_name} at {location} (Confidence: {confidence:.1f}%)"
        
        # Critical detections get email + in-app (SMS disabled for now)
        channels = ['email', 'in_app']
        # SMS disabled by default - set ENABLE_SMS_ALERTS=true in .env to enable
        # if confidence >= 80 and os.getenv('ENABLE_SMS_ALERTS', 'false').lower() == 'true':
        #     channels.append('sms')
        
        return EnhancedAlertService.send_alert(
            message=message,
            severity='critical',
            category='detection',
            alert_type='criminal_detected',
            priority=1,
            channels=channels,
            data={
                'criminal_name': criminal_name,
                'location': location,
                'confidence': confidence,
                **(detection_data or {})
            }
        )
    
    @staticmethod
    def send_criminal_added_alert(criminal_data):
        """Send alert when new criminal is added."""
        message = f"New criminal added: {criminal_data.get('name', 'Unknown')}"
        
        return EnhancedAlertService.send_alert(
            message=message,
            severity='info',
            category='criminal_mgmt',
            alert_type='criminal_added',
            priority=3,
            channels=['email', 'in_app'],
            data=criminal_data
        )
    
    @staticmethod
    def send_criminal_updated_alert(criminal_name, changes):
        """Send alert when criminal is updated."""
        message = f"Criminal profile updated: {criminal_name}"
        
        return EnhancedAlertService.send_alert(
            message=message,
            severity='info',
            category='criminal_mgmt',
            alert_type='criminal_updated',
            priority=3,
            channels=['email', 'in_app'],
            data={'criminal_name': criminal_name, 'changes': changes}
        )
    
    @staticmethod
    def send_criminal_deleted_alert(criminal_name):
        """Send alert when criminal is deleted."""
        message = f"Criminal removed from database: {criminal_name}"
        
        return EnhancedAlertService.send_alert(
            message=message,
            severity='warning',
            category='criminal_mgmt',
            alert_type='criminal_deleted',
            priority=2,
            channels=['email', 'in_app'],
            data={'criminal_name': criminal_name}
        )
    
    @staticmethod
    def send_system_alert(message, severity='warning', details=None):
        """Send system alert."""
        return EnhancedAlertService.send_alert(
            message=message,
            severity=severity,
            category='system',
            alert_type='system_alert',
            priority=2 if severity == 'critical' else 3,
            channels=['email', 'in_app'] if severity == 'critical' else ['in_app'],
            data={'details': details} if details else None
        )


# Convenience functions for backward compatibility
def send_detection_alert(criminal_name, location, confidence, detection_data=None):
    """Send detection alert."""
    return EnhancedAlertService.send_detection_alert(criminal_name, location, confidence, detection_data)


def send_criminal_added_alert(criminal_data):
    """Send criminal added alert."""
    return EnhancedAlertService.send_criminal_added_alert(criminal_data)


def send_criminal_updated_alert(criminal_name, changes):
    """Send criminal updated alert."""
    return EnhancedAlertService.send_criminal_updated_alert(criminal_name, changes)


def send_criminal_deleted_alert(criminal_name):
    """Send criminal deleted alert."""
    return EnhancedAlertService.send_criminal_deleted_alert(criminal_name)


def send_system_alert(message, severity='warning', details=None):
    """Send system alert."""
    return EnhancedAlertService.send_system_alert(message, severity, details)
