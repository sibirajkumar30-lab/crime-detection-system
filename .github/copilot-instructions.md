# Face Recognition and Crime Detection System - Copilot Instructions

## Project Overview
A real-time face recognition system that detects and identifies individuals from CCTV/camera feeds and matches them against a criminal database. Built for law enforcement and security applications using AI/ML and computer vision.

**Target**: BCA Final Year Project
**Focus**: Security, scalability, clean architecture, and impressive demonstration

---

## Technology Stack

### Backend
- **Language**: Python 3.9+
- **Framework**: Flask with Flask-RESTful
- **AI/ML Libraries**:
  - `face_recognition` (dlib-based, 99.38% accuracy)
  - `opencv-python` (cv2) for video/image processing
  - `numpy` for numerical operations
  - `Pillow` for image handling
- **Database ORM**: SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Security**: Flask-CORS, Flask-Limiter, bcrypt
- **Email**: smtplib (Gmail SMTP)

### Frontend
- **Framework**: React.js 18+
- **UI Library**: Material-UI (MUI) or Tailwind CSS
- **State Management**: React Context API / Redux (if needed)
- **HTTP Client**: Axios
- **Routing**: React Router v6

### Database
- **Primary**: PostgreSQL 14+ (or SQLite for development)
- **Caching**: Redis (optional, for production)

### Development Tools
- **Environment**: Python venv
- **Package Manager**: pip (backend), npm (frontend)
- **Version Control**: Git
- **API Testing**: Postman/Thunder Client

---

## Project Structure

```
crime_detection/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app factory
│   │   ├── config.py                # Configuration classes
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # User model
│   │   │   ├── criminal.py          # Criminal model
│   │   │   ├── face_encoding.py     # Face encoding model
│   │   │   ├── detection_log.py     # Detection log model
│   │   │   └── alert.py             # Alert model
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # Authentication routes
│   │   │   ├── face_detection.py    # Detection routes
│   │   │   ├── criminal.py          # Criminal CRUD routes
│   │   │   └── dashboard.py         # Dashboard stats routes
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── face_service.py      # Face detection/recognition logic
│   │   │   ├── detection_service.py # Detection processing
│   │   │   ├── alert_service.py     # Alert/email logic
│   │   │   └── auth_service.py      # Authentication logic
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── validators.py        # Input validation
│   │   │   ├── helpers.py           # Helper functions
│   │   │   └── decorators.py        # Custom decorators
│   │   └── middleware/
│   │       ├── __init__.py
│   │       └── error_handlers.py    # Global error handlers
│   ├── migrations/                   # Database migrations
│   ├── tests/                        # Unit tests
│   ├── uploads/                      # Temporary image storage
│   ├── encodings/                    # Stored face encodings
│   ├── logs/                         # Application logs
│   ├── requirements.txt
│   ├── .env.example
│   ├── .env
│   └── run.py                        # Application entry point
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── Login.jsx
│   │   │   │   └── Register.jsx
│   │   │   ├── dashboard/
│   │   │   │   ├── Dashboard.jsx
│   │   │   │   ├── Stats.jsx
│   │   │   │   └── RecentDetections.jsx
│   │   │   ├── detection/
│   │   │   │   ├── LiveFeed.jsx
│   │   │   │   ├── UploadDetection.jsx
│   │   │   │   └── DetectionResult.jsx
│   │   │   ├── criminal/
│   │   │   │   ├── CriminalList.jsx
│   │   │   │   ├── CriminalForm.jsx
│   │   │   │   └── CriminalDetail.jsx
│   │   │   ├── alerts/
│   │   │   │   ├── AlertPanel.jsx
│   │   │   │   └── AlertHistory.jsx
│   │   │   └── common/
│   │   │       ├── Navbar.jsx
│   │   │       ├── Sidebar.jsx
│   │   │       └── Loading.jsx
│   │   ├── services/
│   │   │   ├── api.js               # Axios instance
│   │   │   ├── authService.js
│   │   │   ├── detectionService.js
│   │   │   └── criminalService.js
│   │   ├── context/
│   │   │   ├── AuthContext.jsx
│   │   │   └── AlertContext.jsx
│   │   ├── utils/
│   │   │   ├── constants.js
│   │   │   └── helpers.js
│   │   ├── App.jsx
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   ├── .env.example
│   └── .env
├── .gitignore
└── README.md
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'operator', -- 'admin', 'operator', 'viewer'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Criminals Table
```sql
CREATE TABLE criminals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    alias VARCHAR(100),
    crime_type VARCHAR(50) NOT NULL, -- 'theft', 'assault', 'fraud', etc.
    description TEXT,
    status VARCHAR(20) DEFAULT 'wanted', -- 'wanted', 'arrested', 'released'
    danger_level VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    last_seen_location VARCHAR(200),
    last_seen_date DATE,
    added_by INTEGER REFERENCES users(id),
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Face Encodings Table
```sql
CREATE TABLE face_encodings (
    id SERIAL PRIMARY KEY,
    criminal_id INTEGER REFERENCES criminals(id) ON DELETE CASCADE,
    encoding_data BYTEA NOT NULL, -- Store numpy array as binary
    image_path VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Detection Logs Table
```sql
CREATE TABLE detection_logs (
    id SERIAL PRIMARY KEY,
    criminal_id INTEGER REFERENCES criminals(id),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_score FLOAT NOT NULL, -- 0.0 to 1.0
    location VARCHAR(200),
    camera_id VARCHAR(50),
    image_path VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'verified', 'false_positive'
    notes TEXT,
    detected_by INTEGER REFERENCES users(id)
);
```

### Alerts Table
```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    detection_log_id INTEGER REFERENCES detection_logs(id),
    recipient_email VARCHAR(100) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'sent', -- 'sent', 'failed', 'pending'
    retry_count INTEGER DEFAULT 0
);
```

---

## API Endpoints Structure

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user (returns JWT)
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/profile` - Get current user profile
- `PUT /api/auth/profile` - Update user profile

