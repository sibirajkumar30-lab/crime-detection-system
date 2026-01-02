"""Alert model for tracking notifications (email, SMS, in-app)."""

from datetime import datetime
from app import db


class Alert(db.Model):
    """Enhanced alert model with severity, categories, and multiple delivery methods."""
    
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Alert metadata
    alert_type = db.Column(db.String(50), nullable=False)  # criminal_detected, criminal_added, system_error, etc.
    severity = db.Column(db.String(20), default='info', nullable=False)  # info, warning, critical
    category = db.Column(db.String(50), nullable=False)  # detection, criminal_mgmt, system, operational
    priority = db.Column(db.Integer, default=3, nullable=False)  # 1=low, 3=medium, 5=high
    
    # Related entities (nullable for flexibility)
    detection_log_id = db.Column(db.Integer, db.ForeignKey('detection_logs.id'), nullable=True)
    video_detection_id = db.Column(db.Integer, db.ForeignKey('video_detections.id'), nullable=True)
    criminal_id = db.Column(db.Integer, db.ForeignKey('criminals.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Alert content
    title = db.Column(db.String(200), nullable=True)
    subject = db.Column(db.String(200), nullable=True)  # For email
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON, nullable=True)  # Additional context data
    
    # Delivery method
    delivery_method = db.Column(db.String(20), default='email', nullable=False)  # email, sms, in_app, push
    recipient_email = db.Column(db.String(100), nullable=True)
    recipient_phone = db.Column(db.String(20), nullable=True)
    
    # Status tracking
    status = db.Column(db.String(20), default='sent', nullable=False)  # sent, failed, pending, delivered, read
    acknowledged = db.Column(db.Boolean, default=False, nullable=False)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    retry_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Alert {self.id} - {self.status}>'
    
    def to_dict(self, include_detection=False):
        """Convert alert object to dictionary."""
        data = {
            'id': self.id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'category': self.category,
            'priority': self.priority,
            'title': self.title,
            'subject': self.subject,
            'message': self.message,
            'data': self.data,
            'delivery_method': self.delivery_method,
            'recipient_email': self.recipient_email,
            'recipient_phone': self.recipient_phone,
            'status': self.status,
            'acknowledged': self.acknowledged,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'detection_log_id': self.detection_log_id,
            'criminal_id': self.criminal_id,
            'user_id': self.user_id,
            'video_detection_id': self.video_detection_id
        }
        
        # if include_detection and self.detection:
        #     data['detection'] = self.detection.to_dict(include_criminal=True)
        
        return data
