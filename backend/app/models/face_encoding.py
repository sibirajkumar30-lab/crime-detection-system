"""Face encoding model for storing facial features."""

from datetime import datetime
import pickle
import numpy as np
from app import db


class FaceEncoding(db.Model):
    """Face encoding model for storing facial feature vectors."""
    
    __tablename__ = 'face_encodings'
    
    id = db.Column(db.Integer, primary_key=True)
    criminal_id = db.Column(db.Integer, db.ForeignKey('criminals.id', ondelete='CASCADE'), nullable=False)
    encoding_data = db.Column(db.LargeBinary, nullable=False)  # Store numpy array as binary
    image_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Phase 2/3 enhancements
    quality_score = db.Column(db.Float, nullable=True)  # 0.0-1.0, higher is better
    pose_type = db.Column(db.String(50), nullable=True)  # frontal, left_profile, right_profile, etc.
    is_primary = db.Column(db.Boolean, default=False, nullable=False)  # Mark best quality photo
    
    def __repr__(self):
        return f'<FaceEncoding {self.id} for Criminal {self.criminal_id}>'
    
    def set_encoding(self, encoding_array):
        """
        Convert numpy array to binary and store.
        
        Args:
            encoding_array: numpy array of face encoding
        """
        self.encoding_data = pickle.dumps(encoding_array)
    
    def get_encoding(self):
        """
        Retrieve and convert binary data back to numpy array.
        
        Returns:
            numpy array of face encoding
        """
        return pickle.loads(self.encoding_data)
    
    def to_dict(self, include_encoding=False):
        """Convert face encoding object to dictionary."""
        data = {
            'id': self.id,
            'criminal_id': self.criminal_id,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'quality_score': self.quality_score,
            'pose_type': self.pose_type,
            'is_primary': self.is_primary
        }
        
        if include_encoding:
            try:
                encoding = self.get_encoding()
                data['encoding'] = encoding.tolist() if isinstance(encoding, np.ndarray) else encoding
            except Exception as e:
                data['encoding'] = None
                data['encoding_error'] = str(e)
        
        return data