### Face Detection
- `POST /api/detection/upload` - Upload image/video for detection
- `POST /api/detection/live` - Process live camera feed
- `GET /api/detection/logs` - Get detection history
- `GET /api/detection/logs/:id` - Get specific detection
- `PUT /api/detection/logs/:id/verify` - Verify detection

### Criminal Management
- `GET /api/criminals` - Get all criminals (with pagination)
- `POST /api/criminals` - Add new criminal
- `GET /api/criminals/:id` - Get criminal details
- `PUT /api/criminals/:id` - Update criminal
- `DELETE /api/criminals/:id` - Delete criminal
- `POST /api/criminals/:id/photo` - Upload criminal photo

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent-detections` - Recent detections
- `GET /api/dashboard/top-criminals` - Most detected criminals

### Alerts
- `GET /api/alerts` - Get all alerts
- `GET /api/alerts/:id` - Get specific alert
- `POST /api/alerts/test` - Test email configuration

---

## Coding Standards & Best Practices

### Python/Flask Backend

#### Code Style
- Follow PEP 8 style guide
- Use type hints where applicable
- Maximum line length: 100 characters
- Use docstrings for all functions/classes

#### Example Function Structure
```python
def detect_faces(image_path: str, confidence_threshold: float = 0.6) -> List[Dict]:
    """
    Detect and recognize faces in the given image.
    
    Args:
        image_path: Path to the image file
        confidence_threshold: Minimum confidence score (0.0-1.0)
    
    Returns:
        List of detected faces with criminal matches
        
    Raises:
        ValueError: If image_path is invalid
        FileNotFoundError: If image file doesn't exist
    """
    # Implementation
    pass
```

#### Error Handling
```python
# Always use try-except blocks
try:
    result = face_recognition.face_encodings(image)
except Exception as e:
    logger.error(f"Face encoding failed: {str(e)}")
    raise ValueError("Failed to process image")
