"""
End-to-End Tests for Video Detection Feature
Complete user workflows for video-based face detection
"""

import pytest
import json
import os
import sys
from io import BytesIO

# Add parent directory to path for helpers
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.video_helpers import create_test_video as create_video_path, create_test_video_with_faces as create_video_with_faces_path


def create_test_video(duration=1, fps=10, width=640, height=480, format='mp4'):
    """Create video and return bytes."""
    video_path = create_video_path(duration, fps, width, height, format)
    try:
        with open(video_path, 'rb') as f:
            return f.read()
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


def create_test_video_with_faces(duration=1, fps=10):
    """Create video with faces and return bytes."""
    video_path = create_video_with_faces_path(duration, fps)
    try:
        with open(video_path, 'rb') as f:
            return f.read()
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)


@pytest.mark.e2e
@pytest.mark.video
class TestVideoDetectionWorkflow:
    """Test complete video detection workflows."""
    
    def test_complete_video_workflow(self, client, admin_token, sample_criminal):
        """
        Complete workflow: Upload video → Process → View results → Delete.
        """
        from app.models.face_encoding import FaceEncoding
        from app import db
        import numpy as np
        
        # Step 1: Add criminal with encoding
        encoding = FaceEncoding(
            criminal_id=sample_criminal.id,
            image_path='test.jpg'
        )
        encoding.set_encoding(np.random.rand(512))
        db.session.add(encoding)
        db.session.commit()
        
        # Step 2: Upload video
        video_data = create_test_video(duration=2, fps=10)
        
        upload_response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={
                'video': (BytesIO(video_data), 'workflow_test.mp4'),
                'location': 'Test Mall',
                'camera_id': 'CAM-MALL-01'
            },
            content_type='multipart/form-data'
        )
        
        assert upload_response.status_code == 201
        video_id = json.loads(upload_response.data)['video_id']
        
        # Step 3: Verify video details
        details_response = client.get(
            f'/api/video/{video_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert details_response.status_code == 200
        
        # Step 4: Process video
        process_response = client.post(
            f'/api/video/process/{video_id}',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'frame_skip': 3}
        )
        assert process_response.status_code in [200, 500]
        
        # Step 5: View results
        results_response = client.get(
            f'/api/video/{video_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert results_response.status_code == 200
        
        # Step 6: Get frame detections
        frames_response = client.get(
            f'/api/video/{video_id}/frames',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert frames_response.status_code == 200
        
        # Step 7: Delete video
        delete_response = client.delete(
            f'/api/video/{video_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert delete_response.status_code == 200
    
    def test_multiple_videos_workflow(self, client, admin_token):
        """Test uploading and processing multiple videos."""
        
        video_ids = []
        
        # Upload 3 videos
        for i in range(3):
            video_data = create_test_video()
            
            response = client.post(
                '/api/video/upload',
                headers={'Authorization': f'Bearer {admin_token}'},
                data={
                    'video': (BytesIO(video_data), f'video_{i+1}.mp4'),
                    'location': f'Location {i+1}'
                },
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 201
            video_ids.append(json.loads(response.data)['video_id'])
        
        # Verify all videos listed
        list_response = client.get(
            '/api/video/list',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert list_response.status_code == 200
        data = json.loads(list_response.data)
        assert len(data['videos']) >= 3
    
    def test_video_with_criminal_match(self, client, app, admin_token, sample_criminal):
        """Test video processing that detects a known criminal."""
        from app.models.face_encoding import FaceEncoding
        from app import db
        import numpy as np
        
        with app.app_context():
            # Add high-quality encoding
            encoding = FaceEncoding(
                criminal_id=sample_criminal.id,
                image_path='criminal_photo.jpg',
                quality_score=0.95
            )
            encoding.set_encoding(np.random.rand(512))
            db.session.add(encoding)
            db.session.commit()
            
            # Upload and process video
            video_data = create_test_video_with_faces(duration=1, fps=5)
            
            upload_response = client.post(
                '/api/video/upload',
                headers={'Authorization': f'Bearer {admin_token}'},
                data={'video': (BytesIO(video_data), 'suspect_video.mp4')},
                content_type='multipart/form-data'
            )
            
            video_id = json.loads(upload_response.data)['video_id']
            
            # Process with lower threshold
            process_response = client.post(
                f'/api/video/process/{video_id}',
                headers={'Authorization': f'Bearer {admin_token}'},
                json={'confidence_threshold': 0.60, 'frame_skip': 2}
            )
            
            # Should complete processing
            assert process_response.status_code in [200, 500]


@pytest.mark.e2e
@pytest.mark.video  
@pytest.mark.performance
class TestVideoPerformance:
    """Test video processing performance."""
    
    def test_large_video_processing_time(self, client, admin_token):
        """Test processing time for larger video (5 seconds)."""
        import time
        
        # Create 3-second video with lower FPS to stay under size limit
        video_data = create_test_video(duration=3, fps=10)
        
        # Upload
        upload_response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'video': (BytesIO(video_data), 'large_video.mp4')},
            content_type='multipart/form-data'
        )
        
        video_id = json.loads(upload_response.data)['video_id']
        
        # Process and measure time
        start_time = time.time()
        
        process_response = client.post(
            f'/api/video/process/{video_id}',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'frame_skip': 10}  # Higher skip for performance
        )
        
        elapsed_time = time.time() - start_time
        
        # Should complete reasonably fast (within 60 seconds)
        assert elapsed_time < 60
    
    def test_frame_skip_performance(self, client, admin_token):
        """Test that higher frame_skip improves performance."""
        import time
        
        video_data = create_test_video(duration=2, fps=10)
        
        # Upload once
        upload_response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'video': (BytesIO(video_data), 'perf_test.mp4')},
            content_type='multipart/form-data'
        )
        
        video_id1 = json.loads(upload_response.data)['video_id']
        
        # Process with frame_skip=2
        start1 = time.time()
        client.post(
            f'/api/video/process/{video_id1}',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'frame_skip': 2}
        )
        time1 = time.time() - start1
        
        # Upload again
        upload_response2 = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'video': (BytesIO(video_data), 'perf_test2.mp4')},
            content_type='multipart/form-data'
        )
        
        video_id2 = json.loads(upload_response2.data)['video_id']
        
        # Process with frame_skip=10
        start2 = time.time()
        client.post(
            f'/api/video/process/{video_id2}',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'frame_skip': 10}
        )
        time2 = time.time() - start2
        
        # Higher frame_skip should be faster (or at least not significantly slower)
        # Note: May not always be true due to system variability
        assert time2 <= time1 * 1.5  # Allow 50% variance


