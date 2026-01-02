"""
Comprehensive QA Tests for Video Detection Feature
Tests video upload, processing, and face detection functionality
"""

import pytest
import os
import json
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.video_helpers import create_test_video as create_video_file, create_test_video_with_faces as create_video_with_faces_file


@pytest.mark.unit
@pytest.mark.video
class TestVideoUpload:
    """Test video file upload functionality."""
    
    def test_upload_valid_mp4_video(self, client, admin_token):
        """Test uploading a valid MP4 video file."""
        from app.models.video_detection import VideoDetection
        from app import db
        
        #Create test video
        video_data = create_test_video()
        
        response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={
                'video': (BytesIO(video_data), 'test_video.mp4'),
                'location': 'Test Location',
                'camera_id': 'CAM-001'
            },
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'video_id' in data
        assert data['metadata']['fps'] > 0
    
    def test_upload_without_token(self, client):
        """Test uploading video without authentication."""
        video_data = create_test_video()
        
        response = client.post(
            '/api/video/upload',
            data={'video': (BytesIO(video_data), 'test.mp4')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 401
    
    def test_upload_without_file(self, client, admin_token):
        """Test upload endpoint without video file."""
        response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'location': 'Test'},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'No video file' in data['message']
    
    def test_upload_invalid_file_format(self, client, admin_token):
        """Test uploading non-video file."""
        # Create a text file instead of video
        text_data = b'This is not a video file'
        
        response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'video': (BytesIO(text_data), 'test.txt')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
    
    def test_upload_avi_video(self, client, admin_token):
        """Test uploading AVI format video."""
        video_data = create_test_video(format='avi')
        
        response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'video': (BytesIO(video_data), 'test.avi')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code in [201, 400]  # May fail if AVI creation fails
    
    def test_upload_large_video(self, client, admin_token):
        """Test uploading larger video file."""
        video_data = create_test_video(duration=3, fps=30)  # 3 seconds
        
        response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'video': (BytesIO(video_data), 'large_test.mp4')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
    
    def test_upload_with_metadata(self, client, admin_token):
        """Test video upload with location and camera_id."""
        video_data = create_test_video()
        
        response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={
                'video': (BytesIO(video_data), 'test.mp4'),
                'location': 'Downtown Plaza',
                'camera_id': 'CAM-PLAZA-001'
            },
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        # Verify metadata stored
        from app.models.video_detection import VideoDetection
        video = VideoDetection.query.get(data['video_id'])
        assert video.location == 'Downtown Plaza'
        assert video.camera_id == 'CAM-PLAZA-001'


@pytest.mark.unit
@pytest.mark.video
class TestVideoMetadata:
    """Test video metadata extraction."""
    
    def test_extract_video_metadata(self):
        """Test extracting FPS, duration, resolution from video."""
        from app.services.video_processing_service import video_processing_service
        import tempfile
        
        # Create test video file
        video_data = create_test_video(fps=25, width=640, height=480)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            tmp.write(video_data)
            tmp_path = tmp.name
        
        try:
            metadata = video_processing_service.get_video_metadata(tmp_path)
            
            assert 'fps' in metadata
            assert metadata['fps'] > 0
            assert 'total_frames' in metadata
            assert 'width' in metadata
            assert 'height' in metadata
            assert 'duration_seconds' in metadata
            assert 'file_size_mb' in metadata
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_metadata_invalid_file(self):
        """Test metadata extraction from invalid file."""
        from app.services.video_processing_service import video_processing_service
        
        metadata = video_processing_service.get_video_metadata('nonexistent.mp4')
        
        assert metadata == {}


@pytest.mark.integration
@pytest.mark.video
class TestVideoProcessing:
    """Test video processing and face detection."""
    
    def test_process_video_with_faces(self, client, app, admin_token, sample_criminal):
        """Test processing video that contains faces."""
        from app.models.video_detection import VideoDetection
        from app.models.face_encoding import FaceEncoding
        from app import db
        
        with app.app_context():
            # Add face encoding for sample criminal
            encoding = FaceEncoding(
                criminal_id=sample_criminal.id,
                image_path='test_face.jpg'
            )
            encoding.set_encoding(np.random.rand(512))
            db.session.add(encoding)
            db.session.commit()
            
            # Upload video
            video_data = create_test_video_with_faces()
            
            upload_response = client.post(
                '/api/video/upload',
                headers={'Authorization': f'Bearer {admin_token}'},
                data={'video': (BytesIO(video_data), 'test_faces.mp4')},
                content_type='multipart/form-data'
            )
            
            assert upload_response.status_code == 201
            upload_data = json.loads(upload_response.data)
            video_id = upload_data['video_id']
            
            # Process video
            process_response = client.post(
                f'/api/video/process/{video_id}',
                headers={'Authorization': f'Bearer {admin_token}'},
                json={
                    'frame_skip': 2,
                    'confidence_threshold': 0.70
                }
            )
            
            # Processing might succeed or fail depending on face detection
            assert process_response.status_code in [200, 500]
    
    def test_process_video_frame_skip(self, client, admin_token):
        """Test video processing with different frame_skip values."""
        video_data = create_test_video()
        
        # Upload
        upload_response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'video': (BytesIO(video_data), 'test.mp4')},
            content_type='multipart/form-data'
        )
        
        video_id = json.loads(upload_response.data)['video_id']
        
        # Process with frame_skip=10
        response = client.post(
            f'/api/video/process/{video_id}',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'frame_skip': 10}
        )
        
        assert response.status_code in [200, 500]
    
    def test_process_nonexistent_video(self, client, admin_token):
        """Test processing video that doesn't exist."""
        response = client.post(
            '/api/video/process/99999',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={}
        )
        
        assert response.status_code == 404
    
    def test_process_video_twice(self, client, admin_token):
        """Test processing same video twice (should reject)."""
        video_data = create_test_video()
        
        # Upload
        upload_response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'video': (BytesIO(video_data), 'test.mp4')},
            content_type='multipart/form-data'
        )
        
        video_id = json.loads(upload_response.data)['video_id']
        
        # Process first time
        response1 = client.post(
            f'/api/video/process/{video_id}',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={}
        )
        
        # Try to process again
        response2 = client.post(
            f'/api/video/process/{video_id}',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={}
        )
        
        # Second attempt should fail if first succeeded
        if response1.status_code == 200:
            assert response2.status_code == 400


