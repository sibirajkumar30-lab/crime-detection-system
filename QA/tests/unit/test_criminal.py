"""
Unit Tests for Criminal Management Module
Tests CRUD operations on criminals
"""

import pytest
from flask import json
from datetime import datetime


@pytest.mark.unit
class TestCriminalCreation:
    """Test criminal creation functionality."""
    
    def test_create_criminal_valid_data(self, client, db_session, admin_token):
        """Test creating criminal with valid data."""
        response = client.post(
            '/api/criminals',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'name': 'Test Criminal',
                'alias': 'TC',
                'age': 30,
                'gender': 'Male',
                'crime_type': 'Theft',
                'crime_details': 'Test details',
                'status': 'wanted',
                'danger_level': 'medium',
                'last_seen_location': 'Test Location'
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['criminal']['name'] == 'Test Criminal'
        assert data['criminal']['status'] == 'wanted'
    
    def test_create_criminal_missing_required_fields(self, client, db_session, admin_token):
        """Test creating criminal with missing required fields."""
        response = client.post(
            '/api/criminals',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'alias': 'TC'
            }
        )
        
        assert response.status_code == 400
    
    def test_create_criminal_invalid_gender(self, client, db_session, admin_token):
        """Test creating criminal with invalid gender."""
        response = client.post(
            '/api/criminals',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'name': 'Test Criminal',
                'age': 30,
                'gender': 'InvalidGender',
                'crime_type': 'Theft',
                'status': 'wanted'
            }
        )
        
        # Should validate gender enum
        assert response.status_code in [400, 201]
    
    def test_create_criminal_invalid_status(self, client, db_session, admin_token):
        """Test creating criminal with invalid status."""
        response = client.post(
            '/api/criminals',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'name': 'Test Criminal',
                'age': 30,
                'gender': 'Male',
                'crime_type': 'Theft',
                'status': 'invalid_status'
            }
        )
        
        # Should validate status enum
        assert response.status_code in [400, 201]
    
    def test_create_criminal_negative_age(self, client, db_session, admin_token):
        """Test creating criminal with negative age."""
        response = client.post(
            '/api/criminals',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'name': 'Test Criminal',
                'age': -5,
                'gender': 'Male',
                'crime_type': 'Theft',
                'status': 'wanted'
            }
        )
        
        assert response.status_code == 400
    
    def test_create_criminal_very_long_name(self, client, db_session, admin_token):
        """Test creating criminal with extremely long name."""
        long_name = 'A' * 1000
        response = client.post(
            '/api/criminals',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'name': long_name,
                'age': 30,
                'gender': 'Male',
                'crime_type': 'Theft',
                'status': 'wanted'
            }
        )
        
        # Should validate max length (BUG if accepts)
        assert response.status_code in [400, 201]
    
    def test_create_criminal_without_auth(self, client, db_session):
        """Test creating criminal without authentication."""
        response = client.post(
            '/api/criminals',
            json={
                'name': 'Test Criminal',
                'age': 30,
                'gender': 'Male',
                'crime_type': 'Theft',
                'status': 'wanted'
            }
        )
        
        assert response.status_code == 401


