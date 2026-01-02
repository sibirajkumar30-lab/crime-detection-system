"""Criminal management routes."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.criminal import Criminal
from app.models.face_encoding import FaceEncoding
from app.services.face_service_deepface import face_service_deepface as face_service  # Using DeepFace AI (99.65% accuracy)
from app.utils.quality_assessment import assess_face_quality, determine_pose_type  # Phase 3 enhancement
from app.services.criminal_alert_service import (
    send_criminal_added_alert,
    send_criminal_updated_alert,
    send_criminal_deleted_alert
)
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('criminal', __name__)

# Allowed file extensions for photo uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}  # Added webp since it's supported


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('', methods=['GET'])
@jwt_required()
def get_criminals():
    """Get all criminals with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', None)
        
        query = Criminal.query
        
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.order_by(Criminal.added_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'criminals': [criminal.to_dict() for criminal in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch criminals: {str(e)}'}), 500


@bp.route('/<int:criminal_id>', methods=['GET'])
@jwt_required()
def get_criminal(criminal_id):
    """Get specific criminal details."""
    try:
        criminal = Criminal.query.get(criminal_id)
        
        if not criminal:
            return jsonify({'message': 'Criminal not found'}), 404
        
        return jsonify({
            'criminal': criminal.to_dict(include_encodings=True)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch criminal: {str(e)}'}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def add_criminal():
    """Add new criminal record."""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('crime_type'):
            return jsonify({'message': 'Missing required fields'}), 400
        
        criminal = Criminal(
            name=data['name'],
            alias=data.get('alias'),
            crime_type=data['crime_type'],
            description=data.get('description'),
            status=data.get('status', 'wanted'),
            danger_level=data.get('danger_level'),
            last_seen_location=data.get('last_seen_location'),
            added_by=current_user_id
        )
        
        db.session.add(criminal)
        db.session.commit()
        
        # Send alert notification
        try:
            added_by_user = User.query.get(current_user_id)
            if added_by_user:
                send_criminal_added_alert(criminal, added_by_user)
        except Exception as e:
            logger.warning(f"Failed to send criminal added alert: {str(e)}")
        
        return jsonify({
            'message': 'Criminal added successfully',
            'criminal': criminal.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to add criminal: {str(e)}'}), 500


@bp.route('/<int:criminal_id>', methods=['PUT'])
@jwt_required()
def update_criminal(criminal_id):
    """Update criminal record."""
    try:
        criminal = Criminal.query.get(criminal_id)
        
        if not criminal:
            return jsonify({'message': 'Criminal not found'}), 404
        
        data = request.get_json()
        
        # Track changes for alert
        changes = {}
        
        # Update fields and track changes
        if 'name' in data and data['name'] != criminal.name:
            changes['name'] = (criminal.name, data['name'])
            criminal.name = data['name']
        if 'alias' in data and data['alias'] != criminal.alias:
            changes['alias'] = (criminal.alias, data['alias'])
            criminal.alias = data['alias']
        if 'crime_type' in data and data['crime_type'] != criminal.crime_type:
            changes['crime_type'] = (criminal.crime_type, data['crime_type'])
            criminal.crime_type = data['crime_type']
        if 'description' in data and data['description'] != criminal.description:
            changes['description'] = (criminal.description, data['description'])
            criminal.description = data['description']
        if 'status' in data and data['status'] != criminal.status:
            changes['status'] = (criminal.status, data['status'])
            criminal.status = data['status']
        if 'danger_level' in data and data['danger_level'] != criminal.danger_level:
            changes['danger_level'] = (criminal.danger_level, data['danger_level'])
            criminal.danger_level = data['danger_level']
        if 'last_seen_location' in data and data['last_seen_location'] != criminal.last_seen_location:
            changes['last_seen_location'] = (criminal.last_seen_location, data['last_seen_location'])
            criminal.last_seen_location = data['last_seen_location']
        
        db.session.commit()
        
        # Send alert notification if there were changes
        if changes:
            try:
                current_user_id = int(get_jwt_identity())
                updated_by_user = User.query.get(current_user_id)
                if updated_by_user:
                    send_criminal_updated_alert(criminal, updated_by_user, changes)
            except Exception as e:
                logger.warning(f"Failed to send criminal updated alert: {str(e)}")
        
        return jsonify({
            'message': 'Criminal updated successfully',
            'criminal': criminal.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update criminal: {str(e)}'}), 500


@bp.route('/<int:criminal_id>', methods=['DELETE'])
@jwt_required()
def delete_criminal(criminal_id):
    """Delete criminal record."""
    try:
        criminal = Criminal.query.get(criminal_id)
        
        if not criminal:
            return jsonify({'message': 'Criminal not found'}), 404
        
        # Preserve criminal data for alert before deletion
        criminal_data = {
            'id': criminal.id,
            'name': criminal.name,
            'alias': criminal.alias,
            'crime_type': criminal.crime_type,
            'status': criminal.status,
            'danger_level': criminal.danger_level,
            'detection_count': len(criminal.detections),
            'encodings_count': len(criminal.face_encodings)
        }
        
        db.session.delete(criminal)
        db.session.commit()
        
        # Send alert notification
        try:
            current_user_id = int(get_jwt_identity())
            deleted_by_user = User.query.get(current_user_id)
            if deleted_by_user:
                send_criminal_deleted_alert(criminal_data, deleted_by_user)
        except Exception as e:
            logger.warning(f"Failed to send criminal deleted alert: {str(e)}")
        
        return jsonify({
            'message': 'Criminal deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete criminal: {str(e)}'}), 500


@bp.route('/<int:criminal_id>/photo', methods=['POST'])
@jwt_required()
def upload_criminal_photo(criminal_id):
    """
    Upload criminal photo and generate face encoding with quality assessment.
    Phase 2/3 Enhancement: Supports multiple photos per criminal with quality scores.
    """
    try:
        criminal = Criminal.query.get(criminal_id)
        if not criminal:
            return jsonify({'message': 'Criminal not found'}), 404
        
        if 'photo' not in request.files:
            return jsonify({'message': 'No photo file provided'}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'message': 'Invalid file format. Allowed: png, jpg, jpeg, gif, bmp, webp'
            }), 400
        
        # Save photo
        filename = secure_filename(file.filename)
        encodings_dir = os.path.join('encodings', str(criminal_id))
        os.makedirs(encodings_dir, exist_ok=True)
        
        # Use timestamp to avoid filename conflicts
        import time
        timestamp = int(time.time())
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(encodings_dir, filename)
        file.save(filepath)
        
        # Extract face encoding
        encoding = face_service.extract_face_encoding(filepath)
        if encoding is None:
            os.remove(filepath)  # Clean up
            return jsonify({'message': 'No face detected in photo'}), 400
        
        # Phase 3: Assess photo quality
        quality_metrics = assess_face_quality(filepath)
        quality_score = quality_metrics.get('overall_score', 0.5)
        pose_type = determine_pose_type(quality_metrics.get('frontality_score', 0.5))
        
        # Save encoding to database with quality metrics
        encoding_bytes = face_service.save_encoding(encoding)
        
        face_encoding = FaceEncoding(
            criminal_id=criminal_id,
            encoding_data=encoding_bytes,
            image_path=filepath,
            quality_score=quality_score,
            pose_type=pose_type,
            is_primary=False  # Will be updated if this is the best quality photo
        )
        
        db.session.add(face_encoding)
        
        # Check if this is the highest quality photo for this criminal
        all_encodings = FaceEncoding.query.filter_by(criminal_id=criminal_id).all()
        if quality_score >= max([enc.quality_score or 0.0 for enc in all_encodings]):
            # Mark this as primary and unmark others
            for enc in all_encodings:
                enc.is_primary = False
            face_encoding.is_primary = True
        
        db.session.commit()
        
        return jsonify({
            'message': 'Photo uploaded and encoding created successfully',
            'encoding_id': face_encoding.id,
            'quality_score': quality_score,
            'quality_metrics': quality_metrics,
            'pose_type': pose_type,
            'is_primary': face_encoding.is_primary
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Photo upload failed: {str(e)}'}), 500


@bp.route('/<int:criminal_id>/photos', methods=['POST'])
@jwt_required()
def upload_multiple_photos(criminal_id):
    """
    Upload multiple photos at once for a criminal.
    Phase 2 Enhancement: Batch upload support.
    """
    try:
        criminal = Criminal.query.get(criminal_id)
        if not criminal:
            return jsonify({'message': 'Criminal not found'}), 404
        
        # Get all files with key 'photos[]'
        files = request.files.getlist('photos[]')
        if not files or len(files) == 0:
            # Try single 'photos' key as fallback
            files = request.files.getlist('photos')
        
        if not files or len(files) == 0:
            return jsonify({'message': 'No photo files provided'}), 400
        
        results = []
        success_count = 0
        
        for file in files:
            if file.filename == '':
                continue
            
            # Validate file type
            if not allowed_file(file.filename):
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': 'Invalid file format'
                })
                continue
            
            try:
                # Save photo
                filename = secure_filename(file.filename)
                encodings_dir = os.path.join('encodings', str(criminal_id))
                os.makedirs(encodings_dir, exist_ok=True)
                
                import time
                timestamp = int(time.time())
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(encodings_dir, filename)
                file.save(filepath)
                
                # Extract encoding
                encoding = face_service.extract_face_encoding(filepath)
                if encoding is None:
                    os.remove(filepath)
                    results.append({
                        'filename': file.filename,
                        'success': False,
                        'error': 'No face detected'
                    })
                    continue
                
                # Assess quality
                quality_metrics = assess_face_quality(filepath)
                quality_score = quality_metrics.get('overall_score', 0.5)
                pose_type = determine_pose_type(quality_metrics.get('frontality_score', 0.5))
                
                # Save to database
                encoding_bytes = face_service.save_encoding(encoding)
                face_encoding = FaceEncoding(
                    criminal_id=criminal_id,
                    encoding_data=encoding_bytes,
                    image_path=filepath,
                    quality_score=quality_score,
                    pose_type=pose_type,
                    is_primary=False
                )
                
                db.session.add(face_encoding)
                success_count += 1
                
                results.append({
                    'filename': file.filename,
                    'success': True,
                    'encoding_id': face_encoding.id,
                    'quality_score': quality_score,
                    'pose_type': pose_type
                })
                
            except Exception as e:
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': str(e)
                })
        
        # Update primary photo (highest quality)
        if success_count > 0:
            all_encodings = FaceEncoding.query.filter_by(criminal_id=criminal_id).all()
            best_encoding = max(all_encodings, key=lambda e: e.quality_score or 0.0)
            for enc in all_encodings:
                enc.is_primary = (enc.id == best_encoding.id)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Uploaded {success_count}/{len(files)} photos successfully',
            'results': results
        }), 201 if success_count > 0 else 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Batch upload failed: {str(e)}'}), 500


@bp.route('/encodings/<int:encoding_id>', methods=['DELETE'])
@jwt_required()
def delete_encoding(encoding_id):
    """
    Delete a specific face encoding/photo.
    Phase 2 Enhancement: Photo management.
    """
    try:
        encoding = FaceEncoding.query.get(encoding_id)
        if not encoding:
            return jsonify({'message': 'Encoding not found'}), 404
        
        criminal_id = encoding.criminal_id
        
        # Delete physical file
        if os.path.exists(encoding.image_path):
            os.remove(encoding.image_path)
        
        db.session.delete(encoding)
        
        # If this was primary, reassign to next best quality
        if encoding.is_primary:
            remaining = FaceEncoding.query.filter_by(criminal_id=criminal_id).all()
            if remaining:
                best = max(remaining, key=lambda e: e.quality_score or 0.0)
                best.is_primary = True
        
        db.session.commit()
        
        return jsonify({'message': 'Photo deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete photo: {str(e)}'}), 500


@bp.route('/encodings/<int:encoding_id>/set-primary', methods=['PUT'])
@jwt_required()
def set_primary_photo(encoding_id):
    """
    Set a specific photo as primary for a criminal.
    Phase 2 Enhancement: Photo management.
    """
    try:
        encoding = FaceEncoding.query.get(encoding_id)
        if not encoding:
            return jsonify({'message': 'Encoding not found'}), 404
        
        # Unmark all other photos for this criminal
        FaceEncoding.query.filter_by(criminal_id=encoding.criminal_id).update({'is_primary': False})
        
        # Mark this as primary
        encoding.is_primary = True
        db.session.commit()
        
        return jsonify({'message': 'Primary photo updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update primary photo: {str(e)}'}), 500
