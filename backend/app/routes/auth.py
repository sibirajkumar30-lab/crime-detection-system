"""Authentication routes."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.invitation import Invitation

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user using invitation token (admin-only registration)."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('token') or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Missing required fields (token, username, password)'}), 400
        
        # Verify invitation token
        invitation = Invitation.query.filter_by(token=data['token']).first()
        
        if not invitation:
            return jsonify({'message': 'Invalid invitation token'}), 400
        
        if not invitation.is_valid():
            return jsonify({'message': 'Invitation token has expired or been used'}), 400
        
        # Verify email matches (if provided)
        email = data.get('email', invitation.email)
        if email != invitation.email:
            return jsonify({'message': 'Email does not match invitation'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already exists'}), 400
        
        # Create new user with role from invitation
        user = User(
            username=data['username'],
            email=email,
            phone=data.get('phone'),
            role=invitation.role
        )
        user.set_password(data['password'])
        
        # Mark invitation as used
        invitation.mark_as_used()
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500


@bp.route('/verify-token', methods=['POST'])
def verify_invitation_token():
    """Verify invitation token validity."""
    try:
        data = request.get_json()
        
        if not data or not data.get('token'):
            return jsonify({'message': 'Missing invitation token'}), 400
        
        invitation = Invitation.query.filter_by(token=data['token']).first()
        
        if not invitation:
            return jsonify({'message': 'Invalid invitation token', 'valid': False}), 404
        
        if not invitation.is_valid():
            return jsonify({
                'message': 'Invitation token has expired or been used',
                'valid': False
            }), 400
        
        return jsonify({
            'message': 'Token is valid',
            'valid': True,
            'email': invitation.email,
            'role': invitation.role,
            'department': invitation.department,
            'expires_at': invitation.expires_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Token verification failed: {str(e)}'}), 500


@bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens."""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'message': 'Account is deactivated'}), 403
        
        # Create tokens - identity must be a string
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Token refresh failed: {str(e)}'}), 500


@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile."""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch profile: {str(e)}'}), 500


@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile."""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'username' in data:
            # Check if username is taken
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user.id:
                return jsonify({'message': 'Username already taken'}), 400
            user.username = data['username']
        
        if 'email' in data:
            # Check if email is taken
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user.id:
                return jsonify({'message': 'Email already taken'}), 400
            user.email = data['email']
        
        if 'phone' in data:
            user.phone = data['phone']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Profile update failed: {str(e)}'}), 500


@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password."""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('currentPassword') or not data.get('newPassword'):
            return jsonify({'message': 'Missing current or new password'}), 400
        
        # Verify current password
        if not user.check_password(data['currentPassword']):
            return jsonify({'message': 'Current password is incorrect'}), 401
        
        # Validate new password
        if len(data['newPassword']) < 6:
            return jsonify({'message': 'New password must be at least 6 characters'}), 400
        
        # Update password
        user.set_password(data['newPassword'])
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Password change failed: {str(e)}'}), 500
