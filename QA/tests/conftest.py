"""
Test Configuration and Fixtures
Shared across all test modules
"""

import os
import sys
import pytest
from datetime import datetime
from flask import Flask
from flask_jwt_extended import create_access_token

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
sys.path.insert(0, backend_path)
print(f"Added to Python path: {backend_path}")

# Try to import app components (may fail if backend not set up)
try:
    from app import create_app, db
    from app.models.user import User
    from app.models.criminal import Criminal
    from app.models.face_encoding import FaceEncoding
    from app.models.detection_log import DetectionLog
    from app.models.alert import Alert
    APP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import app components: {e}")
    print("Some fixtures will not be available. Backend tests may fail.")
    APP_AVAILABLE = False


@pytest.fixture(scope='session')
def app():
    """Create application instance for testing."""
    if not APP_AVAILABLE:
        pytest.skip("Backend app not available")
    
    app = create_app('testing')
    
    # Override config for testing
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key',
        'SECRET_KEY': 'test-secret-key',
        'UPLOAD_FOLDER': 'tests/temp/uploads',
        'ENCODINGS_FOLDER': 'tests/temp/encodings',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    # Workaround for werkzeug version compatibility
    import werkzeug
    if not hasattr(werkzeug, '__version__'):
        import werkzeug._internal
        werkzeug.__version__ = werkzeug._internal.__version__ if hasattr(werkzeug._internal, '__version__') else '3.0.0'
    
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing."""
    with app.app_context():
        # Clean up database before each test
        db.session.remove()
        db.drop_all()
        db.create_all()
        
        yield db
        
        # Clean up after test
        db.session.remove()
        db.drop_all()


@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing."""
    user = User(
        username='admin',
        email='admin@test.com',
        role='admin',
        is_active=True
    )
    user.set_password('Admin@123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def operator_user(db_session):
    """Create operator user for testing."""
    user = User(
        username='operator',
        email='operator@test.com',
        role='operator',
        is_active=True
    )
    user.set_password('Operator@123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def viewer_user(db_session):
    """Create viewer user for testing."""
    user = User(
        username='viewer',
        email='viewer@test.com',
        role='viewer',
        is_active=True
    )
    user.set_password('Viewer@123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_token(app, admin_user):
    """Generate JWT token for admin user."""
    with app.app_context():
        return create_access_token(identity=str(admin_user.id))


@pytest.fixture
def operator_token(app, operator_user):
    """Generate JWT token for operator user."""
    with app.app_context():
        return create_access_token(identity=str(operator_user.id))


@pytest.fixture
def viewer_token(app, viewer_user):
    """Generate JWT token for viewer user."""
    with app.app_context():
        return create_access_token(identity=str(viewer_user.id))


@pytest.fixture
def sample_criminal(db_session, admin_user):
    """Create sample criminal for testing."""
    criminal = Criminal(
        name='John Doe',
        alias='Johnny',
        crime_type='Theft',
        description='Robbery at convenience store',
        status='wanted',
        danger_level='medium',
        last_seen_location='Downtown',
        added_by=admin_user.id
    )
    db.session.add(criminal)
    db.session.commit()
    return criminal


@pytest.fixture
def sample_criminals(db_session, admin_user):
    """Create multiple criminals for testing."""
    criminals = []
    for i in range(5):
        criminal = Criminal(
            name=f'Criminal {i+1}',
            alias=f'Alias{i+1}',
            age=25 + i,
            gender='Male' if i % 2 == 0 else 'Female',
            crime_type='Theft' if i % 2 == 0 else 'Assault',
            crime_details=f'Crime details {i+1}',
            status='wanted' if i % 2 == 0 else 'caught',
            danger_level='low' if i == 0 else 'medium',
            last_seen_location=f'Location {i+1}',
            added_by=admin_user.id
        )
        db.session.add(criminal)
        criminals.append(criminal)
    db.session.commit()
    return criminals


@pytest.fixture
def sample_face_encoding(db_session, sample_criminal):
    """Create sample face encoding for testing."""
    import numpy as np
    
    # Create dummy encoding
    encoding = np.random.rand(512).tolist()
    
    face_enc = FaceEncoding(
        criminal_id=sample_criminal.id,
        encoding=encoding,
        photo_filename='test_photo.jpg',
        quality_score=0.85,
        pose_type='frontal'
    )
    db.session.add(face_enc)
    db.session.commit()
    return face_enc


@pytest.fixture
def sample_detection_log(db_session, sample_criminal, operator_user):
    """Create sample detection log for testing."""
    detection = DetectionLog(
        image_path='uploads/test_detection.jpg',
        detected_by=operator_user.id,
        criminal_id=sample_criminal.id,
        confidence_score=0.92,
        location='Main Street',
        camera_id='CAM-001',
        status='pending'
    )
    db.session.add(detection)
    db.session.commit()
    return detection


@pytest.fixture
def sample_alert(db_session, sample_criminal, sample_detection_log):
    """Create sample alert for testing."""
    alert = Alert(
        detection_id=sample_detection_log.id,
        criminal_id=sample_criminal.id,
        alert_type='high_confidence',
        message='High confidence match detected',
        severity='high',
        status='sent'
    )
    db.session.add(alert)
    db.session.commit()
    return alert


@pytest.fixture
def sample_image_path():
    """Return path to sample test image."""
    return 'tests/test_data/images/test_face.jpg'


@pytest.fixture
def temp_upload_dir(tmp_path):
    """Create temporary upload directory."""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    return str(upload_dir)


@pytest.fixture
def temp_encodings_dir(tmp_path):
    """Create temporary encodings directory."""
    encodings_dir = tmp_path / "encodings"
    encodings_dir.mkdir()
    return str(encodings_dir)


@pytest.fixture
def mock_face_service(mocker):
    """Mock face service for testing without DeepFace."""
    mock_service = mocker.patch('app.services.face_service_deepface.face_service_deepface')
    
    # Configure mock responses
    mock_service.detect_faces.return_value = [
        {'bbox': [100, 100, 200, 200], 'confidence': 0.99}
    ]
    mock_service.get_face_encoding.return_value = [0.1] * 512
    mock_service.compare_faces.return_value = [
        {'criminal_id': 1, 'distance': 0.25, 'match': True}
    ]
    
    return mock_service


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up test files after each test."""
    yield
    
    # Clean up test uploads
    import shutil
    test_dirs = ['tests/temp/uploads', 'tests/temp/encodings']
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )
