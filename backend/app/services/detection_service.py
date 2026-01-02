"""Detection processing service."""

import os
from datetime import datetime
from typing import Dict, List, Optional
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import logging

from app import db
from app.models.criminal import Criminal
from app.models.face_encoding import FaceEncoding
from app.models.detection_log import DetectionLog
from app.services.face_service_deepface import face_service_deepface as face_service  # Using DeepFace AI (99.65% accuracy)
from app.services.alert_service import send_detection_alert

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}  # Added webp - modern format
UPLOAD_FOLDER = 'uploads'


class DetectionService:
    """Handle face detection and criminal matching."""
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @staticmethod
    def save_upload(file: FileStorage) -> Optional[str]:
        """
        Save uploaded file.
        
        Args:
            file: Uploaded file
            
        Returns:
            Path to saved file or None if failed
        """
        try:
            if not file or file.filename == '':
                return None
            
            if not DetectionService.allowed_file(file.filename):
                return None
            
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            file.save(filepath)
            return filepath
            
        except Exception as e:
            logger.error(f"File save failed: {str(e)}")
            return None
    
    @staticmethod
    def process_detection(image_path: str, user_id: int, location: str = None, camera_id: str = None) -> Dict:
        """
        Process face detection on an image with multi-face support.
        
        Multi-Face Detection Enhancement: Detects and matches ALL faces in image,
        not just the first one. Useful for group photos and CCTV footage.
        
        Args:
            image_path: Path to image file
            user_id: ID of user performing detection
            location: Optional location information
            camera_id: Optional camera identifier
            
        Returns:
            Detection results dictionary with multiple matches
        """
        try:
            logger.info(f"Processing detection for image: {image_path}")
            
            # Detect all faces in image
            faces = face_service.detect_faces(image_path)
            logger.info(f"Detected {len(faces)} face(s) in image")
            
            if not faces:
                return {
                    'success': True,
                    'faces_detected': 0,
                    'matches': [],
                    'message': 'No faces detected in image'
                }
            
            # Get all known criminal face encodings with quality scores
            known_encodings = []
            face_encodings = FaceEncoding.query.all()
            logger.info(f"Loading {len(face_encodings)} known face encodings from database")
            
            for fe in face_encodings:
                try:
                    known_encodings.append({
                        'id': fe.id,
                        'criminal_id': fe.criminal_id,
                        'encoding': fe.encoding_data,
                        'quality_score': fe.quality_score or 0.7,
                        'pose_type': fe.pose_type,
                        'is_primary': fe.is_primary
                    })
                except Exception as e:
                    logger.error(f"Error loading encoding {fe.id}: {str(e)}")
                    continue
            
            # Process each detected face
            all_detection_logs = []
            face_match_results = []  # Track matches per face for annotation
            
            for face_idx, face_region in enumerate(faces):
                logger.info(f"Processing face {face_idx + 1}/{len(faces)}")
                
                # Extract encoding for this specific face
                # Note: DeepFace.represent will extract from the first/largest face by default
                # For multi-face, we'd ideally crop to the face region, but for now we process the full image
                # and rely on DeepFace to handle it (it returns embeddings for all detected faces)
                
                try:
                    # For true multi-face support, we should crop the image to face region
                    # But DeepFace.represent actually returns ALL faces, so let's use that
                    import cv2
                    image = cv2.imread(image_path)
                    x, y, w, h = face_region
                    
                    # Crop to face region with some padding
                    padding = 20
                    y1 = max(0, y - padding)
                    y2 = min(image.shape[0], y + h + padding)
                    x1 = max(0, x - padding)
                    x2 = min(image.shape[1], x + w + padding)
                    
                    face_crop = image[y1:y2, x1:x2]
                    
                    # Save temporary cropped face
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        temp_face_path = tmp_file.name
                        cv2.imwrite(temp_face_path, face_crop)
                    
                    # Extract encoding from cropped face
                    encoding = face_service.extract_face_encoding(temp_face_path)
                    
                    # Clean up temp file
                    import os
                    os.remove(temp_face_path)
                    
                    if encoding is None:
                        logger.warning(f"Could not extract encoding for face {face_idx + 1}")
                        face_match_results.append([])  # No matches for this face
                        continue
                    
                    logger.info(f"Extracted {len(encoding)}-D encoding for face {face_idx + 1}")
                    
                    # Find matches for this face
                    matches = face_service.find_matches(encoding, known_encodings)
                    logger.info(f"Found {len(matches)} match(es) for face {face_idx + 1}")
                    
                    # Create detection logs for matches
                    face_matches = []
                    for match in matches:
                        criminal = Criminal.query.get(match['criminal_id'])
                        if not criminal:
                            continue
                        
                        confidence_score = float(match['confidence'])
                        
                        # Auto-verify high-confidence detections (>= 80%)
                        detection_status = 'verified' if confidence_score >= 0.80 else 'pending'
                        
                        # Create detection log
                        detection_log = DetectionLog(
                            criminal_id=match['criminal_id'],
                            confidence_score=confidence_score,
                            location=location,
                            camera_id=camera_id,
                            image_path=image_path,
                            detected_by=user_id,
                            status=detection_status
                        )
                        db.session.add(detection_log)
                        db.session.flush()
                        
                        match_info = {
                            'id': detection_log.id,
                            'criminal_id': criminal.id,
                            'criminal_name': criminal.name,
                            'crime_type': criminal.crime_type,
                            'confidence': confidence_score,
                            'danger_level': criminal.danger_level,
                            'status': criminal.status,
                            'face_index': face_idx,
                            'face_location': face_region
                        }
                        
                        all_detection_logs.append(match_info)
                        face_matches.append(match_info)
                        
                        logger.info(f"  ✓ Face {face_idx + 1} matched: {criminal.name} ({confidence_score:.2%})")
                        
                        # Send email alert for high-confidence matches
                        if confidence_score >= 0.7:
                            try:
                                send_detection_alert(criminal, detection_log, confidence_score)
                            except Exception as e:
                                logger.error(f"Failed to send alert: {str(e)}")
                    
                    face_match_results.append(face_matches)
                    
                except Exception as e:
                    logger.error(f"Error processing face {face_idx + 1}: {str(e)}")
                    face_match_results.append([])
                    continue
            
            db.session.commit()
            
            # Annotate image with ALL detection results
            annotated_path = DetectionService._annotate_multi_face_image(
                image_path, faces, face_match_results
            )
            
            # Summary statistics
            total_faces = len(faces)
            matched_faces = len([f for f in face_match_results if len(f) > 0])
            total_matches = len(all_detection_logs)
            
            return {
                'success': True,
                'faces_detected': total_faces,
                'matched_faces': matched_faces,
                'total_matches': total_matches,
                'matches': all_detection_logs,
                'annotated_image': annotated_path,
                'message': f'Detected {total_faces} face(s), found {total_matches} match(es)'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Detection processing failed: {str(e)}")
            return {
                'success': False,
                'faces_detected': 0,
                'matches': [],
                'message': f'Detection failed: {str(e)}'
            }
    
    @staticmethod
    def _annotate_multi_face_image(image_path: str, faces: List, face_matches: List[List[Dict]]) -> str:
        """
        Annotate image with multiple face detections and matches.
        
        Args:
            image_path: Path to original image
            faces: List of face bounding boxes [(x,y,w,h), ...]
            face_matches: List of match results for each face
            
        Returns:
            Path to annotated image
        """
        try:
            import cv2
            image = cv2.imread(image_path)
            
            for face_idx, ((x, y, w, h), matches) in enumerate(zip(faces, face_matches)):
                if len(matches) > 0:
                    # Green for matches
                    color = (0, 255, 0)
                    best_match = max(matches, key=lambda m: m['confidence'])
                    label = f"{best_match['criminal_name']}: {best_match['confidence']*100:.1f}%"
                else:
                    # Blue for unmatched faces
                    color = (255, 0, 0)
                    label = f"Face {face_idx + 1}: No match"
                
                # Draw rectangle
                cv2.rectangle(image, (x, y), (x+w, y+h), color, 2)
                
                # Draw label background
                (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(image, (x, y-label_h-10), (x+label_w, y), color, -1)
                
                # Draw label text
                cv2.putText(image, label, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Save annotated image
            output_path = image_path.replace('.', '_annotated.')
            cv2.imwrite(output_path, image)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Image annotation failed: {str(e)}")
            return image_path
            
            return {
                'success': True,
                'faces_detected': len(faces),
                'matches': detection_logs,
                'annotated_image': annotated_path,
                'message': f'Detected {len(matches)} potential match(es)' if matches else 'No matches found'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Detection processing failed: {str(e)}")
            return {
                'success': False,
                'faces_detected': 0,
                'matches': [],
                'message': f'Detection failed: {str(e)}'
            }
    
    @staticmethod
    def get_recent_detections(limit: int = 10) -> List[Dict]:
        """
        Get recent detection logs.
        
        Args:
            limit: Maximum number of detections to return
            
        Returns:
            List of detection dictionaries
        """
        try:
            detections = DetectionLog.query\
                .order_by(DetectionLog.detected_at.desc())\
                .limit(limit)\
                .all()
            
            result = []
            for detection in detections:
                criminal = Criminal.query.get(detection.criminal_id)
                result.append({
                    'id': detection.id,
                    'criminal_id': detection.criminal_id,
                    'criminal_name': criminal.name if criminal else 'Unknown',
                    'confidence_score': detection.confidence_score,
                    'detected_at': detection.detected_at.isoformat(),
                    'location': detection.location,
                    'status': detection.status
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get recent detections: {str(e)}")
            return []


# Global instance
detection_service = DetectionService()