```

#### Configuration Management
```python
# Use environment variables
import os
from dotenv import load_dotenv

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
```

#### Security Best Practices
```python
# Password hashing
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

# JWT authentication
from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def protected_route():
    current_user_id = get_jwt_identity()
    # Route logic
```

#### File Upload Validation
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

### React Frontend

#### Component Structure
```jsx
// Use functional components with hooks
import React, { useState, useEffect } from 'react';

const ComponentName = ({ prop1, prop2 }) => {
    const [state, setState] = useState(initialValue);
    
    useEffect(() => {
        // Side effects
    }, [dependencies]);
    
    return (
        <div>
            {/* JSX */}
        </div>
    );
};

export default ComponentName;
```

#### API Service Pattern
```javascript
// services/api.js
import axios from 'axios';

const API = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
    timeout: 10000,
});

// Add JWT token to requests
API.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default API;
```

#### Error Handling
```javascript
try {
    const response = await API.post('/detection/upload', formData);
    // Handle success
} catch (error) {
    if (error.response) {
        // Server responded with error
        console.error('Error:', error.response.data.message);
    } else if (error.request) {
        // Request made but no response
        console.error('Network error');
    } else {
        console.error('Error:', error.message);
    }
}
```

---

## Face Recognition Implementation

### Core Face Detection Service
```python
import face_recognition
import cv2
import numpy as np
from typing import List, Dict, Tuple

class FaceService:
    """Handle all face detection and recognition operations."""
    
    CONFIDENCE_THRESHOLD = 0.6  # 60% match threshold
    
    @staticmethod
    def detect_faces(image_path: str) -> List[np.ndarray]:
        """
        Detect face locations in image.
        
        Returns:
            List of face location tuples (top, right, bottom, left)
        """
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        return face_locations
    
    @staticmethod
    def encode_face(image_path: str) -> List[np.ndarray]:
        """
        Generate 128-dimensional face encodings.
        
        Returns:
            List of face encoding arrays
        """
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        return encodings
    
    @staticmethod
    def compare_faces(known_encodings: List[np.ndarray], 
                     unknown_encoding: np.ndarray,
                     tolerance: float = 0.6) -> Tuple[List[bool], List[float]]:
        """
        Compare face encoding against known faces.
        
        Args:
            known_encodings: List of known face encodings from database
            unknown_encoding: Encoding to compare
            tolerance: Match threshold (lower = stricter)
        
        Returns:
            Tuple of (matches, distances)
        """
        matches = face_recognition.compare_faces(
            known_encodings, 
            unknown_encoding, 
            tolerance=tolerance
        )
        face_distances = face_recognition.face_distance(
            known_encodings, 
            unknown_encoding
        )
        return matches, face_distances
    
    @staticmethod
    def get_best_match(matches: List[bool], 
                       distances: List[float]) -> Tuple[int, float]:
        """
        Find best matching face.
        
        Returns:
            Tuple of (best_match_index, confidence_score)
        """
        if True not in matches:
            return -1, 0.0
        
        best_match_index = np.argmin(distances)
        confidence = 1 - distances[best_match_index]  # Convert distance to confidence
        
        return best_match_index, confidence
