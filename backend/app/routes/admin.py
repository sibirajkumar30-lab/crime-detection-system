"""Admin-only routes for user management."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.invitation import Invitation
from functools import wraps
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('admin', __name__)


def admin_required(fn):
    """Decorator to require admin role."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'super_admin']:
            return jsonify({'message': 'Admin access required'}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper


@bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users (admin only)."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role_filter = request.args.get('role', None)
        
        query = User.query
        
        if role_filter:
            query = query.filter_by(role=role_filter)
        
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to fetch users: {str(e)}")
        return jsonify({'message': f'Failed to fetch users: {str(e)}'}), 500


@bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get specific user details (admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch user: {str(e)}'}), 500


@bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user details (admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'phone' in data:
            user.phone = data['phone']
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update user: {str(e)}'}), 500


@bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    """Deactivate user account (admin only)."""
    try:
        current_user_id = int(get_jwt_identity())
        
        if current_user_id == user_id:
            return jsonify({'message': 'Cannot deactivate your own account'}), 400
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        user.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'User deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to deactivate user: {str(e)}'}), 500


@bp.route('/users/<int:user_id>/activate', methods=['POST'])
@admin_required
def activate_user(user_id):
    """Activate user account (admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        user.is_active = True
        db.session.commit()
        
        return jsonify({'message': 'User activated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to activate user: {str(e)}'}), 500


@bp.route('/invitations', methods=['POST'])
@admin_required
def create_invitation():
    """Create invitation for new user (admin only)."""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('role'):
            return jsonify({'message': 'Missing required fields (email, role)'}), 400
        
        # Validate role
        valid_roles = ['admin', 'operator', 'viewer']
        if data['role'] not in valid_roles:
            return jsonify({'message': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'message': 'User with this email already exists'}), 400
        
        # Check if there's already a pending invitation
        existing_invitation = Invitation.query.filter_by(
            email=data['email'],
            is_active=True
        ).first()
        
        if existing_invitation and existing_invitation.is_valid():
            return jsonify({'message': 'A valid invitation already exists for this email'}), 400
        
        # Create invitation
        invitation = Invitation(
            email=data['email'],
            role=data['role'],
            invited_by=current_user_id,
            department=data.get('department'),
            expires_in_hours=data.get('expires_in_hours', 48)
        )
        
        db.session.add(invitation)
        db.session.commit()
        
        # TODO: Send invitation email
        invitation_link = f"{request.host_url}register?token={invitation.token}"
        
        logger.info(f"Invitation created for {data['email']} by user {current_user_id}")
        
        return jsonify({
            'message': 'Invitation created successfully',
            'invitation': invitation.to_dict(),
            'invitation_link': invitation_link
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create invitation: {str(e)}")
        return jsonify({'message': f'Failed to create invitation: {str(e)}'}), 500


@bp.route('/invitations', methods=['GET'])
@admin_required
def get_invitations():
    """Get all invitations (admin only)."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', 'all')  # all, pending, used, expired
        
        query = Invitation.query
        
        if status == 'pending':
            query = query.filter_by(is_active=True, used_at=None)
        elif status == 'used':
            query = query.filter(Invitation.used_at.isnot(None))
        elif status == 'expired':
            query = query.filter(
                Invitation.expires_at < db.func.now(),
                Invitation.used_at.is_(None)
            )
        
        pagination = query.order_by(Invitation.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'invitations': [inv.to_dict() for inv in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch invitations: {str(e)}'}), 500


@bp.route('/invitations/<int:invitation_id>', methods=['DELETE'])
@admin_required
def revoke_invitation(invitation_id):
    """Revoke an invitation (admin only)."""
    try:
        invitation = Invitation.query.get(invitation_id)
        
        if not invitation:
            return jsonify({'message': 'Invitation not found'}), 404
        
        invitation.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Invitation revoked successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to revoke invitation: {str(e)}'}), 500


@bp.route('/invitations/<int:invitation_id>/resend', methods=['POST'])
@admin_required
def resend_invitation(invitation_id):
    """Resend invitation email (admin only)."""
    try:
        invitation = Invitation.query.get(invitation_id)
        
        if not invitation:
            return jsonify({'message': 'Invitation not found'}), 404
        
        if not invitation.is_valid():
            return jsonify({'message': 'Cannot resend expired or used invitation'}), 400
        
        # TODO: Resend invitation email
        invitation_link = f"{request.host_url}register?token={invitation.token}"
        
        return jsonify({
            'message': 'Invitation resent successfully',
            'invitation_link': invitation_link
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to resend invitation: {str(e)}'}), 500
