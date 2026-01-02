"""Face detection routes."""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.detection_log import DetectionLog
from app.models.criminal import Criminal
from app.services.detection_service import detection_service
import os

bp = Blueprint('face_detection', __name__)


@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_detection():
    """Upload image for face detection."""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Debug: Log what we received
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Request files: {request.files}")
        logger.info(f"Request form: {request.form}")
        logger.info(f"Request content type: {request.content_type}")
        
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({'message': 'No image file provided'}), 400
        
        file = request.files['image']
        location = request.form.get('location', '')
        camera_id = request.form.get('camera_id', '')
        
        # Save uploaded file
        filepath = detection_service.save_upload(file)
        if not filepath:
            return jsonify({'message': 'Invalid file format. Allowed: png, jpg, jpeg, gif, bmp'}), 400
        
        # Process detection
        result = detection_service.process_detection(
            filepath,
            current_user_id,
            location,
            camera_id
        )
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'message': f'Detection failed: {str(e)}'}), 500


@bp.route('/live', methods=['POST'])
@jwt_required()
def live_detection():
    """Process live camera feed frame."""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Check if frame is present
        if 'frame' not in request.files:
            return jsonify({'message': 'No frame provided'}), 400
        
        file = request.files['frame']
        location = request.form.get('location', 'Live Camera')
        camera_id = request.form.get('camera_id', 'default')
        
        # Save frame
        filepath = detection_service.save_upload(file)
        if not filepath:
            return jsonify({'message': 'Invalid frame format'}), 400
        
        # Process detection
        result = detection_service.process_detection(
            filepath,
            current_user_id,
            location,
            camera_id
        )
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'message': f'Live detection failed: {str(e)}'}), 500


@bp.route('/logs', methods=['GET'])
@jwt_required()
def get_detection_logs():
    """Get detection history with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', None)
        
        query = DetectionLog.query
        
        # Filter by status if provided
        if status:
            query = query.filter_by(status=status)
        
        # Paginate
        pagination = query.order_by(DetectionLog.detected_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        detections = []
        for log in pagination.items:
            criminal = Criminal.query.get(log.criminal_id)
            detections.append({
                'id': log.id,
                'criminal_id': log.criminal_id,
                'criminal_name': criminal.name if criminal else 'Unknown',
                'crime_type': criminal.crime_type if criminal else 'N/A',
                'confidence_score': log.confidence_score,
                'detected_at': log.detected_at.isoformat(),
                'location': log.location,
                'camera_id': log.camera_id,
                'status': log.status,
                'notes': log.notes
            })
        
        return jsonify({
            'detections': detections,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get logs: {str(e)}'}), 500


@bp.route('/logs/<int:log_id>', methods=['GET'])
@jwt_required()
def get_detection_log(log_id):
    """Get specific detection log."""
    try:
        log = DetectionLog.query.get(log_id)
        if not log:
            return jsonify({'message': 'Detection log not found'}), 404
        
        criminal = Criminal.query.get(log.criminal_id)
        
        return jsonify({
            'id': log.id,
            'criminal_id': log.criminal_id,
            'criminal_name': criminal.name if criminal else 'Unknown',
            'crime_type': criminal.crime_type if criminal else 'N/A',
            'danger_level': criminal.danger_level if criminal else 'N/A',
            'confidence_score': log.confidence_score,
            'detected_at': log.detected_at.isoformat(),
            'location': log.location,
            'camera_id': log.camera_id,
            'image_path': log.image_path,
            'status': log.status,
            'notes': log.notes
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get log: {str(e)}'}), 500


@bp.route('/logs/<int:log_id>/verify', methods=['PUT'])
@jwt_required()
def verify_detection(log_id):
    """Verify or mark detection as false positive."""
    try:
        data = request.get_json()
        status = data.get('status')  # 'verified' or 'false_positive'
        notes = data.get('notes', '')
        
        if status not in ['verified', 'false_positive']:
            return jsonify({'message': 'Invalid status. Use "verified" or "false_positive"'}), 400
        
        log = DetectionLog.query.get(log_id)
        if not log:
            return jsonify({'message': 'Detection log not found'}), 404
        
        log.status = status
        log.notes = notes
        db.session.commit()
        
        return jsonify({
            'message': 'Detection updated successfully',
            'detection': {
                'id': log.id,
                'status': log.status,
                'notes': log.notes
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to verify detection: {str(e)}'}), 500


@bp.route('/image/<int:log_id>', methods=['GET'])
@jwt_required()
def get_detection_image(log_id):
    """Get detection image."""
    try:
        log = DetectionLog.query.get(log_id)
        if not log or not log.image_path:
            return jsonify({'message': 'Image not found'}), 404
        
        if not os.path.exists(log.image_path):
            return jsonify({'message': 'Image file not found'}), 404
        
        return send_file(log.image_path, mimetype='image/jpeg')
        
    except Exception as e:
        return jsonify({'message': f'Failed to get image: {str(e)}'}), 500
