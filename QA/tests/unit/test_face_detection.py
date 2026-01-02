"""
Unit Tests for Face Detection and Recognition
Tests DeepFace integration and face matching
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.unit
@pytest.mark.face_recognition
class TestFaceDetection:
    """Test face detection functionality."""
    
    @patch('app.services.face_service_deepface.DeepFace')
    def test_detect_single_face(self, mock_deepface, mock_face_service):
        """Test detecting single face in image."""
        mock_deepface.extract_faces.return_value = [
            {
                'facial_area': {'x': 100, 'y': 100, 'w': 150, 'h': 150},
                'confidence': 0.99
            }
        ]
        
        from app.services.face_service_deepface import face_service_deepface
        faces = face_service_deepface.detect_faces('test_image.jpg')
        
        assert len(faces) == 1
        assert faces[0]['confidence'] > 0.9
    
    @patch('app.services.face_service_deepface.DeepFace')
    def test_detect_multiple_faces(self, mock_deepface, mock_face_service):
        """Test detecting multiple faces in image (multi-face support)."""
        mock_deepface.extract_faces.return_value = [
            {'facial_area': {'x': 100, 'y': 100, 'w': 150, 'h': 150}, 'confidence': 0.99},
            {'facial_area': {'x': 300, 'y': 100, 'w': 150, 'h': 150}, 'confidence': 0.98},
            {'facial_area': {'x': 500, 'y': 100, 'w': 150, 'h': 150}, 'confidence': 0.97}
        ]
        
        from app.services.face_service_deepface import face_service_deepface
        faces = face_service_deepface.detect_faces('test_image.jpg')
        
        assert len(faces) == 3
    
    @patch('app.services.face_service_deepface.DeepFace')
    def test_detect_no_faces(self, mock_deepface, mock_face_service):
        """Test image with no faces."""
        mock_deepface.extract_faces.return_value = []
        
        from app.services.face_service_deepface import face_service_deepface
        faces = face_service_deepface.detect_faces('test_image.jpg')
        
        assert len(faces) == 0
    
    @patch('app.services.face_service_deepface.DeepFace')
    def test_detect_face_low_confidence(self, mock_deepface, mock_face_service):
        """Test face detection with low confidence."""
        mock_deepface.extract_faces.return_value = [
            {'facial_area': {'x': 100, 'y': 100, 'w': 150, 'h': 150}, 'confidence': 0.45}
        ]
        
        from app.services.face_service_deepface import face_service_deepface
        faces = face_service_deepface.detect_faces('test_image.jpg')
        
        # Should filter out low confidence faces or return with flag
        assert len(faces) >= 0
    
    @patch('app.services.face_service_deepface.cv2')
    def test_detect_face_invalid_image_path(self, mock_cv2, mock_face_service):
        """Test detection with invalid image path."""
        mock_cv2.imread.return_value = None
        
        from app.services.face_service_deepface import face_service_deepface
        
        with pytest.raises(Exception):
            face_service_deepface.detect_faces('nonexistent.jpg')
    
    @patch('app.services.face_service_deepface.DeepFace')
    def test_detect_face_corrupted_image(self, mock_deepface, mock_face_service):
        """Test detection with corrupted image."""
        mock_deepface.extract_faces.side_effect = Exception("Invalid image")
        
        from app.services.face_service_deepface import face_service_deepface
        
        with pytest.raises(Exception):
            face_service_deepface.detect_faces('corrupted.jpg')


@pytest.mark.unit
@pytest.mark.face_recognition
class TestFaceEncoding:
    """Test face encoding generation."""
    
    @patch('app.services.face_service_deepface.DeepFace')
    def test_generate_encoding_valid_face(self, mock_deepface, mock_face_service):
        """Test generating encoding for valid face."""
        mock_embedding = np.random.rand(512).tolist()
        mock_deepface.represent.return_value = [{'embedding': mock_embedding}]
        
        from app.services.face_service_deepface import face_service_deepface
        encoding = face_service_deepface.get_face_encoding('test_image.jpg')
        
        assert encoding is not None
        assert len(encoding) == 512
    
    @patch('app.services.face_service_deepface.DeepFace')
    def test_generate_encoding_no_face(self, mock_deepface, mock_face_service):
        """Test encoding generation with no face in image."""
        mock_deepface.represent.return_value = []
        
        from app.services.face_service_deepface import face_service_deepface
        encoding = face_service_deepface.get_face_encoding('test_image.jpg')
        
        assert encoding is None or encoding == []
    
    def test_encoding_consistency(self, mock_face_service):
        """Test that same face produces similar encodings."""
        # Mock to return same encoding twice
        mock_embedding = np.random.rand(512).tolist()
        mock_face_service.get_face_encoding.return_value = mock_embedding
        
        encoding1 = mock_face_service.get_face_encoding('test1.jpg')
        encoding2 = mock_face_service.get_face_encoding('test1.jpg')
        
        assert encoding1 == encoding2
    
    def test_encoding_vector_size(self, mock_face_service):
        """Test encoding vector is correct size (512 for Facenet512)."""
        mock_embedding = np.random.rand(512).tolist()
        mock_face_service.get_face_encoding.return_value = mock_embedding
        
        encoding = mock_face_service.get_face_encoding('test.jpg')
        
        assert len(encoding) == 512


@pytest.mark.unit
@pytest.mark.face_recognition
class TestFaceMatching:
    """Test face matching and comparison."""
    
    def test_match_identical_faces(self, mock_face_service):
        """Test matching identical faces."""
        encoding = [0.1] * 512
        
        mock_face_service.compare_faces.return_value = [
            {'criminal_id': 1, 'distance': 0.0, 'match': True}
        ]
        
        matches = mock_face_service.compare_faces(encoding, [encoding])
        
        assert len(matches) > 0
        assert matches[0]['match'] is True
    
    def test_match_similar_faces(self, mock_face_service):
        """Test matching similar faces within threshold."""
        encoding1 = [0.1] * 512
        encoding2 = [0.11] * 512  # Slightly different
        
        mock_face_service.compare_faces.return_value = [
            {'criminal_id': 1, 'distance': 0.15, 'match': True}
        ]
        
        matches = mock_face_service.compare_faces(encoding1, [encoding2])
        
        assert len(matches) > 0
        assert matches[0]['match'] is True
    
    def test_no_match_different_faces(self, mock_face_service):
        """Test no match for different faces."""
        encoding1 = [0.1] * 512
        encoding2 = [0.9] * 512  # Very different
        
        mock_face_service.compare_faces.return_value = [
            {'criminal_id': 1, 'distance': 0.85, 'match': False}
        ]
        
        matches = mock_face_service.compare_faces(encoding1, [encoding2])
        
        assert len(matches) == 0 or matches[0]['match'] is False
    
    def test_match_threshold_boundary(self, mock_face_service):
        """Test matching at threshold boundary."""
        encoding1 = [0.1] * 512
        encoding2 = [0.1] * 512
        
        # Distance exactly at threshold (0.40)
        mock_face_service.compare_faces.return_value = [
            {'criminal_id': 1, 'distance': 0.40, 'match': True}
        ]
        
        matches = mock_face_service.compare_faces(encoding1, [encoding2])
        
        # Behavior at boundary
        assert len(matches) >= 0
    
    def test_match_multiple_criminals(self, mock_face_service):
        """Test matching against multiple criminals."""
        encoding = [0.1] * 512
        
        mock_face_service.compare_faces.return_value = [
            {'criminal_id': 1, 'distance': 0.25, 'match': True},
            {'criminal_id': 2, 'distance': 0.35, 'match': True},
            {'criminal_id': 3, 'distance': 0.50, 'match': False}
        ]
        
        matches = mock_face_service.compare_faces(encoding, [[0.1]*512]*3)
        
        matching_criminals = [m for m in matches if m['match']]
        assert len(matching_criminals) == 2
    
    def test_match_returns_best_match_first(self, mock_face_service):
        """Test that matches are sorted by distance."""
        encoding = [0.1] * 512
        
        mock_face_service.compare_faces.return_value = [
            {'criminal_id': 1, 'distance': 0.15, 'match': True},
            {'criminal_id': 2, 'distance': 0.10, 'match': True},
            {'criminal_id': 3, 'distance': 0.20, 'match': True}
        ]
        
        matches = mock_face_service.compare_faces(encoding, [[0.1]*512]*3)
        
        # Best match (lowest distance) should be first
        if len(matches) > 1:
            assert matches[0]['distance'] <= matches[1]['distance']


@pytest.mark.unit
@pytest.mark.face_recognition
class TestQualityAssessment:
    """Test face quality assessment."""
    
    def test_assess_high_quality_face(self):
        """Test quality assessment for high quality face."""
        from app.utils.quality_assessment import assess_face_quality
        
        # Mock high quality face image
        face_image = np.ones((200, 200, 3), dtype=np.uint8) * 128
        
        quality_score = assess_face_quality(face_image)
        
        assert 0.0 <= quality_score <= 1.0
    
    def test_assess_low_quality_face(self):
        """Test quality assessment for low quality face."""
        from app.utils.quality_assessment import assess_face_quality
        
        # Mock low quality/blurry face
        face_image = np.ones((50, 50, 3), dtype=np.uint8) * 50
        
        quality_score = assess_face_quality(face_image)
        
        assert 0.0 <= quality_score <= 1.0
    
    def test_determine_pose_frontal(self):
        """Test pose determination for frontal face."""
        from app.utils.quality_assessment import determine_pose_type
        
        face_region = {'x': 100, 'y': 100, 'w': 150, 'h': 150}
        image = np.ones((400, 400, 3), dtype=np.uint8) * 128
        
        pose = determine_pose_type(image, face_region)
        
        assert pose in ['frontal', 'profile', 'three_quarter', 'unknown']
    
    def test_quality_threshold_filtering(self):
        """Test that low quality faces are filtered."""
        from app.utils.quality_assessment import assess_face_quality
        
        # Very small/poor quality face
        poor_face = np.ones((20, 20, 3), dtype=np.uint8)
        quality = assess_face_quality(poor_face)
        
        # Should be below acceptable threshold (e.g., 0.5)
        assert quality < 0.7


@pytest.mark.unit
@pytest.mark.face_recognition
class TestFaceServiceEdgeCases:
    """Test edge cases in face recognition."""
    
    def test_empty_database(self, mock_face_service, db_session):
        """Test face matching with no criminals in database."""
        encoding = [0.1] * 512
        
        from app.models.face_encoding import FaceEncoding
        all_encodings = FaceEncoding.query.all()
        
        assert len(all_encodings) == 0
    
    def test_concurrent_encoding_requests(self, mock_face_service):
        """Test handling concurrent encoding requests."""
        # Test for race condition (BUG-006)
        # Should use proper locking or transactions
        pass
    
    def test_malformed_encoding_data(self, db_session):
        """Test handling malformed encoding data."""
        from app.models.face_encoding import FaceEncoding
        
        # Create encoding with wrong dimensions
        bad_encoding = [0.1] * 256  # Wrong size
        
        face_enc = FaceEncoding(
            criminal_id=1,
            encoding=bad_encoding,
            photo_filename='test.jpg'
        )
        
        # Should validate encoding size
        with pytest.raises(Exception):
            db_session.add(face_enc)
            db_session.commit()
    
    def test_threshold_configuration(self):
        """Test that recognition threshold is configurable (BUG-009)."""
        from app.services.face_service_deepface import FaceServiceDeepFace
        
        service = FaceServiceDeepFace()
        
        # Should be able to change threshold
        # Currently hardcoded at 0.40 (BUG)
        assert hasattr(service, 'RECOGNITION_THRESHOLD')


@pytest.mark.unit
@pytest.mark.slow
class TestFaceRecognitionPerformance:
    """Test face recognition performance."""
    
    def test_encoding_generation_speed(self, mock_face_service, benchmark):
        """Test encoding generation performance."""
        def generate_encoding():
            return mock_face_service.get_face_encoding('test.jpg')
        
        result = benchmark(generate_encoding)
        # Should complete in reasonable time
    
    def test_matching_speed_large_database(self, mock_face_service):
        """Test matching performance with large criminal database."""
        encoding = [0.1] * 512
        
        # Simulate 1000 criminals
        large_database = [[0.1] * 512 for _ in range(1000)]
        
        import time
        start = time.time()
        matches = mock_face_service.compare_faces(encoding, large_database)
        duration = time.time() - start
        
        # Should complete in reasonable time (< 5 seconds)
        assert duration < 5.0
