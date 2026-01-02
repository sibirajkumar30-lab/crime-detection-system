"""Email alert service for criminal detections."""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
import logging

from app import db
from app.models.alert import Alert

logger = logging.getLogger(__name__)


def send_detection_alert(criminal, detection_log, confidence: float):
    """
    Send email alert when criminal is detected.
    
    Args:
        criminal: Criminal model instance
        detection_log: DetectionLog model instance
        confidence: Confidence score (0-1)
    """
    try:
        sender_email = os.getenv('SMTP_EMAIL')
        sender_password = os.getenv('SMTP_PASSWORD')
        recipient_email = os.getenv('ALERT_EMAIL', sender_email)
        
        if not sender_email or not sender_password:
            logger.warning("SMTP credentials not configured, skipping email alert")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f'🚨 ALERT: Criminal Detected - {criminal.name}'
        
        # HTML body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #f44336; color: white; padding: 20px; text-align: center;">
                <h1>⚠️ CRIMINAL DETECTION ALERT</h1>
            </div>
            <div style="padding: 20px;">
                <h2>Criminal Information</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Name:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Crime Type:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.crime_type}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Status:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.status.upper()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Danger Level:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.danger_level.upper()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Confidence Score:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{confidence * 100:.2f}%</td>
                    </tr>
                </table>
                
                <h2 style="margin-top: 30px;">Detection Details</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Time (IST):</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{(detection_log.detected_at + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Location:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{detection_log.location or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Camera ID:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{detection_log.camera_id or 'N/A'}</td>
                    </tr>
                </table>
                
                <div style="margin-top: 30px; padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                    <strong>⚡ ACTION REQUIRED:</strong> Please verify this detection and take appropriate action immediately.
                </div>
                
                {f'<p style="margin-top: 20px;"><strong>Description:</strong> {criminal.description}</p>' if criminal.description else ''}
            </div>
            <div style="background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666;">
                <p>This is an automated alert from Crime Detection System</p>
                <p>Generated at {(datetime.now() + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')} IST</p>
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
        alert = Alert(
            alert_type='criminal_detected',
            severity='critical',
            category='detection',
            priority=5,
            detection_log_id=detection_log.id,
            criminal_id=criminal.id,
            recipient_email=recipient_email,
            subject=msg['Subject'],
            message=html_body,
            delivery_method='email',
            status='sent'
        )
        db.session.add(alert)
        db.session.commit()
        
        logger.info(f"Alert sent for detection {detection_log.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send alert: {str(e)}")
        
        # Log failed alert
        try:
            alert = Alert(
                alert_type='criminal_detected',
                severity='critical',
                category='detection',
                priority=5,
                detection_log_id=detection_log.id,
                criminal_id=criminal.id,
                recipient_email=recipient_email if 'recipient_email' in locals() else 'unknown',
                subject=f'ALERT: Criminal Detected - {criminal.name}',
                message=f'Failed to send: {str(e)}',
                delivery_method='email',
                status='failed'
            )
            db.session.add(alert)
            db.session.commit()
        except:
            pass
        
        return False


def send_video_detection_alert(video_detection, matched_criminals_details: dict):
    """
    Send ONE consolidated email alert for video detection with all criminals found.
    
    Args:
        video_detection: VideoDetection model instance
        matched_criminals_details: Dictionary of criminal_id -> details
    """
    try:
        sender_email = os.getenv('SMTP_EMAIL')
        sender_password = os.getenv('SMTP_PASSWORD')
        recipient_email = os.getenv('ALERT_EMAIL', sender_email)
        
        if not sender_email or not sender_password:
            logger.warning("SMTP credentials not configured, skipping email alert")
            return False
        
        from app.models.criminal import Criminal
        
        # Build criminals table HTML
        criminals_html = ""
        for criminal_id, details in matched_criminals_details.items():
            criminal = Criminal.query.get(criminal_id)
            if criminal:
                criminals_html += f"""
                <tr style="border-bottom: 2px solid #f44336;">
                    <td style="padding: 15px; background-color: #ffebee;">
                        <strong style="font-size: 16px;">{details['name']}</strong><br/>
                        <span style="color: #666;">Crime: {criminal.crime_type}</span><br/>
                        <span style="color: #666;">Status: {criminal.status.upper()}</span>
                    </td>
                    <td style="padding: 15px; text-align: center; background-color: #ffebee;">
                        <strong style="font-size: 18px; color: #d32f2f;">{details['max_confidence']*100:.1f}%</strong><br/>
                        <span style="font-size: 12px; color: #666;">Max Confidence</span>
                    </td>
                    <td style="padding: 15px; text-align: center; background-color: #ffebee;">
                        <strong style="font-size: 18px;">{details['frame_count']}</strong><br/>
                        <span style="font-size: 12px; color: #666;">Frames</span>
                    </td>
                    <td style="padding: 15px; text-align: center; background-color: #ffebee;">
                        <strong>{details['first_timestamp']}s</strong><br/>
                        <span style="font-size: 12px; color: #666;">First Seen</span>
                    </td>
                </tr>
                """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f'🎥 VIDEO ALERT: {len(matched_criminals_details)} Criminal(s) Detected'
        
        # HTML body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #d32f2f; color: white; padding: 20px; text-align: center;">
                <h1>🎥 VIDEO DETECTION ALERT</h1>
                <p style="font-size: 18px; margin: 10px 0;">
                    {len(matched_criminals_details)} Criminal(s) Detected in Video
                </p>
            </div>
            
            <div style="padding: 20px;">
                <h2>Video Information</h2>
                <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Video ID:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">#{video_detection.id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Upload Time (IST):</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{(video_detection.upload_date + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Location:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{video_detection.location or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Camera ID:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{video_detection.camera_id or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Duration:</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{video_detection.duration_seconds:.1f}s ({video_detection.total_frames} frames)</td>
                    </tr>
                </table>
                
                <h2>🚨 Detected Criminals</h2>
                <table style="border-collapse: collapse; width: 100%; margin-top: 10px;">
                    <thead>
                        <tr style="background-color: #f44336; color: white;">
                            <th style="padding: 12px; text-align: left;">Criminal Details</th>
                            <th style="padding: 12px; text-align: center;">Confidence</th>
                            <th style="padding: 12px; text-align: center;">Detections</th>
                            <th style="padding: 12px; text-align: center;">First Seen</th>
                        </tr>
                    </thead>
                    <tbody>
                        {criminals_html}
                    </tbody>
                </table>
                
                <div style="margin-top: 30px; padding: 20px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                    <strong style="font-size: 18px;">⚡ URGENT ACTION REQUIRED</strong><br/>
                    <p style="margin: 10px 0 0 0;">
                        {len(matched_criminals_details)} wanted criminal(s) detected in video footage. 
                        Immediate verification and response required.
                    </p>
                </div>
            </div>
            
            <div style="background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666;">
                <p>This is an automated alert from Crime Detection System</p>
                <p>Generated at {(datetime.now() + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')} IST</p>
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
        alert = Alert(
            alert_type='video_detection',
            severity='critical',
            category='detection',
            priority=5,
            video_detection_id=video_detection.id,
            recipient_email=recipient_email,
            subject=msg['Subject'],
            message=html_body,
            delivery_method='email',
            status='sent'
        )
        db.session.add(alert)
        db.session.commit()
        
        logger.info(f"Video alert sent for video {video_detection.id} with {len(matched_criminals_details)} criminal(s)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send video alert: {str(e)}")
        return False