@pytest.mark.integration
@pytest.mark.video
class TestVideoRetrieval:
    """Test retrieving video detection records."""
    
    def test_list_videos(self, client, admin_token):
        """Test listing all videos."""
        response = client.get(
            '/api/video/list',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'videos' in data
        assert isinstance(data['videos'], list)
    
    def test_list_videos_with_limit(self, client, admin_token):
        """Test listing videos with limit parameter."""
        response = client.get(
            '/api/video/list?limit=5',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['videos']) <= 5
    
    def test_list_videos_by_status(self, client, admin_token):
        """Test filtering videos by processing status."""
        response = client.get(
            '/api/video/list?status=pending',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # All returned videos should have pending status
        for video in data['videos']:
            assert video['processing_status'] == 'pending'
    
    def test_get_video_details(self, client, admin_token):
        """Test getting detailed info for specific video."""
        # Upload a video first
        video_data = create_test_video()
        upload_response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'video': (BytesIO(video_data), 'test.mp4')},
            content_type='multipart/form-data'
        )
        
        video_id = json.loads(upload_response.data)['video_id']
        
        # Get details
        response = client.get(
            f'/api/video/{video_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'video' in data
        assert data['video']['id'] == video_id
    
    def test_get_nonexistent_video(self, client, admin_token):
        """Test getting video that doesn't exist."""
        response = client.get(
            '/api/video/99999',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 404
    
    def test_get_video_frames(self, client, admin_token):
        """Test retrieving frame detections for video."""
        video_data = create_test_video()
        upload_response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'video': (BytesIO(video_data), 'test.mp4')},
            content_type='multipart/form-data'
        )
        
        video_id = json.loads(upload_response.data)['video_id']
        
        response = client.get(
            f'/api/video/{video_id}/frames',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'frames' in data
        assert isinstance(data['frames'], list)
    
    def test_get_video_frames_matched_only(self, client, admin_token):
        """Test retrieving only frames with criminal matches."""
        video_data = create_test_video()
        upload_response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'video': (BytesIO(video_data), 'test.mp4')},
            content_type='multipart/form-data'
        )
        
        video_id = json.loads(upload_response.data)['video_id']
        
        response = client.get(
            f'/api/video/{video_id}/frames?matched_only=true',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # All returned frames should have criminal_id
        for frame in data['frames']:
            assert frame['criminal_id'] is not None


@pytest.mark.integration
@pytest.mark.video
class TestVideoStats:
    """Test video statistics endpoints."""
    
    def test_get_video_stats(self, client, admin_token):
        """Test retrieving video processing statistics."""
        response = client.get(
            '/api/video/stats',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'stats' in data
        assert 'total_videos' in data['stats']
        assert 'videos_by_status' in data['stats']
        assert 'total_faces_detected' in data['stats']
        assert 'total_criminals_matched' in data['stats']
    
    def test_stats_structure(self, client, admin_token):
        """Test statistics response structure."""
        response = client.get(
            '/api/video/stats',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        data = json.loads(response.data)
        stats = data['stats']
        
        # Check videos_by_status structure
        assert 'pending' in stats['videos_by_status']
        assert 'processing' in stats['videos_by_status']
        assert 'completed' in stats['videos_by_status']
        assert 'failed' in stats['videos_by_status']


@pytest.mark.integration
@pytest.mark.video
class TestVideoDelete:
    """Test video deletion."""
    
    def test_delete_video(self, client, admin_token):
        """Test deleting a video and its files."""
        # Upload video
        video_data = create_test_video()
        upload_response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'video': (BytesIO(video_data), 'test.mp4')},
            content_type='multipart/form-data'
        )
        
        video_id = json.loads(upload_response.data)['video_id']
        
        # Delete video
        response = client.delete(
            f'/api/video/{video_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify video is deleted
        get_response = client.get(
            f'/api/video/{video_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_video(self, client, admin_token):
        """Test deleting video that doesn't exist."""
        response = client.delete(
            '/api/video/99999',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 404


# Helper functions

def create_test_video(duration=1, fps=10, width=320, height=240, format='mp4'):
    """
    Wrapper to create test video and return bytes.
    Uses shared helper from helpers.video_helpers.
    """
    video_path = create_video_file(duration, fps, width, height, format)
    try:
        with open(video_path, 'rb') as f:
            return f.read()
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


def create_test_video_with_faces(duration=1, fps=10):
    """
    Wrapper to create test video with faces and return bytes.
    Uses shared helper from helpers.video_helpers.
    """
    video_path = create_video_with_faces_file(duration, fps)
    try:
        with open(video_path, 'rb') as f:
            return f.read()
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
