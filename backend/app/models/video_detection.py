"""Video detection model for tracking video-based face detection events."""

from datetime import datetime
from app import db


class VideoDetection(db.Model):
    """Video detection model for recording face detection events from video files."""
    
    __tablename__ = 'video_detections'
    
    id = db.Column(db.Integer, primary_key=True)
    video_filename = db.Column(db.String(255), nullable=False)
    video_path = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Video metadata
    duration_seconds = db.Column(db.Float, nullable=True)
    fps = db.Column(db.Float, nullable=True)
    total_frames = db.Column(db.Integer, nullable=True)
    resolution_width = db.Column(db.Integer, nullable=True)
    resolution_height = db.Column(db.Integer, nullable=True)
    file_size_mb = db.Column(db.Float, nullable=True)
    
    # Processing metadata
    processing_status = db.Column(db.String(20), default='pending', nullable=False)  # pending, processing, completed, failed
    frames_processed = db.Column(db.Integer, default=0)
    total_faces_detected = db.Column(db.Integer, default=0)
    unique_criminals_matched = db.Column(db.Integer, default=0)
    processing_started_at = db.Column(db.DateTime, nullable=True)
    processing_completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Location metadata
    location = db.Column(db.String(200), nullable=True)
    camera_id = db.Column(db.String(50), nullable=True)
    
    # Results
    annotated_video_path = db.Column(db.String(500), nullable=True)  # Path to video with bounding boxes
    summary_report = db.Column(db.Text, nullable=True)  # JSON string with detailed results
    
    # Relationships
    frame_detections = db.relationship('VideoFrameDetection', backref='video', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<VideoDetection {self.id} - {self.video_filename}>'
    
    def to_dict(self, include_frames=False):
        """Convert video detection object to dictionary."""
        data = {
            'id': self.id,
            'video_filename': self.video_filename,
            'video_path': self.video_path,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'uploaded_by': self.uploaded_by,
            'duration_seconds': self.duration_seconds,
            'fps': self.fps,
            'total_frames': self.total_frames,
            'resolution': f'{self.resolution_width}x{self.resolution_height}' if self.resolution_width else None,
            'file_size_mb': self.file_size_mb,
            'processing_status': self.processing_status,
            'frames_processed': self.frames_processed,
            'total_faces_detected': self.total_faces_detected,
            'unique_criminals_matched': self.unique_criminals_matched,
            'processing_started_at': self.processing_started_at.isoformat() if self.processing_started_at else None,
            'processing_completed_at': self.processing_completed_at.isoformat() if self.processing_completed_at else None,
            'error_message': self.error_message,
            'location': self.location,
            'camera_id': self.camera_id,
            'annotated_video_path': self.annotated_video_path
        }
        
        # Add matched criminals info - always fetch to ensure data consistency
        from app.models.criminal import Criminal
        # Get unique criminal IDs from frame detections
        criminal_ids = db.session.query(VideoFrameDetection.criminal_id).filter(
            VideoFrameDetection.video_detection_id == self.id,
            VideoFrameDetection.criminal_id.isnot(None)
        ).distinct().all()
        
        matched_criminals = []
        for (cid,) in criminal_ids:
            criminal = Criminal.query.get(cid)
            if criminal:
                matched_criminals.append({
                    'id': criminal.id,
                    'name': criminal.name,
                    'crime_type': criminal.crime_type,
                    'danger_level': criminal.danger_level
                })
        data['matched_criminals'] = matched_criminals
        
        # Update unique_criminals_matched count if it doesn't match
        if len(matched_criminals) != self.unique_criminals_matched:
            self.unique_criminals_matched = len(matched_criminals)
            try:
                db.session.commit()
            except:
                db.session.rollback()
        
        if include_frames and self.frame_detections:
            data['frame_detections'] = [frame.to_dict() for frame in self.frame_detections]
        
        return data


class VideoFrameDetection(db.Model):
    """Individual frame detection results within a video."""
    
    __tablename__ = 'video_frame_detections'
    
    id = db.Column(db.Integer, primary_key=True)
    video_detection_id = db.Column(db.Integer, db.ForeignKey('video_detections.id', ondelete='CASCADE'), nullable=False)
    frame_number = db.Column(db.Integer, nullable=False)
    timestamp_seconds = db.Column(db.Float, nullable=False)
    
    # Face detection in this frame
    faces_detected = db.Column(db.Integer, default=0)
    
    # Match results
    criminal_id = db.Column(db.Integer, db.ForeignKey('criminals.id'), nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)  # 0.0 to 1.0
    face_coordinates = db.Column(db.String(100), nullable=True)  # JSON: {"x": 100, "y": 200, "w": 50, "h": 50}
    
    # Frame image path (optional - can extract frame for review)
    frame_image_path = db.Column(db.String(500), nullable=True)
    
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<VideoFrameDetection Video:{self.video_detection_id} Frame:{self.frame_number}>'
    
    def to_dict(self, include_criminal=False):
        """Convert frame detection to dictionary."""
        data = {
            'id': self.id,
            'video_detection_id': self.video_detection_id,
            'frame_number': self.frame_number,
            'timestamp_seconds': self.timestamp_seconds,
            'faces_detected': self.faces_detected,
            'criminal_id': self.criminal_id,
            'confidence_score': self.confidence_score,
            'face_coordinates': self.face_coordinates,
            'frame_image_path': self.frame_image_path,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None
        }
        
        if include_criminal and self.criminal_id:
            from app.models.criminal import Criminal
            criminal = Criminal.query.get(self.criminal_id)
            if criminal:
                data['criminal'] = criminal.to_dict()
        
        return data