```

### Video Stream Processing
```python
def process_video_stream():
    """Process live video feed for face detection."""
    video_capture = cv2.VideoCapture(0)  # 0 = default camera
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(
            rgb_small_frame, 
            face_locations
        )
        
        # Process each face
        for (top, right, bottom, left), face_encoding in zip(
            face_locations, 
            face_encodings
        ):
            # Scale back up face locations
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Compare with database
            # ... matching logic ...
            
            # Draw rectangle around face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Display result
        cv2.imshow('Video', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    video_capture.release()
    cv2.destroyAllWindows()
```

---

## Email Alert System

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

class AlertService:
    """Handle email alerts for criminal detection."""
    
    @staticmethod
    def send_alert_email(recipient: str, 
                        criminal_name: str, 
                        confidence: float,
                        image_path: str = None):
        """
        Send email alert when criminal detected.
        
        Args:
            recipient: Email address to send alert
            criminal_name: Name of detected criminal
            confidence: Confidence score (0-1)
            image_path: Optional path to detection image
        """
        sender_email = os.getenv('SMTP_EMAIL')
        sender_password = os.getenv('SMTP_PASSWORD')
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = f'🚨 ALERT: Criminal Detected - {criminal_name}'
        
        body = f"""
        <html>
        <body>
            <h2 style="color: red;">Criminal Detection Alert</h2>
            <p><strong>Name:</strong> {criminal_name}</p>
            <p><strong>Confidence:</strong> {confidence * 100:.2f}%</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Action Required:</strong> Immediate verification needed</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Attach image if provided
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment', 
                              filename='detection.jpg')
                msg.attach(img)
        
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            return True
        except Exception as e:
            logger.error(f"Email send failed: {str(e)}")
            return False
```

---

## Security Implementation

### JWT Authentication Flow
```python
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

# Login endpoint
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
        refresh_token = create_refresh_token(identity=user.id, expires_delta=timedelta(days=7))
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401
```

### Role-Based Access Control
```python
from functools import wraps

def role_required(allowed_roles):
    """Decorator to check user role."""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if user.role not in allowed_roles:
                return jsonify({'message': 'Insufficient permissions'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@criminal_bp.route('/criminals', methods=['POST'])
@role_required(['admin'])
def add_criminal():
    # Only admins can add criminals
    pass
```

### Input Validation
```python
from marshmallow import Schema, fields, validate

class CriminalSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    crime_type = fields.Str(required=True)
    description = fields.Str(validate=validate.Length(max=1000))
    danger_level = fields.Str(validate=validate.OneOf(['low', 'medium', 'high', 'critical']))

# Usage in route
@criminal_bp.route('/criminals', methods=['POST'])
def add_criminal():
    schema = CriminalSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
```

---

## Testing Guidelines

### Backend Unit Tests
```python
import unittest
from app import create_app, db

class FaceServiceTests(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_face_detection(self):
        """Test face detection on sample image."""
        result = FaceService.detect_faces('test_images/face.jpg')
        self.assertGreater(len(result), 0)
    
    def test_face_encoding(self):
        """Test face encoding generation."""
        encodings = FaceService.encode_face('test_images/face.jpg')
        self.assertEqual(len(encodings[0]), 128)  # 128-dimensional encoding
```

### Frontend Testing (Jest/React Testing Library)
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import Login from './Login';

test('renders login form', () => {
    render(<Login />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
});

test('handles login submission', async () => {
    render(<Login />);
    fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
        target: { value: 'password123' }
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    // Assert expected behavior
});
```

---

## Performance Optimization

### Backend Optimizations
- Use database indexing on frequently queried fields (email, criminal name)
- Implement pagination for large result sets
- Cache face encodings in Redis (optional)
- Resize images before processing (max 1024x1024)
- Process video frames at reduced FPS (skip frames if needed)
- Use connection pooling for database

### Frontend Optimizations
- Lazy load components with React.lazy()
- Implement virtual scrolling for large lists
- Debounce search inputs
- Optimize images (compress, lazy load)
- Use React.memo() for expensive components
- Implement proper error boundaries

---

## Deployment Considerations

### Environment Variables (.env)
```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/crime_detection

# Email (Gmail)
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Frontend
REACT_APP_API_URL=http://localhost:5000/api

# Face Recognition
FACE_RECOGNITION_TOLERANCE=0.6
MAX_UPLOAD_SIZE=5242880  # 5MB
```

### Production Checklist
- [ ] Change SECRET_KEY and JWT_SECRET_KEY to strong random values
- [ ] Set FLASK_ENV=production
- [ ] Use production database (PostgreSQL)
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up proper logging
- [ ] Implement rate limiting
- [ ] Configure file upload limits
- [ ] Set up monitoring (optional)
- [ ] Create database backups

---

## Key Implementation Notes

### When Writing Code:
1. **Always validate user input** before processing
2. **Handle errors gracefully** with proper try-except blocks
3. **Log important events** (detection, alerts, errors)
4. **Use type hints** in Python for clarity
5. **Write docstrings** for all functions
6. **Keep functions small** (single responsibility)
7. **Use meaningful variable names**
8. **Comment complex logic** but avoid obvious comments
9. **Follow DRY principle** (Don't Repeat Yourself)
10. **Test edge cases** (no faces, multiple faces, poor quality images)

### Face Recognition Tips:
- Resize images to max 1024x1024 before processing
- Use `face_locations` with `model='hog'` for CPU, `model='cnn'` for GPU
- Set confidence threshold to 0.6 (60%) for balanced accuracy
- Store face encodings as pickle or binary in database
- Handle cases with 0, 1, or multiple faces detected
- Implement image quality checks before processing

### Security Priorities:
1. Never store passwords in plain text (use bcrypt)
2. Always use JWT for authentication
3. Validate and sanitize all file uploads
4. Implement rate limiting on API endpoints
5. Use HTTPS in production
6. Sanitize database queries (use ORM)
7. Implement proper CORS configuration
8. Log security events (failed logins, unauthorized access)

---

## Common Pitfalls to Avoid

1. **Don't load all criminal encodings on every request** - cache them
2. **Don't process full resolution video frames** - downscale first
3. **Don't skip error handling** - always wrap risky operations
4. **Don't hardcode secrets** - use environment variables
5. **Don't ignore confidence scores** - implement thresholds
6. **Don't forget to close file handles** - use context managers
7. **Don't skip input validation** - validate everything from frontend
8. **Don't use synchronous operations for heavy tasks** - consider async
9. **Don't store large images in database** - store paths only
10. **Don't forget to clean up temporary files** - implement cleanup

---

## Demo Preparation Tips

### For Impressive Demonstration:
1. Prepare sample criminal database with clear photos
2. Create different test scenarios (single face, multiple faces)
3. Show confidence scores in UI
4. Demonstrate email alerts (use your email)
5. Show admin vs operator role differences
6. Display real-time statistics
7. Demonstrate error handling (wrong format, no face detected)
8. Show responsive UI on different screen sizes
9. Explain security measures implemented
10. Have backup plan (screenshots/video) if live demo fails

### Key Points to Mention to Lecturer:
- "Uses industry-standard face_recognition library (99.38% accuracy)"
- "Implements JWT-based authentication for security"
- "Follows RESTful API design principles"
- "Uses PostgreSQL for scalable data management"
- "Implements role-based access control"
- "Includes real-time email alerting system"
- "Follows secure coding best practices (password hashing, input validation)"
- "Scalable architecture suitable for production deployment"

---

## Quick Start Commands

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
flask db init
flask db migrate
flask db upgrade
python run.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Requirements.txt
```txt
Flask==2.3.0
Flask-RESTful==0.3.10
Flask-SQLAlchemy==3.0.5
Flask-JWT-Extended==4.5.2
Flask-CORS==4.0.0
Flask-Bcrypt==1.0.1
Flask-Limiter==3.3.1
face-recognition==1.3.0
opencv-python==4.8.0.74
numpy==1.24.3
Pillow==10.0.0
python-dotenv==1.0.0
psycopg2-binary==2.9.6
```

---

## Additional Resources

- Face Recognition Library: https://github.com/ageitgey/face_recognition
- OpenCV Documentation: https://docs.opencv.org/
- Flask Documentation: https://flask.palletsprojects.com/
- React Documentation: https://react.dev/
- PostgreSQL Documentation: https://www.postgresql.org/docs/

---

**Remember**: Focus on building a functional, secure, and well-architected system. The goal is to demonstrate your understanding of full-stack development, AI/ML integration, security best practices, and software engineering principles.

Good luck with your final year project! 🚀
