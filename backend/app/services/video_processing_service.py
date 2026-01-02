"""Video processing service for frame-by-frame face detection."""

import os
import cv2
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app import db
from app.models.video_detection import VideoDetection, VideoFrameDetection
from app.models.criminal import Criminal
from app.models.face_encoding import FaceEncoding
from app.models.detection_log import DetectionLog
from app.services.face_service_deepface import face_service_deepface as face_service
from app.services.alert_service import send_detection_alert

logger = logging.getLogger(__name__)

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'}
VIDEO_UPLOAD_FOLDER = 'uploads/videos'
FRAME_UPLOAD_FOLDER = 'uploads/video_frames'
ANNOTATED_VIDEO_FOLDER = 'uploads/annotated_videos'


class VideoProcessingService:
    """Handle video upload, processing, and face detection."""
    
    @staticmethod
    def allowed_video_file(filename: str) -> bool:
        """Check if file extension is allowed for videos."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS
    
    @staticmethod
    def save_video_upload(file: FileStorage) -> Optional[str]:
        """
        Save uploaded video file.
        
        Args:
            file: FileStorage object from request
            
        Returns:
            Path to saved file or None if invalid
        """
        try:
            if not file or file.filename == '':
                return None
            
            if not VideoProcessingService.allowed_video_file(file.filename):
                logger.warning(f"Invalid video file type: {file.filename}")
                return None
            
            # Create upload directory
            os.makedirs(VIDEO_UPLOAD_FOLDER, exist_ok=True)
            
            # Generate secure filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(VIDEO_UPLOAD_FOLDER, filename)
            
            # Save file
            file.save(filepath)
            logger.info(f"Video saved: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Video upload failed: {str(e)}")
            return None
    
    @staticmethod
    def get_video_metadata(video_path: str) -> Dict:
        """
        Extract metadata from video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video metadata
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError("Could not open video file")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # File size in MB
            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            
            cap.release()
            
            return {
                'fps': fps,
                'total_frames': frame_count,
                'width': width,
                'height': height,
                'duration_seconds': duration,
                'file_size_mb': round(file_size_mb, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to extract video metadata: {str(e)}")
            return {}
    
    @staticmethod
    def process_video(
        video_detection_id: int,
        frame_skip: int = 5,
        confidence_threshold: float = 0.70
    ) -> Dict:
        """
        Process video frame-by-frame for face detection.
        
        Args:
            video_detection_id: ID of VideoDetection record
            frame_skip: Process every Nth frame (default: 5 for performance)
            confidence_threshold: Minimum confidence for match (0.0-1.0)
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Get video detection record
            video_detection = VideoDetection.query.get(video_detection_id)
            if not video_detection:
                return {'success': False, 'message': 'Video detection record not found'}
            
            # Update status
            video_detection.processing_status = 'processing'
            video_detection.processing_started_at = datetime.utcnow()
            db.session.commit()
            
            video_path = video_detection.video_path
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                video_detection.processing_status = 'failed'
                video_detection.error_message = 'Could not open video file'
                db.session.commit()
                return {'success': False, 'message': 'Could not open video file'}
            
            # Get all criminal encodings for matching
            criminals_data = []
            criminals = Criminal.query.filter_by(status='wanted').all()
            for criminal in criminals:
                encodings = FaceEncoding.query.filter_by(criminal_id=criminal.id).all()
                for enc in encodings:
                    criminals_data.append({
                        'criminal_id': criminal.id,
                        'criminal_name': criminal.name,
                        'encoding': enc.get_encoding()
                    })
            
            logger.info(f"Loaded {len(criminals_data)} criminal encodings for matching")
            
            # Process video frames
            frame_number = 0
            total_faces = 0
            matched_criminals = set()
            matched_criminals_details = {}  # Store details for email alert
            frames_with_matches = []
            
            fps = video_detection.fps if video_detection.fps else 30
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_number += 1
                
                # Skip frames for performance
                if frame_number % frame_skip != 0:
                    continue
                
                # Save frame temporarily
                os.makedirs(FRAME_UPLOAD_FOLDER, exist_ok=True)
                frame_filename = f"video_{video_detection_id}_frame_{frame_number}.jpg"
                frame_path = os.path.join(FRAME_UPLOAD_FOLDER, frame_filename)
                cv2.imwrite(frame_path, frame)
                
                # Detect faces in frame
                try:
                    faces = face_service.detect_faces(frame_path)
                    
                    if faces:
                        total_faces += len(faces)
                        logger.info(f"Frame {frame_number}: Detected {len(faces)} face(s)")
                        
                        # Process each face
                        for face_idx, face_coords in enumerate(faces):
                            # Extract face encoding
                            import tempfile
                            import numpy as np
                            
                            x, y, w, h = face_coords
                            # Crop face with padding
                            padding = 20
                            y1 = max(0, y - padding)
                            y2 = min(frame.shape[0], y + h + padding)
                            x1 = max(0, x - padding)
                            x2 = min(frame.shape[1], x + w + padding)
                            
                            face_crop = frame[y1:y2, x1:x2]
                            
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                                temp_face_path = tmp.name
                                cv2.imwrite(temp_face_path, face_crop)
                            
                            try:
                                detected_encoding = face_service.extract_face_encoding(temp_face_path)
                                
                                if detected_encoding is not None:
                                    # Match against criminals
                                    best_match = None
                                    best_confidence = 0.0
                                    
                                    for criminal_data in criminals_data:
                                        is_match, confidence = face_service.compare_faces(
                                            criminal_data['encoding'],
                                            detected_encoding
                                        )
                                        
                                        if confidence > best_confidence:
                                            best_confidence = confidence
                                            best_match = criminal_data
                                    
                                    # Check if match meets threshold
                                    if best_match and best_confidence >= confidence_threshold:
                                        criminal_id = best_match['criminal_id']
                                        matched_criminals.add(criminal_id)
                                        
                                        # Store details for final email alert
                                        if criminal_id not in matched_criminals_details:
                                            matched_criminals_details[criminal_id] = {
                                                'name': best_match['criminal_name'],
                                                'max_confidence': best_confidence,
                                                'frame_count': 1,
                                                'first_frame': frame_number,
                                                'first_timestamp': round(frame_number / fps, 2)
                                            }
                                        else:
                                            matched_criminals_details[criminal_id]['frame_count'] += 1
                                            if best_confidence > matched_criminals_details[criminal_id]['max_confidence']:
                                                matched_criminals_details[criminal_id]['max_confidence'] = best_confidence
                                        
                                        # Create frame detection record
                                        frame_detection = VideoFrameDetection(
                                            video_detection_id=video_detection_id,
                                            frame_number=frame_number,
                                            timestamp_seconds=frame_number / fps,
                                            faces_detected=len(faces),
                                            criminal_id=criminal_id,
                                            confidence_score=best_confidence,
                                            face_coordinates=json.dumps({'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)}),
                                            frame_image_path=frame_path
                                        )
                                        db.session.add(frame_detection)
                                        
                                        frames_with_matches.append({
                                            'frame': frame_number,
                                            'timestamp': round(frame_number / fps, 2),
                                            'criminal': best_match['criminal_name'],
                                            'confidence': round(best_confidence * 100, 2)
                                        })
                                        
                                        logger.info(f"Match found in frame {frame_number}: {best_match['criminal_name']} ({best_confidence*100:.1f}%)")
                                        
                                        # NOTE: Alert will be sent at the end of processing, not per frame
                                    else:
                                        # No match - still record frame had faces
                                        frame_detection = VideoFrameDetection(
                                            video_detection_id=video_detection_id,
                                            frame_number=frame_number,
                                            timestamp_seconds=frame_number / fps,
                                            faces_detected=len(faces),
                                            face_coordinates=json.dumps({'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)}),
                                            frame_image_path=frame_path
                                        )
                                        db.session.add(frame_detection)
                                
                            finally:
                                # Clean up temp file
                                if os.path.exists(temp_face_path):
                                    os.remove(temp_face_path)
                    
                    # Remove frame image if no matches (save storage)
                    if not any(f['frame'] == frame_number for f in frames_with_matches):
                        if os.path.exists(frame_path):
                            os.remove(frame_path)
                    
                except Exception as e:
                    logger.error(f"Error processing frame {frame_number}: {str(e)}")
                    continue
                
                # Update progress periodically
                if frame_number % 50 == 0:
                    video_detection.frames_processed = frame_number
                    db.session.commit()
            
            cap.release()
            
            # Send ONE consolidated email alert if criminals were detected
            if matched_criminals_details:
                try:
                    from app.services.alert_service import send_video_detection_alert
                    send_video_detection_alert(video_detection, matched_criminals_details)
                except Exception as e:
                    logger.error(f"Failed to send video alert: {str(e)}")
            
            # Update final statistics
            video_detection.processing_status = 'completed'
            video_detection.processing_completed_at = datetime.utcnow()
            video_detection.frames_processed = frame_number
            video_detection.total_faces_detected = total_faces
            video_detection.unique_criminals_matched = len(matched_criminals)
            video_detection.summary_report = json.dumps({
                'total_frames': frame_number,
                'frames_processed': frame_number // frame_skip,
                'total_faces': total_faces,
                'unique_criminals': len(matched_criminals),
                'matches': frames_with_matches
            })
            db.session.commit()
            
            return {
                'success': True,
                'frames_processed': frame_number,
                'total_faces': total_faces,
                'unique_criminals_matched': len(matched_criminals),
                'matches': frames_with_matches
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Video processing failed: {str(e)}")
            
            # Update status
            if video_detection:
                video_detection.processing_status = 'failed'
                video_detection.error_message = str(e)
                db.session.commit()
            
            return {
                'success': False,
                'message': f'Video processing failed: {str(e)}'
            }
    
    @staticmethod
    def get_video_detections(limit: int = 10) -> List[Dict]:
        """Get recent video detection records."""
        try:
            videos = VideoDetection.query.order_by(
                VideoDetection.upload_date.desc()
            ).limit(limit).all()
            
            return [v.to_dict() for v in videos]
            
        except Exception as e:
            logger.error(f"Failed to retrieve video detections: {str(e)}")
            return []
    
    @staticmethod
    def get_video_detection_details(video_id: int) -> Optional[Dict]:
        """Get detailed results for a specific video detection."""
        try:
            video = VideoDetection.query.get(video_id)
            if not video:
                return None
            
            return video.to_dict(include_frames=True)
            
        except Exception as e:
            logger.error(f"Failed to get video details: {str(e)}")
            return None


# Global instance
video_processing_service = VideoProcessingService()
