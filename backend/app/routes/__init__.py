"""Routes package."""

from app.routes import auth, criminal, face_detection, video_detection, dashboard, notifications

def init_app(app):
    """Register all blueprints."""
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(criminal.bp, url_prefix='/api/criminals')
    app.register_blueprint(face_detection.bp, url_prefix='/api/face-detection')
    app.register_blueprint(video_detection.bp, url_prefix='/api/video-detection')
    app.register_blueprint(dashboard.bp, url_prefix='/api/dashboard')
    app.register_blueprint(notifications.bp, url_prefix='/api/notifications')
