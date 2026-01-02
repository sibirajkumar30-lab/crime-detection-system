"""
Test Data Factories using factory_boy
Generate realistic test data for testing
"""

import factory
from factory.faker import Faker
from factory.fuzzy import FuzzyChoice, FuzzyInteger
from datetime import datetime
import random

from app import db
from app.models.user import User
from app.models.criminal import Criminal
from app.models.face_encoding import FaceEncoding
from app.models.detection_log import DetectionLog
from app.models.alert import Alert


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    username = Faker('user_name')
    email = Faker('email')
    role = FuzzyChoice(['admin', 'operator', 'viewer'])
    is_active = True
    created_at = Faker('date_time_this_year')
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password after creation."""
        if create:
            obj.set_password(extracted or 'DefaultPassword@123')


class CriminalFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Criminal instances."""
    
    class Meta:
        model = Criminal
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    name = Faker('name')
    alias = Faker('user_name')
    age = FuzzyInteger(18, 70)
    gender = FuzzyChoice(['Male', 'Female'])
    crime_type = FuzzyChoice(['Theft', 'Assault', 'Fraud', 'Robbery', 'Vandalism', 'Burglary'])
    crime_details = Faker('text', max_nb_chars=200)
    status = FuzzyChoice(['wanted', 'caught', 'released', 'under_investigation'])
    danger_level = FuzzyChoice(['low', 'medium', 'high'])
    last_seen_location = Faker('address')
    added_date = Faker('date_time_this_year')
    
    @factory.lazy_attribute
    def added_by(self):
        """Get or create a user."""
        user = User.query.first()
        if not user:
            user = UserFactory()
        return user.id


class FaceEncodingFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating FaceEncoding instances."""
    
    class Meta:
        model = FaceEncoding
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    photo_filename = Faker('file_name', extension='jpg')
    quality_score = factory.LazyFunction(lambda: random.uniform(0.5, 1.0))
    pose_type = FuzzyChoice(['frontal', 'profile', 'three_quarter'])
    created_at = Faker('date_time_this_year')
    
    @factory.lazy_attribute
    def criminal_id(self):
        """Get or create a criminal."""
        criminal = Criminal.query.first()
        if not criminal:
            criminal = CriminalFactory()
        return criminal.id
    
    @factory.lazy_attribute
    def encoding(self):
        """Generate random face encoding (512-dimensional vector)."""
        import numpy as np
        return np.random.rand(512).tolist()


class DetectionLogFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating DetectionLog instances."""
    
    class Meta:
        model = DetectionLog
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    image_path = Faker('file_path', extension='jpg')
    location = Faker('address')
    camera_id = factory.LazyFunction(lambda: f"CAM-{random.randint(100, 999)}")
    confidence_score = factory.LazyFunction(lambda: random.uniform(0.7, 0.99))
    status = FuzzyChoice(['pending', 'reviewed', 'false_positive'])
    detection_date = Faker('date_time_this_month')
    
    @factory.lazy_attribute
    def detected_by(self):
        """Get or create a user."""
        user = User.query.filter_by(role='operator').first()
        if not user:
            user = UserFactory(role='operator')
        return user.id
    
    @factory.lazy_attribute
    def criminal_id(self):
        """Get or create a criminal (optional)."""
        criminal = Criminal.query.first()
        if criminal:
            return criminal.id
        return None


class AlertFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Alert instances."""
    
    class Meta:
        model = Alert
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    alert_type = FuzzyChoice(['high_confidence', 'medium_confidence', 'manual'])
    message = Faker('sentence')
    severity = FuzzyChoice(['low', 'medium', 'high', 'critical'])
    status = FuzzyChoice(['sent', 'delivered', 'failed', 'acknowledged'])
    created_at = Faker('date_time_this_month')
    
    @factory.lazy_attribute
    def detection_id(self):
        """Get or create a detection log."""
        detection = DetectionLog.query.first()
        if not detection:
            detection = DetectionLogFactory()
        return detection.id
    
    @factory.lazy_attribute
    def criminal_id(self):
        """Get or create a criminal."""
        criminal = Criminal.query.first()
        if not criminal:
            criminal = CriminalFactory()
        return criminal.id


# Batch creation helpers
def create_test_dataset(num_users=10, num_criminals=50, num_detections=100):
    """
    Create a complete test dataset with related records.
    
    Args:
        num_users: Number of users to create
        num_criminals: Number of criminals to create
        num_detections: Number of detections to create
    """
    print(f"Creating test dataset...")
    
    # Create users
    print(f"Creating {num_users} users...")
    users = UserFactory.create_batch(num_users)
    admin = UserFactory(role='admin', username='test_admin')
    
    # Create criminals
    print(f"Creating {num_criminals} criminals...")
    criminals = CriminalFactory.create_batch(num_criminals)
    
    # Create face encodings for criminals (1-3 per criminal)
    print(f"Creating face encodings...")
    for criminal in criminals:
        num_photos = random.randint(1, 3)
        FaceEncodingFactory.create_batch(num_photos, criminal_id=criminal.id)
    
    # Create detection logs
    print(f"Creating {num_detections} detection logs...")
    detections = DetectionLogFactory.create_batch(num_detections)
    
    # Create alerts for some detections
    print(f"Creating alerts...")
    high_confidence_detections = [d for d in detections if d.confidence_score > 0.85]
    for detection in high_confidence_detections[:20]:  # Alert on top 20
        AlertFactory(detection_id=detection.id, criminal_id=detection.criminal_id)
    
    print("Test dataset created successfully!")
    print(f"Summary:")
    print(f"  - Users: {len(users) + 1}")
    print(f"  - Criminals: {len(criminals)}")
    print(f"  - Face Encodings: {FaceEncoding.query.count()}")
    print(f"  - Detections: {len(detections)}")
    print(f"  - Alerts: {Alert.query.count()}")


# Specialized factories for specific test scenarios
class WantedCriminalFactory(CriminalFactory):
    """Factory for wanted criminals."""
    status = 'wanted'
    danger_level = FuzzyChoice(['medium', 'high'])


class HighDangerCriminalFactory(CriminalFactory):
    """Factory for high danger criminals."""
    status = 'wanted'
    danger_level = 'high'
    crime_type = FuzzyChoice(['Assault', 'Robbery', 'Murder'])


class HighConfidenceDetectionFactory(DetectionLogFactory):
    """Factory for high confidence detections."""
    confidence_score = factory.LazyFunction(lambda: random.uniform(0.85, 0.99))
    status = 'pending'


class AdminUserFactory(UserFactory):
    """Factory for admin users."""
    role = 'admin'
    username = factory.Sequence(lambda n: f'admin_{n}')


class OperatorUserFactory(UserFactory):
    """Factory for operator users."""
    role = 'operator'
    username = factory.Sequence(lambda n: f'operator_{n}')


# Context manager for temporary test data
class TestDataContext:
    """Context manager for creating and cleaning up test data."""
    
    def __init__(self, **kwargs):
        self.factories = kwargs
        self.created_objects = []
    
    def __enter__(self):
        """Create test data."""
        for model_name, count in self.factories.items():
            factory_class = globals().get(f"{model_name}Factory")
            if factory_class:
                objects = factory_class.create_batch(count)
                self.created_objects.extend(objects)
        return self.created_objects
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up test data."""
        for obj in reversed(self.created_objects):
            try:
                db.session.delete(obj)
            except:
                pass
        db.session.commit()


# Usage example:
# with TestDataContext(User=5, Criminal=10) as objects:
#     # Use test data
#     pass
# # Data automatically cleaned up
