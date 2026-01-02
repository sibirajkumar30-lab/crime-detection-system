import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .config import config
import logging
from logging.handlers import RotatingFileHandler

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)


def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    limiter.init_app(app)
    
    # Create upload directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['ENCODINGS_FOLDER'], exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_commands(app)
    
    return app


def setup_logging(app):
    """Configure application logging."""
    if not app.debug and not app.testing:
        # File handler
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Crime Detection System startup')


def register_blueprints(app):
    """Register application blueprints."""
    from .routes import auth, face_detection, criminal, dashboard, video_detection, admin, notifications
    from flask import jsonify, render_template_string, send_from_directory
    
    # Root route
    @app.route('/')
    def index():
        """API health check and documentation."""
        return jsonify({
            'message': 'Crime Detection System API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'auth': '/api/auth (POST /login, /register, GET /profile)',
                'criminals': '/api/criminals (GET, POST, PUT, DELETE)',
                'detection': '/api/detection (POST /upload, /live)',
                'video_detection': '/api/video (POST /upload, /process)',
                'dashboard': '/api/dashboard (GET /stats, /recent-detections)'
            },
            'documentation': 'Visit /test for API testing interface'
        }), 200
    
    # Serve encoding images
    @app.route('/encodings/<path:filename>')
    def serve_encoding(filename):
        """Serve face encoding images."""
        encodings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), app.config['ENCODINGS_FOLDER'])
        return send_from_directory(encodings_path, filename)
    
    # Serve upload images
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        """Serve uploaded images."""
        uploads_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
        return send_from_directory(uploads_path, filename)
    
    # Test page route
    @app.route('/test')
    def test_page():
        """Simple test page for API."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Crime Detection System - API Test</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                .endpoint { margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #4CAF50; }
                .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; color: white; margin-right: 10px; }
                .post { background: #FF9800; }
                .get { background: #4CAF50; }
                code { background: #e0e0e0; padding: 2px 6px; border-radius: 3px; }
                .test-form { margin-top: 20px; padding: 20px; background: #e3f2fd; border-radius: 4px; }
                input, button { padding: 10px; margin: 5px 0; width: 100%; box-sizing: border-box; }
                button { background: #2196F3; color: white; border: none; cursor: pointer; font-weight: bold; }
                button:hover { background: #1976D2; }
                #response { margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 4px; white-space: pre-wrap; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚨 Crime Detection System API</h1>
                <p><strong>Status:</strong> ✅ Running</p>
                <p><strong>Base URL:</strong> <code>http://127.0.0.1:5000</code></p>
                
                <h2>📍 Available Endpoints</h2>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/api/auth/login</code>
                    <p>Login with email and password</p>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/api/auth/register</code>
                    <p>Register new user</p>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/api/criminals</code>
                    <p>Get all criminals</p>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/api/dashboard/stats</code>
                    <p>Get dashboard statistics</p>
                </div>
                
                <h2>🧪 Test Login</h2>
                <div class="test-form">
                    <h3>Login Test</h3>
                    <input type="email" id="email" placeholder="Email" value="sibirajkumar30@gmail.com">
                    <input type="password" id="password" placeholder="Password" value="1234">
                    <button onclick="testLogin()">Test Login</button>
                    <div id="response"></div>
                </div>
            </div>
            
            <script>
                async function testLogin() {
                    const email = document.getElementById('email').value;
                    const password = document.getElementById('password').value;
                    const responseDiv = document.getElementById('response');
                    
                    responseDiv.innerHTML = 'Loading...';
                    
                    try {
                        const response = await fetch('/api/auth/login', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ email, password })
                        });
                        
                        const data = await response.json();
                        responseDiv.innerHTML = JSON.stringify(data, null, 2);
                        
                        if (data.access_token) {
                            localStorage.setItem('access_token', data.access_token);
                            responseDiv.innerHTML += '\\n\\n✅ Token saved to localStorage!';
                        }
                    } catch (error) {
                        responseDiv.innerHTML = 'Error: ' + error.message;
                    }
                }
            </script>
        </body>
        </html>
        """
        return render_template_string(html)
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(face_detection.bp, url_prefix='/api/detection')
    app.register_blueprint(criminal.bp, url_prefix='/api/criminals')
    app.register_blueprint(dashboard.bp, url_prefix='/api/dashboard')
    app.register_blueprint(video_detection.bp, url_prefix='/api/video')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    app.register_blueprint(notifications.bp, url_prefix='/api/notifications')


def register_error_handlers(app):
    """Register error handlers."""
    from .middleware.error_handlers import handle_404, handle_500, handle_validation_error
    from flask import jsonify
    import logging
    
    logger = logging.getLogger(__name__)
    
    app.register_error_handler(404, handle_404)
    app.register_error_handler(500, handle_500)
    app.register_error_handler(ValueError, handle_validation_error)
    
    # JWT error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        logger.error(f"Unauthorized access: {error_string}")
        return jsonify({'message': 'Missing authorization token', 'error': error_string}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        logger.error(f"Invalid token: {error_string}")
        return jsonify({'message': 'Invalid or malformed token', 'error': error_string}), 422
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.warning(f"Expired token for user: {jwt_payload.get('sub')}")
        return jsonify({'message': 'Token has expired', 'error': 'token_expired'}), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        logger.warning(f"Revoked token for user: {jwt_payload.get('sub')}")
        return jsonify({'message': 'Token has been revoked', 'error': 'token_revoked'}), 401
    
    @jwt.token_verification_failed_loader
    def token_verification_failed_callback(jwt_header, jwt_payload):
        logger.error(f"Token verification failed: {jwt_header}")
        return jsonify({'message': 'Token verification failed', 'error': 'verification_failed'}), 422


def register_commands(app):
    """Register CLI commands."""
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        print("Database initialized!")
    
    @app.cli.command()
    def create_admin():
        """Create an admin user."""
        from .models.user import User
        
        email = input("Enter admin email: ")
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")
        
        admin = User(
            email=email,
            username=username,
            role='admin'
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{username}' created successfully!")
