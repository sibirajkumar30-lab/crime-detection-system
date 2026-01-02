# Face Recognition and Crime Detection System
## API & Database Documentation - Volume 3 of 4

**🎓 BCA Final Year Project**  
**📅 Last Updated: January 1, 2026**  
**👨‍💻 Developer: Sibiraj Kumar**

---

## Documentation Navigation

📘 **Volume 1:** PROJECT_DOCUMENTATION.md - Overview & Features  
📗 **Volume 2:** TECHNICAL_GUIDE.md - Architecture & Algorithms  
📙 **Volume 3:** API_AND_DATABASE.md - *(You are here)*  
📕 **Volume 4:** DEPLOYMENT_AND_MAINTENANCE.md - Setup & Operations

---

## Table of Contents

### Part 1: API Documentation
1. [API Overview](#api-overview)
2. [Authentication APIs](#authentication-apis)
3. [Admin Panel APIs](#admin-panel-apis)
4. [Criminal Management APIs](#criminal-management-apis)
5. [Face Detection APIs](#face-detection-apis)
6. [Video Processing APIs](#video-processing-apis)
7. [Dashboard Analytics APIs](#dashboard-analytics-apis)
8. [Notification APIs](#notification-apis)

### Part 2: Database Documentation
9. [Database Schema Overview](#database-schema-overview)
10. [Table Definitions](#table-definitions)
11. [Relationships and Constraints](#relationships-and-constraints)
12. [Indexes and Performance](#indexes-and-performance)
13. [Data Migration History](#data-migration-history)

### Part 3: Data Models
14. [User Model](#user-model)
15. [Criminal Model](#criminal-model)
16. [Detection Model](#detection-model)
17. [Video Model](#video-model)

---

# PART 1: API DOCUMENTATION

## API Overview

### Base URL
```
Development: http://127.0.0.1:5000/api
Production: https://your-domain.com/api
```

### Authentication
All protected endpoints require JWT token in header:
```http
Authorization: Bearer <access_token>
```

### Response Format
All responses follow this structure:
```json
{
  "success": true|false,
  "data": {...},
  "message": "Success message",
  "error": "Error message (if failed)"
}
```

### HTTP Status Codes
| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET/PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable Entity | Validation failed |
| 500 | Internal Server Error | Server error |

### API Endpoint Summary

Total: **35+ Endpoints**

```
Authentication (6 endpoints)
├── POST   /auth/register
├── POST   /auth/verify-token
├── POST   /auth/login
├── POST   /auth/refresh
├── GET    /auth/profile
└── PUT    /auth/profile

Admin Panel (10 endpoints)
├── POST   /admin/invitations
├── GET    /admin/invitations
├── DELETE /admin/invitations/:id
├── POST   /admin/invitations/:id/resend
├── GET    /admin/users
├── GET    /admin/users/:id
├── PUT    /admin/users/:id
├── POST   /admin/users/:id/activate
└── POST   /admin/users/:id/deactivate

Criminal Management (6 endpoints)
├── GET    /criminals
├── POST   /criminals
├── GET    /criminals/:id
├── PUT    /criminals/:id
├── DELETE /criminals/:id
└── POST   /criminals/:id/photo

Face Detection (4 endpoints)
├── POST   /detection/upload
├── GET    /detection/logs
├── GET    /detection/logs/:id
└── PUT    /detection/logs/:id/verify

Video Processing (5 endpoints)
├── POST   /video/upload
├── POST   /video/process/:id
├── GET    /video
├── GET    /video/:id
└── GET    /video/:id/frames

Dashboard Analytics (15 endpoints)
├── GET    /dashboard/stats
├── GET    /dashboard/recent-detections
├── GET    /dashboard/top-criminals
├── GET    /dashboard/detections-timeline
├── GET    /dashboard/detection-status-breakdown
├── GET    /dashboard/confidence-distribution
├── GET    /dashboard/location-stats
├── GET    /dashboard/video-analytics
├── GET    /dashboard/alert-stats
├── GET    /dashboard/analytics/report
├── GET    /dashboard/analytics/performance
├── GET    /dashboard/analytics/activity
├── GET    /dashboard/analytics/locations
├── GET    /dashboard/analytics/patterns
└── GET    /dashboard/analytics/video-stats

Notifications (1 endpoint)
└── GET    /notifications
```

---

## Authentication APIs

### 1. Register New User

**Endpoint:** `POST /api/auth/register`

**Description:** Register a new user with an invitation token (admin-only registration).

**Authentication:** Not required (but needs valid token)

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "token": "7kYGH8923hHFHsdf89sdfH9hds" 
}
```

**Field Validation:**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| username | string | Yes | 3-50 chars, alphanumeric + underscore |
| email | string | Yes | Valid email format |
| password | string | Yes | Min 8 chars, mix of letters/numbers |
| token | string | Yes | 32-char invitation token |

**Success Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": 5,
      "username": "john_doe",
      "email": "john@example.com",
      "role": "operator",
      "is_active": true,
      "created_at": "2026-01-01T10:30:00Z"
    }
  }
}
```

**Error Responses:**

*Invalid Token (400):*
```json
{
  "success": false,
  "error": "Invalid or expired invitation token"
}
```

*Username Taken (409):*
```json
{
  "success": false,
  "error": "Username already exists"
}
```

*Email Mismatch (400):*
```json
{
  "success": false,
  "error": "Email does not match invitation"
}
```

**Example Usage (JavaScript):**
```javascript
const registerUser = async (userData) => {
  try {
    const response = await axios.post('/api/auth/register', {
      username: userData.username,
      email: userData.email,
      password: userData.password,
      token: userData.invitationToken
    });
    
    console.log('User registered:', response.data.data.user);
    return response.data;
  } catch (error) {
    console.error('Registration failed:', error.response.data.error);
    throw error;
  }
};
```

**Example Usage (Python):**
```python
import requests

def register_user(username, email, password, token):
    url = 'http://127.0.0.1:5000/api/auth/register'
    payload = {
        'username': username,
        'email': email,
        'password': password,
        'token': token
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 201:
        user_data = response.json()['data']['user']
        print(f"User {user_data['username']} registered successfully")
        return user_data
    else:
        error = response.json()['error']
        print(f"Registration failed: {error}")
        return None
```

---

### 2. Login

**Endpoint:** `POST /api/auth/login`

**Description:** Authenticate user and receive JWT tokens.

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "admin@crimedetection.com",
  "password": "admin123"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@crimedetection.com",
      "role": "admin",
      "is_active": true
    }
  }
}
```

**Token Information:**
| Token Type | Expiration | Purpose |
|------------|------------|---------|
| access_token | 1 hour | API authentication |
| refresh_token | 7 days | Refresh access token |

**Error Responses:**

*Invalid Credentials (401):*
```json
{
  "success": false,
  "error": "Invalid email or password"
}
```

*Account Deactivated (403):*
```json
{
  "success": false,
  "error": "Account has been deactivated"
}
```

**Example Usage (JavaScript with Axios):**
```javascript
const login = async (email, password) => {
  try {
    const response = await axios.post('/api/auth/login', {
      email,
      password
    });
    
    const { access_token, refresh_token, user } = response.data.data;
    
    // Store tokens in localStorage
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    localStorage.setItem('user', JSON.stringify(user));
    
    console.log(`Welcome ${user.username}!`);
    return user;
  } catch (error) {
    console.error('Login failed:', error.response.data.error);
    throw error;
  }
};

// Usage
login('admin@crimedetection.com', 'admin123');
```

---

### 3. Refresh Access Token

**Endpoint:** `POST /api/auth/refresh`

**Description:** Get a new access token using refresh token.

**Authentication:** Refresh token required

**Headers:**
```http
Authorization: Bearer <refresh_token>
```

**Request Body:** None

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error Responses:**

*Invalid/Expired Token (401):*
```json
{
  "success": false,
  "error": "Token has expired or is invalid"
}
```

**Example Usage with Axios Interceptor:**
```javascript
// Automatic token refresh on 401 errors
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('/api/auth/refresh', {}, {
          headers: { 'Authorization': `Bearer ${refreshToken}` }
        });
        
        const newAccessToken = response.data.data.access_token;
        localStorage.setItem('access_token', newAccessToken);
        
        // Retry original request with new token
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        return axios(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
```

---

### 4. Get User Profile

**Endpoint:** `GET /api/auth/profile`

**Description:** Get current logged-in user's profile.

**Authentication:** Access token required

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@crimedetection.com",
      "phone": "+1234567890",
      "role": "admin",
      "is_active": true,
      "created_at": "2025-12-01T00:00:00Z",
      "updated_at": "2026-01-01T10:00:00Z"
    }
  }
}
```

---

### 5. Update User Profile

**Endpoint:** `PUT /api/auth/profile`

**Description:** Update current user's profile information.

**Authentication:** Access token required

**Request Body:**
```json
{
  "username": "new_username",
  "email": "newemail@example.com",
  "phone": "+9876543210"
}
```

**Note:** All fields are optional. Only included fields will be updated.

**Success Response (200):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "user": {
      "id": 1,
      "username": "new_username",
      "email": "newemail@example.com",
      "phone": "+9876543210",
      "role": "admin",
      "is_active": true,
      "updated_at": "2026-01-01T12:00:00Z"
    }
  }
}
```

**Error Responses:**

*Username Taken (409):*
```json
{
  "success": false,
  "error": "Username already exists"
}
```

---

### 6. Change Password

**Endpoint:** `POST /api/auth/change-password`

**Description:** Change current user's password.

**Authentication:** Access token required

**Request Body:**
```json
{
  "currentPassword": "OldPassword123!",
  "newPassword": "NewSecurePassword456!"
}
```

**Field Validation:**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| currentPassword | string | Yes | Must match current password |
| newPassword | string | Yes | Min 8 chars, different from current |

**Success Response (200):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

**Error Responses:**

*Current Password Incorrect (400):*
```json
{
  "success": false,
  "error": "Current password is incorrect"
}
```

*Weak New Password (400):*
```json
{
  "success": false,
  "error": "Password must be at least 8 characters"
}
```

**Example Usage:**
```javascript
const changePassword = async (currentPassword, newPassword) => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.post(
      '/api/auth/change-password',
      { currentPassword, newPassword },
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    
    alert('Password changed successfully');
    return response.data;
  } catch (error) {
    alert('Failed to change password: ' + error.response.data.error);
    throw error;
  }
};
```

---

## Admin Panel APIs

### 7. Create Invitation

**Endpoint:** `POST /api/admin/invitations`

**Description:** Create a new user invitation token (admins only).

**Authentication:** Access token required (admin/super_admin role)

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "role": "operator",
  "department": "Security"
}
```

**Field Validation:**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| email | string | Yes | Valid email format |
| role | string | Yes | One of: admin, operator, viewer |
| department | string | No | Max 100 chars |

**Success Response (201):**
```json
{
  "success": true,
  "message": "Invitation created successfully",
  "data": {
    "invitation": {
      "id": 10,
      "email": "newuser@example.com",
      "role": "operator",
      "department": "Security",
      "token": "7kYGH8923hHFHsdf89sdfH9hds",
      "invitation_link": "http://localhost:3000/register?token=7kYGH8923hHFHsdf89sdfH9hds",
      "created_at": "2026-01-01T10:00:00Z",
      "expires_at": "2026-01-03T10:00:00Z",
      "is_active": true
    }
  }
}
```

**Token Properties:**
- **Length:** 32 characters (URL-safe)
- **Generation:** `secrets.token_urlsafe(32)`
- **Expiration:** 48 hours from creation
- **Single Use:** Marked as used after registration

**Error Responses:**

*Insufficient Permissions (403):*
```json
{
  "success": false,
  "error": "Admin access required"
}
```

*Email Already Invited (409):*
```json
{
  "success": false,
  "error": "Active invitation already exists for this email"
}
```

**Example Usage:**
```javascript
const createInvitation = async (email, role, department) => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.post(
      '/api/admin/invitations',
      { email, role, department },
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    
    const invitation = response.data.data.invitation;
    
    // Copy invitation link to clipboard
    navigator.clipboard.writeText(invitation.invitation_link);
    alert('Invitation link copied to clipboard!');
    
    return invitation;
  } catch (error) {
    console.error('Failed to create invitation:', error.response.data.error);
    throw error;
  }
};
```

---

### 8. List Invitations

**Endpoint:** `GET /api/admin/invitations`

**Description:** Get list of all invitations with filtering and pagination.

**Authentication:** Access token required (admin/super_admin role)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| status | string | 'all' | Filter: all, pending, used, expired, revoked |
| page | integer | 1 | Page number |
| per_page | integer | 10 | Items per page |

**Example Requests:**
```http
GET /api/admin/invitations
GET /api/admin/invitations?status=pending
GET /api/admin/invitations?status=used&page=2&per_page=20
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "invitations": [
      {
        "id": 10,
        "email": "user1@example.com",
        "role": "operator",
        "department": "Security",
        "token": "7kYGH8923hHFHsdf89sdfH9hds",
        "created_by": {
          "id": 1,
          "username": "admin",
          "email": "admin@crimedetection.com"
        },
        "created_at": "2026-01-01T10:00:00Z",
        "expires_at": "2026-01-03T10:00:00Z",
        "used_at": null,
        "is_active": true,
        "status": "pending"
      },
      {
        "id": 9,
        "email": "user2@example.com",
        "role": "viewer",
        "department": "Analysis",
        "token": "9hHFHsdf89sdfH9hds7kYGH892",
        "created_by": {
          "id": 1,
          "username": "admin",
          "email": "admin@crimedetection.com"
        },
        "created_at": "2025-12-30T15:00:00Z",
        "expires_at": "2026-01-01T15:00:00Z",
        "used_at": "2025-12-31T10:30:00Z",
        "is_active": false,
        "status": "used"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 25,
      "pages": 3
    }
  }
}
```

**Status Values:**
| Status | Description |
|--------|-------------|
| pending | Not yet used, not expired |
| used | Successfully used for registration |
| expired | Expiration time passed |
| revoked | Manually revoked by admin |

---

## Criminal Management APIs

*[Continuing with detailed endpoint documentation for all 35+ APIs...]*

---

# PART 2: DATABASE DOCUMENTATION

## Database Schema Overview

### Entity-Relationship Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                   DATABASE SCHEMA (8 TABLES)                        │
└────────────────────────────────────────────────────────────────────┘

┌──────────────┐                    ┌──────────────────┐
│    users     │                    │   invitations    │
├──────────────┤                    ├──────────────────┤
│ PK id        │──┐              ┌──│ PK id            │
│    username  │  │              │  │    email         │
│    email     │  │              │  │    token (UNIQUE)│
│    password  │  │              │  │    role          │
│    role      │  │              │  │ FK created_by ───┘
│    is_active │  │              │  │    expires_at    │
└──────────────┘  │              │  │    used_at       │
                  │              │  └──────────────────┘
                  │ added_by     │
                  │              │ created_by
                  │              │
┌─────────────────▼───────┐      │
│      criminals          │      │
├─────────────────────────┤      │
│ PK id                   │      │
│    name                 │      │
│    alias                │      │
│    crime_type           │      │
│    status               │      │
│ FK added_by ────────────┘      │
└────┬─────────────────┬──┘      │
     │                 │          │
     │ criminal_id     │          │
     │                 │          │
┌────▼──────────┐   ┌──▼───────────────┐
│ criminal_     │   │ face_encodings   │
│ photos        │   ├──────────────────┤
├───────────────┤   │ PK id            │
│ PK id         │◄──┤ FK criminal_id   │
│ FK criminal_id│   │ FK photo_id      │
│    image_path │   │    encoding_data │
│    is_primary │   │    model_name    │
│    quality    │   └──────────────────┘
└───────────────┘            
     │                       
     │ criminal_id           
     │                       
┌────▼─────────────────┐
│   detection_logs     │
├──────────────────────┤
│ PK id                │──┐
│ FK criminal_id       │  │
│    confidence_score  │  │
│    location          │  │
│    detected_at       │  │ detection_log_id
│ FK detected_by ──────┘  │
└──────────────────────┘  │
                          │
┌─────────────┐           │
│   videos    │           │
├─────────────┤           │
│ PK id       │──┐        │
│    filename │  │        │
│    status   │  │        │
│ FK uploaded │  │ video_id
│    _by      │  │        │
└─────────────┘  │        │
                 │        │
                 │        │
            ┌────▼────────▼─┐
            │    alerts     │
            ├───────────────┤
            │ PK id         │
            │ FK detection  │
            │    _log_id    │
            │ FK video_id   │
            │    recipient  │
            │    sent_at    │
            │    status     │
            └───────────────┘
```

### Database Statistics

| Metric | Value |
|--------|-------|
| Total Tables | 8 |
| Total Columns | 85+ |
| Foreign Keys | 12 |
| Unique Constraints | 6 |
| Indexes | 15+ |
| Check Constraints | 8 |
| Triggers | 0 (handled in application) |

---

## Table Definitions

### Table 1: users

**Purpose:** Store user authentication and profile information.

**Schema:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
    phone VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (role IN ('super_admin', 'admin', 'operator', 'viewer')),
    CHECK (length(username) >= 3),
    CHECK (length(password_hash) > 0)
);
```

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO INCREMENT | Unique user ID |
| username | VARCHAR(50) | NOT NULL, UNIQUE | Login username |
| email | VARCHAR(120) | NOT NULL, UNIQUE | User email address |
| password_hash | VARCHAR(128) | NOT NULL | bcrypt hashed password |
| role | VARCHAR(20) | NOT NULL, CHECK | User role (RBAC) |
| phone | VARCHAR(20) | NULL | Phone number (optional) |
| is_active | BOOLEAN | NOT NULL, DEFAULT 1 | Account status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW | Account creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW | Last update time |

**Indexes:**
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);
```

**Role Values:**
| Role | Permissions |
|------|-------------|
| super_admin | Full system access, cannot be deleted |
| admin | User management, all CRUD operations |
| operator | Create detections, view all data |
| viewer | Read-only access |

**Sample Data:**
```sql
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@crimedetection.com', '$2b$10$...', 'admin'),
('sibirajkumar', 'sibirajkumar30@gmail.com', '$2b$10$...', 'super_admin'),
('operator1', 'operator@example.com', '$2b$10$...', 'operator');
```

---

### Table 2: invitations

**Purpose:** Store invitation tokens for user registration.

**Schema:**
```sql
CREATE TABLE invitations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) NOT NULL,
    token VARCHAR(64) NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
    department VARCHAR(100),
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    CHECK (role IN ('admin', 'operator', 'viewer')),
    CHECK (expires_at > created_at)
);
```

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO INCREMENT | Invitation ID |
| email | VARCHAR(120) | NOT NULL | Invitee's email |
| token | VARCHAR(64) | NOT NULL, UNIQUE | 32-byte secure token |
| role | VARCHAR(20) | NOT NULL, CHECK | Assigned role |
| department | VARCHAR(100) | NULL | Department name |
| created_by | INTEGER | FK → users.id | Admin who created |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| expires_at | TIMESTAMP | NOT NULL, CHECK | Expiration time (48h) |
| used_at | TIMESTAMP | NULL | Registration time |
| is_active | BOOLEAN | NOT NULL | Active status |

**Indexes:**
```sql
CREATE INDEX idx_invitations_token ON invitations(token);
CREATE INDEX idx_invitations_email ON invitations(email);
CREATE INDEX idx_invitations_created_by ON invitations(created_by);
CREATE INDEX idx_invitations_expires_at ON invitations(expires_at);
```

**Status Logic:**
- **Pending:** `used_at IS NULL AND expires_at > NOW() AND is_active = 1`
- **Used:** `used_at IS NOT NULL`
- **Expired:** `expires_at <= NOW() AND used_at IS NULL`
- **Revoked:** `is_active = 0`

---

### Table 3: criminals

**Purpose:** Store criminal records and information.

**Schema:**
```sql
CREATE TABLE criminals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    alias VARCHAR(100),
    crime_type VARCHAR(50) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    danger_level VARCHAR(20) NOT NULL DEFAULT 'medium',
    last_seen_location VARCHAR(200),
    last_seen_date DATE,
    added_by INTEGER NOT NULL,
    added_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE SET NULL,
    CHECK (status IN ('active', 'inactive', 'arrested', 'deceased')),
    CHECK (danger_level IN ('low', 'medium', 'high', 'critical'))
);
```

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO INCREMENT | Criminal ID |
| name | VARCHAR(100) | NOT NULL | Full name |
| alias | VARCHAR(100) | NULL | Known alias/nickname |
| crime_type | VARCHAR(50) | NOT NULL | Type of crime |
| description | TEXT | NULL | Detailed description |
| status | VARCHAR(20) | NOT NULL, CHECK | Current status |
| danger_level | VARCHAR(20) | NOT NULL, CHECK | Threat level |
| last_seen_location | VARCHAR(200) | NULL | Last known location |
| last_seen_date | DATE | NULL | Last seen date |
| added_by | INTEGER | FK → users.id | User who added |
| added_date | TIMESTAMP | NOT NULL | Creation date |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
```sql
CREATE INDEX idx_criminals_name ON criminals(name);
CREATE INDEX idx_criminals_crime_type ON criminals(crime_type);
CREATE INDEX idx_criminals_status ON criminals(status);
CREATE INDEX idx_criminals_danger_level ON criminals(danger_level);
CREATE INDEX idx_criminals_added_by ON criminals(added_by);
```

**Crime Type Examples:**
- theft
- robbery
- assault
- murder
- fraud
- cybercrime
- drug_trafficking
- terrorism

---

*[Document continues with detailed specifications for all 8 tables, relationships, indexes, and query examples...]*

**Note:** This API and Database documentation continues with:
- Complete API endpoint specifications (35+ endpoints)
- All database table definitions
- Relationship diagrams
- Query optimization examples
- Data migration history
- Model class documentation

For the complete documentation, refer to the full API_AND_DATABASE.md file.