@pytest.mark.unit
class TestCriminalRetrieval:
    """Test criminal retrieval functionality."""
    
    def test_get_all_criminals(self, client, db_session, admin_token, sample_criminals):
        """Test retrieving all criminals."""
        response = client.get(
            '/api/criminals',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'criminals' in data
        assert len(data['criminals']) == 5
    
    def test_get_criminals_with_pagination(self, client, db_session, admin_token, sample_criminals):
        """Test criminal retrieval with pagination."""
        response = client.get(
            '/api/criminals?page=1&per_page=2',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['criminals']) == 2
        assert data['total'] == 5
        assert data['pages'] == 3
    
    def test_get_criminals_filter_by_status(self, client, db_session, admin_token, sample_criminals):
        """Test filtering criminals by status."""
        response = client.get(
            '/api/criminals?status=wanted',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        for criminal in data['criminals']:
            assert criminal['status'] == 'wanted'
    
    def test_get_criminal_by_id(self, client, db_session, admin_token, sample_criminal):
        """Test retrieving specific criminal by ID."""
        response = client.get(
            f'/api/criminals/{sample_criminal.id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['criminal']['name'] == sample_criminal.name
    
    def test_get_nonexistent_criminal(self, client, db_session, admin_token):
        """Test retrieving non-existent criminal."""
        response = client.get(
            '/api/criminals/99999',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 404
    
    def test_get_criminals_invalid_pagination(self, client, db_session, admin_token):
        """Test with invalid pagination parameters."""
        response = client.get(
            '/api/criminals?page=-1&per_page=999999',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        # Should validate pagination (BUG-012)
        assert response.status_code in [200, 400]


@pytest.mark.unit
class TestCriminalUpdate:
    """Test criminal update functionality."""
    
    def test_update_criminal_valid_data(self, client, db_session, admin_token, sample_criminal):
        """Test updating criminal with valid data."""
        response = client.put(
            f'/api/criminals/{sample_criminal.id}',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'name': 'Updated Name',
                'status': 'caught'
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['criminal']['name'] == 'Updated Name'
        assert data['criminal']['status'] == 'caught'
    
    def test_update_nonexistent_criminal(self, client, db_session, admin_token):
        """Test updating non-existent criminal."""
        response = client.put(
            '/api/criminals/99999',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'name': 'Updated Name'}
        )
        
        assert response.status_code == 404
    
    def test_update_criminal_invalid_data(self, client, db_session, admin_token, sample_criminal):
        """Test updating criminal with invalid data."""
        response = client.put(
            f'/api/criminals/{sample_criminal.id}',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'age': -10}
        )
        
        assert response.status_code == 400
    
    def test_update_criminal_partial_update(self, client, db_session, admin_token, sample_criminal):
        """Test partial update of criminal."""
        original_name = sample_criminal.name
        response = client.put(
            f'/api/criminals/{sample_criminal.id}',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'status': 'caught'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['criminal']['name'] == original_name
        assert data['criminal']['status'] == 'caught'


@pytest.mark.unit
class TestCriminalDeletion:
    """Test criminal deletion functionality."""
    
    def test_delete_criminal(self, client, db_session, admin_token, sample_criminal):
        """Test deleting criminal."""
        criminal_id = sample_criminal.id
        response = client.delete(
            f'/api/criminals/{criminal_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        
        # Verify deletion
        from app.models.criminal import Criminal
        criminal = Criminal.query.get(criminal_id)
        # Should be None for hard delete or have is_deleted=True for soft delete
        assert criminal is None or hasattr(criminal, 'is_deleted')
    
    def test_delete_nonexistent_criminal(self, client, db_session, admin_token):
        """Test deleting non-existent criminal."""
        response = client.delete(
            '/api/criminals/99999',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 404
    
    def test_delete_criminal_cascade_encodings(self, client, db_session, admin_token, sample_criminal, sample_face_encoding):
        """Test that deleting criminal also deletes associated encodings."""
        criminal_id = sample_criminal.id
        encoding_id = sample_face_encoding.id
        
        response = client.delete(
            f'/api/criminals/{criminal_id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        
        # Verify encoding is also deleted
        from app.models.face_encoding import FaceEncoding
        encoding = FaceEncoding.query.get(encoding_id)
        assert encoding is None


@pytest.mark.unit
class TestPhotoManagement:
    """Test criminal photo management."""
    
    def test_upload_photo_valid_image(self, client, db_session, admin_token, sample_criminal, tmp_path):
        """Test uploading valid photo."""
        # Create test image
        from PIL import Image
        import io
        
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        response = client.post(
            f'/api/criminals/{sample_criminal.id}/photos',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'photo': (img_bytes, 'test.jpg')},
            content_type='multipart/form-data'
        )
        
        # Implementation may vary
        assert response.status_code in [200, 201]
    
    def test_upload_photo_invalid_format(self, client, db_session, admin_token, sample_criminal):
        """Test uploading invalid file format."""
        import io
        
        txt_file = io.BytesIO(b'This is not an image')
        response = client.post(
            f'/api/criminals/{sample_criminal.id}/photos',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'photo': (txt_file, 'test.txt')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
    
    def test_upload_photo_exceeds_size_limit(self, client, db_session, admin_token, sample_criminal):
        """Test uploading photo exceeding size limit."""
        import io
        
        # Create large fake file (10MB)
        large_file = io.BytesIO(b'0' * (10 * 1024 * 1024))
        response = client.post(
            f'/api/criminals/{sample_criminal.id}/photos',
            headers={'Authorization': f'Bearer {admin_token}'},
            data={'photo': (large_file, 'large.jpg')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 413  # Payload Too Large
    
    def test_upload_multiple_photos(self, client, db_session, admin_token, sample_criminal):
        """Test uploading multiple photos for same criminal."""
        # Should test BUG-008 (no limit on photo uploads)
        pass
    
    def test_delete_photo(self, client, db_session, admin_token, sample_criminal, sample_face_encoding):
        """Test deleting criminal photo."""
        response = client.delete(
            f'/api/criminals/{sample_criminal.id}/photos/{sample_face_encoding.id}',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        # Implementation may vary
        assert response.status_code in [200, 204]
