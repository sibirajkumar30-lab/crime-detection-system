"""Criminal model for storing criminal records."""

from datetime import datetime
from app import db


class Criminal(db.Model):
    """Criminal record model."""
    
    __tablename__ = 'criminals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    alias = db.Column(db.String(100))
    crime_type = db.Column(db.String(50), nullable=False)  # theft, assault, fraud, etc.
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='wanted', nullable=False)  # wanted, arrested, released
    danger_level = db.Column(db.String(20))  # low, medium, high, critical
    last_seen_location = db.Column(db.String(200))
    last_seen_date = db.Column(db.Date)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    added_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    face_encodings = db.relationship('FaceEncoding', backref='criminal', lazy=True, cascade='all, delete-orphan')
    detections = db.relationship('DetectionLog', backref='criminal', lazy=True)
    
    def __repr__(self):
        return f'<Criminal {self.name}>'
    
    def to_dict(self, include_encodings=False):
        """Convert criminal object to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'alias': self.alias,
            'crime_type': self.crime_type,
            'description': self.description,
            'status': self.status,
            'danger_level': self.danger_level,
            'last_seen_location': self.last_seen_location,
            'last_seen_date': self.last_seen_date.isoformat() if self.last_seen_date else None,
            'added_by': self.added_by,
            'added_date': self.added_date.isoformat() if self.added_date else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'encodings_count': len(self.face_encodings)
        }
        
        if include_encodings:
            data['encodings'] = [enc.to_dict() for enc in self.face_encodings]
        
        return data
