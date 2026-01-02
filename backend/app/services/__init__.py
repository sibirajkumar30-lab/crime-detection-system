"""Services package."""

from app.services.face_service_deepface import face_service_deepface
from app.services.detection_service import detection_service
from app.services.alert_service import send_detection_alert

__all__ = ['face_service_deepface', 'detection_service', 'send_detection_alert']
