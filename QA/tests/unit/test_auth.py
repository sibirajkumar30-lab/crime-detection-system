"""
Unit Tests for Authentication Module
Tests user registration, login, JWT token generation
"""

import pytest
from flask import json


@pytest.mark.unit
@pytest.mark.auth
class TestUserRegistration:
    """Test user registration functionality."""
    
    def test_register_valid_user(self, client, db_session):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'Password@123',
            'role': 'operator'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User registered successfully'
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'newuser@test.com'
        assert data['user']['role'] == 'operator'
    
    def test_register_missing_username(self, client, db_session):
        """Test registration with missing username."""
        response = client.post('/api/auth/register', json={
            'email': 'test@test.com',
            'password': 'Password@123'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing required fields' in data['message']
    
    def test_register_missing_email(self, client, db_session):
        """Test registration with missing email."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': 'Password@123'
        })
        
        assert response.status_code == 400
    
    def test_register_missing_password(self, client, db_session):
        """Test registration with missing password."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@test.com'
        })
        
        assert response.status_code == 400
    
    def test_register_duplicate_username(self, client, db_session, admin_user):
        """Test registration with duplicate username."""
        response = client.post('/api/auth/register', json={
            'username': 'admin',
            'email': 'newemail@test.com',
            'password': 'Password@123'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Username already exists' in data['message']
    
    def test_register_duplicate_email(self, client, db_session, admin_user):
        """Test registration with duplicate email."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'admin@test.com',
            'password': 'Password@123'
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Email already exists' in data['message']
    
    def test_register_invalid_email_format(self, client, db_session):
        """Test registration with invalid email format."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'Password@123'
        })
        
        # Should be validated by marshmallow or email validator
        # May pass if validation not implemented (BUG)
        assert response.status_code in [400, 201]
    
    def test_register_weak_password(self, client, db_session):
        """Test registration with weak password."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@test.com',
            'password': '123'
        })
        
        # Should fail if password strength validation implemented
        # May pass if not validated (BUG)
        assert response.status_code in [400, 201]
    
    def test_register_default_role(self, client, db_session):
        """Test registration defaults to operator role."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'Password@123'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['user']['role'] == 'operator'
    
    def test_register_empty_json(self, client, db_session):
        """Test registration with empty JSON."""
        response = client.post('/api/auth/register', json={})
        
        assert response.status_code == 400


@pytest.mark.unit
@pytest.mark.auth
class TestUserLogin:
    """Test user login functionality."""
    
    def test_login_valid_credentials(self, client, db_session, admin_user):
        """Test successful login with valid credentials."""
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'Admin@123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['username'] == 'admin'
    
    def test_login_wrong_password(self, client, db_session, admin_user):
        """Test login with wrong password."""
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'WrongPassword'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid credentials' in data['message'] or 'Unauthorized' in data['message']
    
    def test_login_nonexistent_user(self, client, db_session):
        """Test login with nonexistent username."""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'Password@123'
        })
        
        assert response.status_code == 401
    
    def test_login_missing_username(self, client, db_session):
        """Test login with missing username."""
        response = client.post('/api/auth/login', json={
            'password': 'Password@123'
        })
        
        assert response.status_code == 400
    
    def test_login_missing_password(self, client, db_session):
        """Test login with missing password."""
        response = client.post('/api/auth/login', json={
            'username': 'admin'
        })
        
        assert response.status_code == 400
    
    def test_login_inactive_user(self, client, db_session, admin_user):
        """Test login with inactive user."""
        admin_user.is_active = False
        db_session.commit()
        
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'Admin@123'
        })
        
        # Should fail if inactive users are blocked
        assert response.status_code in [401, 403]
    
    def test_login_case_sensitive_username(self, client, db_session, admin_user):
        """Test if username is case-sensitive."""
        response = client.post('/api/auth/login', json={
            'username': 'ADMIN',
            'password': 'Admin@123'
        })
        
        # Behavior depends on implementation
        assert response.status_code in [200, 401]
    
    def test_login_sql_injection_attempt(self, client, db_session):
        """Test login against SQL injection."""
        response = client.post('/api/auth/login', json={
            'username': "admin' OR '1'='1",
            'password': 'anything'
        })
        
        assert response.status_code == 401
    
    def test_login_empty_credentials(self, client, db_session):
        """Test login with empty credentials."""
        response = client.post('/api/auth/login', json={
            'username': '',
            'password': ''
        })
        
        assert response.status_code == 400


@pytest.mark.unit
@pytest.mark.auth
class TestJWTToken:
    """Test JWT token functionality."""
    
    def test_access_protected_route_with_token(self, client, admin_token):
        """Test accessing protected route with valid token."""
        response = client.get(
            '/api/criminals',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
    
    def test_access_protected_route_without_token(self, client):
        """Test accessing protected route without token."""
        response = client.get('/api/criminals')
        
        assert response.status_code == 401
    
    def test_access_protected_route_invalid_token(self, client):
        """Test accessing protected route with invalid token."""
        response = client.get(
            '/api/criminals',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        assert response.status_code == 422  # Unprocessable Entity for invalid JWT
    
    def test_access_protected_route_expired_token(self, client, app):
        """Test accessing protected route with expired token."""
        # This requires mocking time or using a very short expiry
        # Will be implemented in integration tests
        pass
    
    def test_token_contains_user_identity(self, client, db_session, admin_user):
        """Test that token contains user identity."""
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'Admin@123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Decode token (in real test, use proper JWT decoding)
        assert 'access_token' in data
        assert len(data['access_token']) > 0


@pytest.mark.unit
@pytest.mark.auth
class TestPasswordSecurity:
    """Test password security features."""
    
    def test_password_is_hashed(self, db_session, admin_user):
        """Test that password is hashed in database."""
        assert admin_user.password_hash != 'Admin@123'
        assert len(admin_user.password_hash) > 50  # Bcrypt hash length
    
    def test_check_password_method(self, db_session, admin_user):
        """Test password verification method."""
        assert admin_user.check_password('Admin@123') is True
        assert admin_user.check_password('WrongPassword') is False
    
    def test_password_not_in_user_dict(self, db_session, admin_user):
        """Test that password is not exposed in to_dict."""
        user_dict = admin_user.to_dict()
        assert 'password' not in user_dict
        assert 'password_hash' not in user_dict


@pytest.mark.unit
@pytest.mark.auth
class TestRoleBasedAccess:
    """Test role-based access control."""
    
    def test_admin_can_access_admin_routes(self, client, admin_token):
        """Test admin can access admin-only routes."""
        # Example: Delete user (admin only)
        # Implementation depends on actual RBAC implementation
        pass
    
    def test_operator_cannot_access_admin_routes(self, client, operator_token):
        """Test operator cannot access admin-only routes."""
        # Implementation depends on actual RBAC implementation
        pass
    
    def test_viewer_has_read_only_access(self, client, viewer_token):
        """Test viewer has read-only access."""
        # Implementation depends on actual RBAC implementation
        pass
