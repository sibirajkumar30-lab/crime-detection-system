"""Notification routes for in-app alerts."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import or_, and_
from app import db
from app.models.alert import Alert
from app.models.user import User

bp = Blueprint('notifications', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    """
    Get all alerts (email and in-app notifications) for viewing history.
    
    Query params:
        - unread_only: true/false (default: false)
        - limit: int (default: 50)
        - severity: info/warning/critical
        - category: detection/criminal_mgmt/system/operational
    """
    try:
        current_user_id = int(get_jwt_identity())
        
        # Query parameters
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = request.args.get('limit', 100, type=int)
        severity = request.args.get('severity')
        category = request.args.get('category')
        
        # Build query for ALL alerts (not just in_app)
        query = Alert.query
        
        # Apply filters
        if unread_only:
            query = query.filter(Alert.acknowledged == False)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        if category:
            query = query.filter(Alert.category == category)
        
        # Get alerts, newest first
        alerts = query.order_by(
            Alert.sent_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'notifications': [a.to_dict() for a in alerts],
            'total': query.count(),
            'unread_count': Alert.query.filter(Alert.acknowledged == False).count()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get notifications: {str(e)}'}), 500


@bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get count of unread notifications for current user."""
    try:
        current_user_id = int(get_jwt_identity())
        
        count = Alert.query.filter(
            Alert.delivery_method == 'in_app',
            Alert.acknowledged == False
            # Note: user_id column not in DB yet
            # or_(
            #     Alert.user_id == current_user_id,
            #     Alert.user_id.is_(None)
            # )
        ).count()
        
        return jsonify({'unread_count': count}), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get count: {str(e)}'}), 500


@bp.route('/<int:notification_id>/mark-read', methods=['PUT'])
@jwt_required()
def mark_as_read(notification_id):
    """Mark a notification as read."""
    try:
        current_user_id = int(get_jwt_identity())
        
        notification = Alert.query.get(notification_id)
        if not notification:
            return jsonify({'message': 'Notification not found'}), 404
        
        # Note: user_id column not in DB yet, so allowing access to all
        # if notification.user_id and notification.user_id != current_user_id:
        # if notification.user_id and notification.user_id != current_user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        notification.acknowledged = True
        notification.acknowledged_by = current_user_id
        notification.acknowledged_at = datetime.utcnow()
        notification.status = 'read'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Notification marked as read',
            'notification': notification.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to mark as read: {str(e)}'}), 500


@bp.route('/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_as_read():
    """Mark all notifications as read for current user."""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Update all unread notifications
        Alert.query.filter(
            Alert.delivery_method == 'in_app',
            Alert.acknowledged == False
            # Note: user_id column not in DB yet
            # or_(
            #     Alert.user_id == current_user_id,
            #     Alert.user_id.is_(None)
            # )
        ).update({
            'acknowledged': True,
            'acknowledged_by': current_user_id,
            'acknowledged_at': datetime.utcnow(),
            'status': 'read'
        }, synchronize_session=False)
        
        db.session.commit()
        
        return jsonify({'message': 'All notifications marked as read'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to mark all as read: {str(e)}'}), 500


@bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """Delete a notification."""
    try:
        current_user_id = int(get_jwt_identity())
        
        notification = Alert.query.get(notification_id)
        if not notification:
            return jsonify({'message': 'Notification not found'}), 404
        # Note: user_id column not in DB yet
        # if notification.user_id and notification.user_id != current_user_id:
        # # Verify user has access
        if notification.user_id and notification.user_id != current_user_id:
            return jsonify({'message': 'Unauthorized'}), 403
        
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({'message': 'Notification deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete: {str(e)}'}), 500


@bp.route('/clear-old', methods=['DELETE'])
@jwt_required()
def clear_old_notifications():
    """Clear notifications older than 30 days."""
    try:
        current_user_id = int(get_jwt_identity())
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Delete old acknowledged notifications
        Alert.query.filter(
            Alert.delivery_method == 'in_app',
            Alert.acknowledged == True,
            Alert.created_at < thirty_days_ago
            # Note: user_id column not in DB yet
            # or_(
            #     Alert.user_id == current_user_id,
            #     Alert.user_id.is_(None)
            # )
        ).delete(synchronize_session=False)
        
        db.session.commit()
        
        return jsonify({'message': 'Old notifications cleared'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to clear: {str(e)}'}), 500
