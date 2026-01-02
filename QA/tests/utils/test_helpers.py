"""
Test Utilities and Helpers
Common functions used across test suite
"""

import os
import shutil
import tempfile
from typing import Dict, List, Optional
import numpy as np
from PIL import Image, ImageDraw
import io


class TestImageGenerator:
    """Generate test images for face detection testing."""
    
    @staticmethod
    def create_simple_face_image(width=300, height=300, color='beige'):
        """
        Create a simple face-like image for testing.
        
        Args:
            width: Image width
            height: Image height
            color: Face color
            
        Returns:
            PIL Image object
        """
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw face (circle)
        face_size = min(width, height) // 2
        face_left = (width - face_size) // 2
        face_top = (height - face_size) // 2
        draw.ellipse(
            [face_left, face_top, face_left + face_size, face_top + face_size],
            fill=color,
            outline='black',
            width=2
        )
        
        # Draw eyes
        eye_y = face_top + face_size // 3
        left_eye_x = face_left + face_size // 3
        right_eye_x = face_left + 2 * face_size // 3
        eye_size = face_size // 10
        
        draw.ellipse([left_eye_x - eye_size, eye_y - eye_size,
                     left_eye_x + eye_size, eye_y + eye_size],
                    fill='black')
        draw.ellipse([right_eye_x - eye_size, eye_y - eye_size,
                     right_eye_x + eye_size, eye_y + eye_size],
                    fill='black')
        
        # Draw mouth
        mouth_y = face_top + 2 * face_size // 3
        mouth_width = face_size // 3
        mouth_left = face_left + face_size // 3
        draw.arc([mouth_left, mouth_y, mouth_left + mouth_width, mouth_y + face_size // 6],
                start=0, end=180, fill='black', width=2)
        
        return img
    
    @staticmethod
    def create_multi_face_image(num_faces=3, width=800, height=600):
        """
        Create image with multiple faces.
        
        Args:
            num_faces: Number of faces to include
            width: Image width
            height: Image height
            
        Returns:
            PIL Image object
        """
        img = Image.new('RGB', (width, height), color='lightgray')
        
        face_width = width // num_faces
        colors = ['beige', 'tan', 'peachpuff', 'wheat']
        
        for i in range(num_faces):
            face_img = TestImageGenerator.create_simple_face_image(
                width=face_width - 20,
                height=height - 20,
                color=colors[i % len(colors)]
            )
            img.paste(face_img, (i * face_width + 10, 10))
        
        return img
    
    @staticmethod
    def create_blank_image(width=200, height=200, color='white'):
        """Create blank image with no faces."""
        return Image.new('RGB', (width, height), color=color)
    
    @staticmethod
    def create_low_quality_image(width=50, height=50):
        """Create poor quality/small image."""
        img = Image.new('RGB', (width, height), color='gray')
        # Add noise
        pixels = img.load()
        for i in range(width):
            for j in range(height):
                noise = np.random.randint(-30, 30, 3)
                current = pixels[i, j]
                pixels[i, j] = tuple(max(0, min(255, c + n)) for c, n in zip(current, noise))
        return img
    
    @staticmethod
    def image_to_bytes(image, format='JPEG'):
        """Convert PIL Image to bytes."""
        img_bytes = io.BytesIO()
        image.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes
    
    @staticmethod
    def save_test_image(image, filename, directory='tests/test_data/images'):
        """Save test image to file."""
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)
        image.save(filepath)
        return filepath


class TestDataHelper:
    """Helper functions for test data management."""
    
    @staticmethod
    def create_temp_directory(prefix='test_'):
        """Create temporary directory for testing."""
        return tempfile.mkdtemp(prefix=prefix)
    
    @staticmethod
    def cleanup_temp_directory(directory):
        """Remove temporary directory and contents."""
        if os.path.exists(directory):
            shutil.rmtree(directory)
    
    @staticmethod
    def generate_fake_encoding(dimensions=512):
        """Generate fake face encoding for testing."""
        return np.random.rand(dimensions).tolist()
    
    @staticmethod
    def generate_similar_encoding(original_encoding, similarity=0.95):
        """
        Generate encoding similar to original.
        
        Args:
            original_encoding: Original encoding vector
            similarity: Similarity factor (0.0 to 1.0)
            
        Returns:
            Similar encoding vector
        """
        original = np.array(original_encoding)
        noise = np.random.randn(len(original)) * (1 - similarity)
        similar = original + noise
        return similar.tolist()


