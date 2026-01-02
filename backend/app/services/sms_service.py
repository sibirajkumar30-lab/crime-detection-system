"""SMS alert service using Twilio."""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Twilio (optional dependency)
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not installed. SMS functionality disabled. Install with: pip install twilio")


def send_sms_alert(phone_number, message_text, alert_type='info'):
    """
    Send SMS alert using Twilio.
    
    Args:
        phone_number: Recipient phone number (+1234567890 format)
        message_text: SMS message content (max 160 chars recommended)
        alert_type: Type of alert for logging
        
    Returns:
        dict: {'success': bool, 'message_sid': str or None, 'error': str or None}
    """
    if not TWILIO_AVAILABLE:
        logger.error("Twilio library not installed")
        return {
            'success': False,
            'message_sid': None,
            'error': 'Twilio library not installed. Run: pip install twilio'
        }
    
    try:
        # Get Twilio credentials from environment
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, from_number]):
            logger.warning("Twilio credentials not configured")
            return {
                'success': False,
                'message_sid': None,
                'error': 'Twilio credentials not configured in .env'
            }
        
        # Validate phone number format
        if not phone_number.startswith('+'):
            phone_number = f'+{phone_number}'
        
        # Truncate message if too long (SMS limit is 160 chars per segment)
        if len(message_text) > 160:
            message_text = message_text[:157] + '...'
        
        # Create Twilio client
        client = Client(account_sid, auth_token)
        
        # Send SMS
        message = client.messages.create(
            body=message_text,
            from_=from_number,
            to=phone_number
        )
        
        logger.info(f"SMS sent successfully. SID: {message.sid}, To: {phone_number}")
        
        return {
            'success': True,
            'message_sid': message.sid,
            'error': None
        }
        
    except Exception as e:
        logger.error(f"Failed to send SMS: {str(e)}")
        return {
            'success': False,
            'message_sid': None,
            'error': str(e)
        }


def format_criminal_detection_sms(criminal_name, location, confidence):
    """
    Format SMS message for criminal detection alert.
    Keep it short (160 chars max for single SMS).
    
    Args:
        criminal_name: Name of detected criminal
        location: Detection location
        confidence: Confidence score (0-1)
        
    Returns:
        str: Formatted SMS message
    """
    confidence_pct = int(confidence * 100)
    loc = location or 'Unknown'
    
    # Keep it concise for SMS
    message = f"🚨 ALERT: {criminal_name} detected at {loc}. Confidence: {confidence_pct}%. Respond immediately."
    
    return message


def format_system_alert_sms(alert_title, details):
    """
    Format SMS message for system alerts.
    
    Args:
        alert_title: Alert title
        details: Brief details
        
    Returns:
        str: Formatted SMS message
    """
    message = f"⚠️ {alert_title}: {details}"
    return message[:160]  # Truncate to SMS limit


def send_critical_detection_sms(criminal, detection_log, confidence, phone_numbers):
    """
    Send SMS for critical criminal detections.
    Only sends if confidence > 90% and criminal danger level is high/critical.
    
    Args:
        criminal: Criminal model instance
        detection_log: DetectionLog model instance  
        confidence: Confidence score (0-1)
        phone_numbers: List of phone numbers to notify
        
    Returns:
        list: List of result dicts for each SMS sent
    """
    # Check if this is critical enough for SMS
    if confidence < 0.90:
        logger.info(f"Confidence {confidence} < 0.90, skipping SMS")
        return []
    
    if criminal.danger_level not in ['high', 'critical']:
        logger.info(f"Danger level {criminal.danger_level} not high/critical, skipping SMS")
        return []
    
    # Format SMS message
    sms_text = format_criminal_detection_sms(
        criminal.name,
        detection_log.location,
        confidence
    )
    
    # Send to all numbers
    results = []
    for phone in phone_numbers:
        result = send_sms_alert(phone, sms_text, alert_type='critical_detection')
        results.append({
            'phone': phone,
            **result
        })
    
    return results
