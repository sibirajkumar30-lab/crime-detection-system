"""Face quality assessment utilities for Phase 3."""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional


def assess_face_quality(image_path: str, face_box: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, float]:
    """
    Assess the quality of a face image based on multiple factors.
    
    Args:
        image_path: Path to the image file
        face_box: Optional (x, y, w, h) bounding box of the face
        
    Returns:
        Dictionary with quality metrics:
        - blur_score: 0.0-1.0 (higher is sharper)
        - brightness_score: 0.0-1.0 (optimal around 0.5)
        - size_score: 0.0-1.0 (larger faces score higher)
        - frontality_score: 0.0-1.0 (frontal faces score higher)
        - overall_score: 0.0-1.0 (weighted average)
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return _default_quality_scores()
        
        # If face box provided, crop to face region
        if face_box:
            x, y, w, h = face_box
            face_img = img[y:y+h, x:x+w]
        else:
            face_img = img
        
        # 1. Blur Assessment (Laplacian variance)
        blur_score = assess_blur(face_img)
        
        # 2. Brightness Assessment
        brightness_score = assess_brightness(face_img)
        
        # 3. Size Assessment
        size_score = assess_size(face_img)
        
        # 4. Frontality Assessment (simplified - uses eye detection)
        frontality_score = assess_frontality(face_img)
        
        # 5. Calculate Overall Score (weighted average)
        overall_score = (
            0.30 * blur_score +        # 30% weight on sharpness
            0.20 * brightness_score +  # 20% weight on brightness
            0.25 * size_score +        # 25% weight on face size
            0.25 * frontality_score    # 25% weight on frontality
        )
        
        return {
            'blur_score': round(blur_score, 3),
            'brightness_score': round(brightness_score, 3),
            'size_score': round(size_score, 3),
            'frontality_score': round(frontality_score, 3),
            'overall_score': round(overall_score, 3)
        }
        
    except Exception as e:
        print(f"Error assessing quality: {str(e)}")
        return _default_quality_scores()


def assess_blur(face_img: np.ndarray) -> float:
    """
    Assess image sharpness using Laplacian variance.
    Higher variance = sharper image.
    
    Args:
        face_img: Face image as numpy array
        
    Returns:
        Blur score 0.0-1.0 (higher is better)
    """
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Normalize: variance typically ranges from 0-500 for faces
    # Good quality: > 100, Poor quality: < 50
    normalized = min(laplacian_var / 200.0, 1.0)
    return float(normalized)


def assess_brightness(face_img: np.ndarray) -> float:
    """
    Assess image brightness. Optimal brightness is around 110-150 (out of 255).
    
    Args:
        face_img: Face image as numpy array
        
    Returns:
        Brightness score 0.0-1.0 (higher is better)
    """
    # Convert to grayscale
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
    
    # Calculate mean brightness
    mean_brightness = np.mean(gray)
    
    # Optimal brightness is 110-150
    # Score based on distance from optimal range
    optimal_min, optimal_max = 110, 150
    
    if optimal_min <= mean_brightness <= optimal_max:
        score = 1.0
    elif mean_brightness < optimal_min:
        # Too dark
        score = max(0.0, mean_brightness / optimal_min)
    else:
        # Too bright
        score = max(0.0, 1.0 - (mean_brightness - optimal_max) / (255 - optimal_max))
    
    return float(score)


def assess_size(face_img: np.ndarray) -> float:
    """
    Assess face size. Larger faces generally have more detail.
    
    Args:
        face_img: Face image as numpy array
        
    Returns:
        Size score 0.0-1.0 (higher is better)
    """
    height, width = face_img.shape[:2]
    face_pixels = height * width
    
    # Optimal size: >= 100x100 pixels
    # Minimum acceptable: 50x50 pixels
    optimal_pixels = 100 * 100
    min_pixels = 50 * 50
    
    if face_pixels >= optimal_pixels:
        score = 1.0
    elif face_pixels < min_pixels:
        score = 0.3  # Minimum score for very small faces
    else:
        # Linear interpolation between min and optimal
        score = 0.3 + 0.7 * (face_pixels - min_pixels) / (optimal_pixels - min_pixels)
    
    return float(score)


def assess_frontality(face_img: np.ndarray) -> float:
    """
    Assess if face is frontal using eye detection.
    Frontal faces have both eyes visible and horizontally aligned.
    
    Args:
        face_img: Face image as numpy array
        
    Returns:
        Frontality score 0.0-1.0 (higher is better, 1.0 = frontal)
    """
    try:
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
        
        # Load eye cascade classifier
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Detect eyes
        eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20))
        
        num_eyes = len(eyes)
        
        if num_eyes >= 2:
            # Both eyes detected - likely frontal
            # Check if eyes are horizontally aligned
            eye1_y = eyes[0][1] + eyes[0][3] // 2
            eye2_y = eyes[1][1] + eyes[1][3] // 2
            vertical_diff = abs(eye1_y - eye2_y)
            
            # If eyes are within 20% of face height, consider frontal
            face_height = face_img.shape[0]
            if vertical_diff < face_height * 0.2:
                return 1.0  # Frontal face
            else:
                return 0.7  # Slightly tilted
        elif num_eyes == 1:
            # Only one eye visible - profile view
            return 0.5
        else:
            # No eyes detected - could be poor quality or extreme angle
            return 0.3
            
    except Exception as e:
        # If eye detection fails, return neutral score
        return 0.6


def determine_pose_type(frontality_score: float) -> str:
    """
    Determine pose type based on frontality score.
    
    Args:
        frontality_score: Score from assess_frontality (0.0-1.0)
        
    Returns:
        Pose type: 'frontal', 'three_quarter', 'profile', or 'unknown'
    """
    if frontality_score >= 0.8:
        return 'frontal'
    elif frontality_score >= 0.6:
        return 'three_quarter'
    elif frontality_score >= 0.4:
        return 'profile'
    else:
        return 'unknown'


def get_adaptive_threshold(overall_quality: float, base_threshold: float = 0.40) -> float:
    """
    Calculate adaptive recognition threshold based on image quality.
    Lower quality images need more lenient thresholds.
    
    Args:
        overall_quality: Quality score from assess_face_quality (0.0-1.0)
        base_threshold: Base recognition threshold (default 0.40)
        
    Returns:
        Adjusted threshold for face matching
    """
    if overall_quality >= 0.8:
        # High quality - can use strict threshold
        return base_threshold - 0.05  # 0.35 for high quality
    elif overall_quality >= 0.6:
        # Good quality - use base threshold
        return base_threshold  # 0.40
    elif overall_quality >= 0.4:
        # Medium quality - slightly more lenient
        return base_threshold + 0.05  # 0.45
    else:
        # Low quality - more lenient
        return base_threshold + 0.10  # 0.50


def _default_quality_scores() -> Dict[str, float]:
    """Return default quality scores when assessment fails."""
    return {
        'blur_score': 0.5,
        'brightness_score': 0.5,
        'size_score': 0.5,
        'frontality_score': 0.5,
        'overall_score': 0.5
    }


# Example usage
if __name__ == '__main__':
    # Test quality assessment
    test_image = "test_face.jpg"
    quality = assess_face_quality(test_image)
    print("Quality Assessment:")
    for metric, score in quality.items():
        print(f"  {metric}: {score}")
    
    pose = determine_pose_type(quality['frontality_score'])
    print(f"\nPose Type: {pose}")
    
    threshold = get_adaptive_threshold(quality['overall_score'])
    print(f"Adaptive Threshold: {threshold}")
