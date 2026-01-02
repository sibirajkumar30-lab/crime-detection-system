"""Detection log model for tracking face detection events."""

from datetime import datetime
from app import db


class DetectionLog(db.Model):
    """Detection log model for recording face detection events."""
    
    __tablename__ = 'detection_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    criminal_id = db.Column(db.Integer, db.ForeignKey('criminals.id'), nullable=True)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    confidence_score = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    location = db.Column(db.String(200))
    camera_id = db.Column(db.String(50))
    image_path = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, verified, false_positive
    notes = db.Column(db.Text)
    detected_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    alerts = db.relationship('Alert', backref='detection', lazy=True)
    
    def __repr__(self):
        return f'<DetectionLog {self.id} - Criminal {self.criminal_id}>'
    
    def to_dict(self, include_criminal=False, include_user=False):
        """Convert detection log object to dictionary."""
        data = {
            'id': self.id,
            'criminal_id': self.criminal_id,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'confidence_score': self.confidence_score,
            'location': self.location,
            'camera_id': self.camera_id,
            'image_path': self.image_path,
            'status': self.status,
            'notes': self.notes,
            'detected_by': self.detected_by
        }
        
        if include_criminal and self.criminal:
            data['criminal'] = self.criminal.to_dict()
        
        if include_user and self.detected_by_user:
            data['detected_by_user'] = self.detected_by_user.to_dict()
        
        return data