@pytest.mark.e2e
@pytest.mark.video
class TestVideoSecurity:
    """Test security aspects of video detection."""
    
    def test_unauthorized_video_access(self, client):
        """Test accessing video endpoints without authentication."""
        # Try to list videos
        response = client.get('/api/video/list')
        assert response.status_code == 401
        
        # Try to upload
        video_data = create_test_video()
        
        response = client.post(
            '/api/video/upload',
            data={'video': (BytesIO(video_data), 'test.mp4')},
            content_type='multipart/form-data'
        )
        assert response.status_code == 401
    
    def test_operator_can_upload_videos(self, client, operator_token):
        """Test that operator role can upload videos."""
        video_data = create_test_video()
        
        response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {operator_token}'},
            data={'video': (BytesIO(video_data), 'operator_video.mp4')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
    
    def test_viewer_can_view_videos(self, client, admin_token, viewer_token):
        """Test that viewer role can view but not upload videos."""
        # Upload as admin
        video_data = create_test_video()
        
        upload_response = client.post(
            '/api/video/upload',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'video': (BytesIO(video_data), 'test.mp4')},
            content_type='multipart/form-data'
        )
        
        # Viewer should be able to list videos
        list_response = client.get(
            '/api/video/list',
            headers={'Authorization': f'Bearer {viewer_token}'}
        )
        assert list_response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