class APITestHelper:
    """Helper functions for API testing."""
    
    @staticmethod
    def assert_json_response(response, status_code=200):
        """Assert response is valid JSON with correct status."""
        assert response.status_code == status_code
        assert response.content_type == 'application/json'
        return response.get_json()
    
    @staticmethod
    def create_auth_header(token):
        """Create authorization header."""
        return {'Authorization': f'Bearer {token}'}
    
    @staticmethod
    def assert_pagination_response(data):
        """Assert response has pagination fields."""
        assert 'total' in data
        assert 'pages' in data
        assert 'current_page' in data or 'page' in data
    
    @staticmethod
    def assert_error_response(response, status_code, message_contains=None):
        """Assert response is error with expected format."""
        assert response.status_code == status_code
        data = response.get_json()
        assert 'message' in data or 'error' in data
        
        if message_contains:
            error_message = data.get('message') or data.get('error')
            assert message_contains.lower() in error_message.lower()


class DatabaseHelper:
    """Helper functions for database operations in tests."""
    
    @staticmethod
    def count_records(model_class):
        """Count total records of a model."""
        return model_class.query.count()
    
    @staticmethod
    def get_or_create(model_class, **kwargs):
        """Get existing record or create new one."""
        instance = model_class.query.filter_by(**kwargs).first()
        if instance:
            return instance
        
        from app import db
        instance = model_class(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    @staticmethod
    def delete_all(model_class):
        """Delete all records of a model."""
        from app import db
        model_class.query.delete()
        db.session.commit()


class PerformanceHelper:
    """Helper functions for performance testing."""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure function execution time."""
        import time
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        return result, elapsed
    
    @staticmethod
    def assert_execution_time(func, max_time, *args, **kwargs):
        """Assert function completes within time limit."""
        result, elapsed = PerformanceHelper.measure_execution_time(func, *args, **kwargs)
        assert elapsed < max_time, f"Execution took {elapsed:.2f}s, expected < {max_time}s"
        return result


class SecurityTestHelper:
    """Helper functions for security testing."""
    
    @staticmethod
    def sql_injection_payloads():
        """Return common SQL injection test payloads."""
        return [
            "' OR '1'='1",
            "1' OR '1' = '1",
            "' OR 1=1--",
            "admin'--",
            "' UNION SELECT NULL--",
            "1; DROP TABLE users--"
        ]
    
    @staticmethod
    def xss_payloads():
        """Return common XSS test payloads."""
        return [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'>"
        ]
    
    @staticmethod
    def assert_sanitized(original, sanitized):
        """Assert dangerous content was sanitized."""
        dangerous_patterns = ['<script>', '<iframe>', 'javascript:', 'onerror=']
        for pattern in dangerous_patterns:
            assert pattern not in sanitized.lower(), f"Dangerous pattern '{pattern}' not sanitized"


class ValidationHelper:
    """Helper functions for validation testing."""
    
    @staticmethod
    def invalid_emails():
        """Return list of invalid email formats."""
        return [
            'notanemail',
            '@example.com',
            'user@',
            'user@.com',
            'user..name@example.com',
            'user@example'
        ]
    
    @staticmethod
    def edge_case_strings():
        """Return edge case string values."""
        return [
            '',  # Empty
            ' ',  # Whitespace
            'a' * 1000,  # Very long
            '   trim me   ',  # Extra whitespace
            'Special!@#$%^&*()',  # Special characters
            '中文',  # Non-ASCII
            '\n\r\t',  # Control characters
        ]
    
    @staticmethod
    def invalid_ages():
        """Return invalid age values."""
        return [-1, 0, 151, -100, 999]


class MockHelper:
    """Helper functions for mocking."""
    
    @staticmethod
    def mock_deepface_detection(mocker, num_faces=1, confidence=0.99):
        """Mock DeepFace face detection."""
        mock = mocker.patch('app.services.face_service_deepface.DeepFace.extract_faces')
        
        faces = []
        for i in range(num_faces):
            faces.append({
                'facial_area': {'x': 100 * i, 'y': 100, 'w': 150, 'h': 150},
                'confidence': confidence
            })
        
        mock.return_value = faces
        return mock
    
    @staticmethod
    def mock_deepface_encoding(mocker, encoding=None):
        """Mock DeepFace face encoding."""
        mock = mocker.patch('app.services.face_service_deepface.DeepFace.represent')
        
        if encoding is None:
            encoding = np.random.rand(512).tolist()
        
        mock.return_value = [{'embedding': encoding}]
        return mock
    
    @staticmethod
    def mock_email_service(mocker):
        """Mock email alert service."""
        return mocker.patch('app.services.alert_service.send_email')


# Pytest fixtures can use these helpers
def pytest_configure():
    """Make helpers available to pytest."""
    import pytest
    pytest.image_gen = TestImageGenerator
    pytest.data_helper = TestDataHelper
    pytest.api_helper = APITestHelper
    pytest.db_helper = DatabaseHelper
    pytest.perf_helper = PerformanceHelper
    pytest.security_helper = SecurityTestHelper
    pytest.validation_helper = ValidationHelper
    pytest.mock_helper = MockHelper
