"""Invitation model for admin-only user registration."""

from datetime import datetime, timedelta
from app import db
import secrets


class Invitation(db.Model):
    """Invitation token model for secure user registration."""
    
    __tablename__ = 'invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # admin, operator, viewer
    department = db.Column(db.String(100), nullable=True)
    invited_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    inviter = db.relationship('User', backref='invitations_sent', lazy=True)
    
    def __init__(self, email, role, invited_by, department=None, expires_in_hours=48):
        """Initialize invitation with auto-generated token."""
        self.email = email
        self.role = role
        self.invited_by = invited_by
        self.department = department
        self.token = self.generate_token()
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    @staticmethod
    def generate_token():
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)
    
    def is_valid(self):
        """Check if invitation is still valid."""
        return (
            self.is_active and 
            self.used_at is None and 
            datetime.utcnow() < self.expires_at
        )
    
    def mark_as_used(self):
        """Mark invitation as used."""
        self.used_at = datetime.utcnow()
        self.is_active = False
    
    def to_dict(self):
        """Convert invitation to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'department': self.department,
            'invited_by': self.invited_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'is_active': self.is_active,
            'is_valid': self.is_valid()
        }
    
    def __repr__(self):
        return f'<Invitation {self.email} - {self.role}>'
