"""Production-grade Face Recognition using DeepFace library.

DeepFace is Facebook's face recognition library with 99.65% accuracy.
Uses state-of-the-art deep learning models: VGG-Face, FaceNet, ArcFace, etc.
"""

import cv2
import numpy as np
import os
import pickle
from typing import List, Dict, Tuple, Optional
import logging
from deepface import DeepFace

logger = logging.getLogger(__name__)


class FaceServiceDeepFace:
    """
    Production-grade face recognition using DeepFace.
    
    Supports multiple models:
    - VGG-Face: Fast, 98.95% accuracy
    - Facenet: Balanced, 99.20% accuracy
    - Facenet512: Best, 99.65% accuracy (RECOMMENDED)
    - ArcFace: Latest, 99.41% accuracy
    """
    
    # Model selection - you can change this
    MODEL_NAME = "Facenet512"  # Best accuracy: 99.65%
    # Other options: "VGG-Face", "Facenet", "ArcFace", "DeepFace"
    
    # Distance metric
    DISTANCE_METRIC = "cosine"  # cosine, euclidean, or euclidean_l2
    
    # Recognition threshold (model-specific)
    # TUNED: Increased from 0.30 to 0.40 for better matching across different photos
    THRESHOLDS = {
        "VGG-Face": {"cosine": 0.40, "euclidean": 0.60},
        "Facenet": {"cosine": 0.40, "euclidean": 10},
        "Facenet512": {"cosine": 0.40, "euclidean": 23.56},  # Relaxed from 0.30
        "ArcFace": {"cosine": 0.68, "euclidean": 4.15}
    }
    
    # For compatibility with old code
    RECOGNITION_THRESHOLD = 0.40  # Cosine distance threshold (relaxed for real-world photos)
    
    def __init__(self):
        """Initialize DeepFace service."""
        logger.info(f"Initializing DeepFace with model: {self.MODEL_NAME}")
        logger.info(f"Expected accuracy: {self._get_accuracy()}")
        
        # Pre-load model to avoid first-time delay
        try:
            # This will download model if not present (~100MB first time)
            DeepFace.build_model(self.MODEL_NAME)
            logger.info(f"✓ {self.MODEL_NAME} model loaded successfully")
        except Exception as e:
            logger.error(f"Model loading failed: {str(e)}")
            logger.warning("Model will be downloaded on first use")
    
    def _get_accuracy(self) -> str:
        """Get expected accuracy for current model."""
        accuracies = {
            "VGG-Face": "98.95%",
            "Facenet": "99.20%",
            "Facenet512": "99.65%",
            "ArcFace": "99.41%",
            "DeepFace": "97.35%"
        }
        return accuracies.get(self.MODEL_NAME, "99%+")
    
    def detect_faces(self, image_path: str) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using DeepFace's built-in detector.
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of (x, y, width, height) tuples
        """
        try:
            # DeepFace.extract_faces returns detected faces with coordinates
            faces = DeepFace.extract_faces(
                img_path=image_path,
                detector_backend='opencv',  # Fast and reliable
                enforce_detection=False,     # Don't fail if no face
                align=True                   # Align faces for better recognition
            )
            
            if not faces:
                logger.warning(f"No faces detected in {image_path}")
                return []
            
            # Convert to (x, y, w, h) format
            face_regions = []
            for face in faces:
                region = face['facial_area']
                x, y = region['x'], region['y']
                w, h = region['w'], region['h']
                face_regions.append((x, y, w, h))
            
            logger.info(f"Detected {len(face_regions)} face(s)")
            return face_regions
            
        except Exception as e:
            logger.error(f"Face detection failed: {str(e)}")
            return []
    
    def extract_face_encoding(self, image_path: str) -> Optional[np.ndarray]:
        """
        Extract face embedding using DeepFace.
        
        Returns 128-D (Facenet) or 512-D (Facenet512) or 2622-D (VGG-Face) embedding.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Face embedding as numpy array
        """
        try:
            # DeepFace.represent extracts embeddings
            embedding_objs = DeepFace.represent(
                img_path=image_path,
                model_name=self.MODEL_NAME,
                enforce_detection=False,  # Don't throw error if no face detected
                detector_backend='opencv',
                align=True
            )
            
            if not embedding_objs or len(embedding_objs) == 0:
                logger.warning("No face encoding extracted - no face detected")
                return None
            
            # Get embedding (use first face if multiple detected)
            embedding = embedding_objs[0]["embedding"]
            embedding = np.array(embedding)
            
            logger.info(f"Extracted {len(embedding)}-D embedding using {self.MODEL_NAME}")
            return embedding
            
        except ValueError as e:
            # Face not detected
            logger.warning(f"No face detected in image: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Embedding extraction failed: {str(e)}", exc_info=True)
            return None
    
    def compare_faces(self, known_encoding: np.ndarray, unknown_encoding: np.ndarray) -> Tuple[bool, float]:
        """
        Compare two face embeddings.
        
        Args:
            known_encoding: Reference face embedding
            unknown_encoding: Test face embedding
            
        Returns:
            (is_match, confidence_score) where confidence is 0-1 (1 = identical)
        """
        try:
            # Calculate distance using specified metric
            if self.DISTANCE_METRIC == "cosine":
                # Cosine distance = 1 - cosine similarity
                distance = np.dot(known_encoding, unknown_encoding) / (
                    np.linalg.norm(known_encoding) * np.linalg.norm(unknown_encoding)
                )
                distance = 1 - distance
            elif self.DISTANCE_METRIC == "euclidean":
                distance = np.linalg.norm(known_encoding - unknown_encoding)
            elif self.DISTANCE_METRIC == "euclidean_l2":
                known_norm = known_encoding / np.linalg.norm(known_encoding)
                unknown_norm = unknown_encoding / np.linalg.norm(unknown_encoding)
                distance = np.linalg.norm(known_norm - unknown_norm)
            else:
                # Default to cosine
                distance = np.dot(known_encoding, unknown_encoding) / (
                    np.linalg.norm(known_encoding) * np.linalg.norm(unknown_encoding)
                )
                distance = 1 - distance
            
            # Get threshold for current model and metric
            threshold = self.THRESHOLDS.get(self.MODEL_NAME, {}).get(self.DISTANCE_METRIC, 0.40)
            
            # Check if match
            is_match = distance <= threshold
            
            # Convert distance to confidence (0-1, where 1 is identical)
            # For cosine: distance 0 = identical (confidence 1), distance 1 = different (confidence 0)
            if self.DISTANCE_METRIC == "cosine":
                confidence = 1 - distance
            else:
                # For euclidean: normalize based on threshold
                confidence = max(0, 1 - (distance / (threshold * 2)))
            
            confidence = np.clip(confidence, 0.0, 1.0)
            
            logger.debug(f"Distance: {distance:.4f}, Threshold: {threshold:.4f}, "
                        f"Confidence: {confidence:.4f}, Match: {is_match}")
            
            return is_match, float(confidence)
            
        except Exception as e:
            logger.error(f"Face comparison failed: {str(e)}")
            return False, 0.0
    
    def find_matches(self, unknown_encoding: np.ndarray, known_encodings: List[Dict]) -> List[Dict]:
        """
        Find matching faces from known encodings using ensemble matching.
        
        Phase 2 Enhancement: Multiple photos per criminal
        - Groups encodings by criminal_id
        - Compares against all photos of each criminal
        - Uses minimum distance (best match) strategy
        - Returns matches with adaptive thresholds based on quality
        
        Args:
            unknown_encoding: Face embedding to match
            known_encodings: List of dicts with 'criminal_id', 'encoding', 'quality_score'
            
        Returns:
            List of matches sorted by confidence
        """
        # Group encodings by criminal_id for ensemble matching
        criminal_encodings = {}
        for known in known_encodings:
            crim_id = known['criminal_id']
            if crim_id not in criminal_encodings:
                criminal_encodings[crim_id] = []
            criminal_encodings[crim_id].append(known)
        
        matches = []
        
        for criminal_id, encodings in criminal_encodings.items():
            try:
                # Compare against all photos of this criminal
                best_match = None
                best_confidence = 0.0
                best_distance = float('inf')
                
                for known in encodings:
                    # Deserialize encoding
                    if isinstance(known['encoding'], bytes):
                        encoding = pickle.loads(known['encoding'])
                    else:
                        encoding = known['encoding']
                    
                    # Calculate distance
                    if self.DISTANCE_METRIC == "cosine":
                        similarity = np.dot(encoding, unknown_encoding) / (
                            np.linalg.norm(encoding) * np.linalg.norm(unknown_encoding)
                        )
                        distance = 1 - similarity
                    elif self.DISTANCE_METRIC == "euclidean":
                        distance = np.linalg.norm(encoding - unknown_encoding)
                    else:
                        # Default to cosine
                        similarity = np.dot(encoding, unknown_encoding) / (
                            np.linalg.norm(encoding) * np.linalg.norm(unknown_encoding)
                        )
                        distance = 1 - similarity
                    
                    # Convert distance to confidence
                    if self.DISTANCE_METRIC == "cosine":
                        confidence = 1 - distance
                    else:
                        threshold = self.THRESHOLDS.get(self.MODEL_NAME, {}).get(self.DISTANCE_METRIC, 0.40)
                        confidence = max(0, 1 - (distance / (threshold * 2)))
                    
                    # Track best match (minimum distance)
                    if distance < best_distance:
                        best_distance = distance
                        best_confidence = confidence
                        best_match = known
                
                # Apply adaptive threshold based on quality
                quality_score = best_match.get('quality_score', 0.7) if best_match else 0.7
                threshold = self._get_adaptive_threshold(quality_score)
                
                # Check if best match passes threshold
                if best_distance <= threshold:
                    matches.append({
                        'criminal_id': criminal_id,
                        'confidence': float(np.clip(best_confidence, 0.0, 1.0)),
                        'face_encoding_id': best_match.get('id') if best_match else None,
                        'distance': float(best_distance),
                        'num_photos_compared': len(encodings),
                        'quality_score': quality_score
                    })
                    logger.info(f"✓ Match: Criminal {criminal_id}, "
                              f"Confidence: {best_confidence:.2%}, "
                              f"Distance: {best_distance:.4f}, "
                              f"Photos compared: {len(encodings)}")
                    
            except Exception as e:
                logger.error(f"Error comparing with criminal {criminal_id}: {str(e)}")
                continue
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        return matches
    
    def _get_adaptive_threshold(self, quality_score: float) -> float:
        """
        Calculate adaptive recognition threshold based on image quality.
        Phase 3 Enhancement: Quality-based threshold adjustment.
        
        Args:
            quality_score: Quality score from assess_face_quality (0.0-1.0)
            
        Returns:
            Adjusted threshold for face matching
        """
        base_threshold = self.THRESHOLDS.get(self.MODEL_NAME, {}).get(self.DISTANCE_METRIC, 0.40)
        
        if quality_score >= 0.8:
            # High quality - can use strict threshold
            return base_threshold - 0.05
        elif quality_score >= 0.6:
            # Good quality - use base threshold
            return base_threshold
        elif quality_score >= 0.4:
            # Medium quality - slightly more lenient
            return base_threshold + 0.05
        else:
            # Low quality - more lenient
            return base_threshold + 0.10
    
    def save_encoding(self, encoding: np.ndarray) -> bytes:
        """Serialize encoding for database storage."""
        return pickle.dumps(encoding)
    
    def load_encoding(self, encoding_bytes: bytes) -> np.ndarray:
        """Deserialize encoding from database."""
        return pickle.loads(encoding_bytes)
    
    def annotate_image(self, image_path: str, faces: List[Tuple], matches: List[Dict] = None) -> str:
        """
        Draw bounding boxes on detected faces.
        
        Args:
            image_path: Path to image
            faces: List of face bounding boxes
            matches: Optional list of match results
            
        Returns:
            Path to annotated image
        """
        try:
            image = cv2.imread(image_path)
            
            for i, (x, y, w, h) in enumerate(faces):
                if matches and i < len(matches):
                    # Green for matches
                    color = (0, 255, 0)
                    confidence = matches[i]['confidence']
                    label = f"Match: {confidence*100:.1f}%"
                else:
                    # Blue for unmatched faces
                    color = (255, 0, 0)
                    label = "No match"
                
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


# Global instance
face_service_deepface = FaceServiceDeepFace()
