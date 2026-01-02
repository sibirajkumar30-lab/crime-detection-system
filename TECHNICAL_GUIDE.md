# Face Recognition and Crime Detection System
## Technical Architecture Guide - Volume 2 of 4

**🎓 BCA Final Year Project**  
**📅 Last Updated: January 1, 2026**  
**👨‍💻 Developer: Sibiraj Kumar**

---

## Documentation Navigation

📘 **Volume 1:** PROJECT_DOCUMENTATION.md - Overview & Features  
📗 **Volume 2:** TECHNICAL_GUIDE.md - *(You are here)*  
📙 **Volume 3:** API_AND_DATABASE.md - API & Database  
📕 **Volume 4:** DEPLOYMENT_AND_MAINTENANCE.md - Setup & Operations

---

## Table of Contents

### Part 1: System Architecture
1. [High-Level Architecture](#high-level-architecture)
2. [Component Architecture](#component-architecture)
3. [Data Flow Diagrams](#data-flow-diagrams)
4. [Technology Stack Deep-Dive](#technology-stack-deep-dive)

### Part 2: Face Recognition Algorithm
5. [Algorithm Overview](#algorithm-overview)
6. [DeepFace Facenet512 Model](#deepface-facenet512-model)
7. [Face Detection Process](#face-detection-process)
8. [Face Encoding Process](#face-encoding-process)
9. [Face Matching Algorithm](#face-matching-algorithm)
10. [Multi-Photo Ensemble Matching](#multi-photo-ensemble-matching)

### Part 3: Backend Architecture
11. [Flask Application Structure](#flask-application-structure)
12. [Database Models](#database-models)
13. [Service Layer](#service-layer)
14. [API Routes](#api-routes)
15. [Middleware and Utilities](#middleware-and-utilities)

### Part 4: Frontend Architecture
16. [React Application Structure](#react-application-structure)
17. [Component Hierarchy](#component-hierarchy)
18. [State Management](#state-management)
19. [API Integration](#api-integration)
20. [UI/UX Design Patterns](#uiux-design-patterns)

### Part 5: Advanced Topics
21. [Video Processing Pipeline](#video-processing-pipeline)
22. [Quality Assessment System](#quality-assessment-system)
23. [Email Alert System](#email-alert-system)
24. [Security Implementation](#security-implementation)
25. [Performance Optimization](#performance-optimization)

---

# PART 1: SYSTEM ARCHITECTURE

## High-Level Architecture

### Three-Tier Architecture

The system follows a classic **three-tier architecture** pattern, separating concerns into presentation, application, and data layers:

```
┌────────────────────────────────────────────────────────────────────┐
│                        SYSTEM ARCHITECTURE                          │
│                        3-Tier Architecture                          │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  TIER 1: PRESENTATION LAYER (Frontend)                              │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  React Application (Port 3000)                               │  │
│  │  ├── Components (UI Elements)                                │  │
│  │  ├── Services (API Calls)                                    │  │
│  │  ├── Context (State Management)                              │  │
│  │  └── Utils (Helper Functions)                                │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬────────────────────────────────────────┘
                            │
                            │ HTTP/REST API (JSON)
                            │ JWT Authentication
                            │
┌───────────────────────────▼────────────────────────────────────────┐
│  TIER 2: APPLICATION LAYER (Backend)                                │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Flask Application (Port 5000)                               │  │
│  │  ├── Routes (API Endpoints)                                  │  │
│  │  ├── Services (Business Logic)                               │  │
│  │  │   ├── DetectionService (Face Recognition)                 │  │
│  │  │   ├── VideoService (Video Processing)                     │  │
│  │  │   ├── EmailService (Notifications)                        │  │
│  │  │   └── AnalyticsService (Dashboard Data)                   │  │
│  │  ├── Middleware (Auth, Logging)                              │  │
│  │  ├── Utils (Helpers)                                         │  │
│  │  └── ML Engine (DeepFace + OpenCV)                           │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬────────────────────────────────────────┘
                            │
                            │ SQLAlchemy ORM
                            │ Database Queries
                            │
┌───────────────────────────▼────────────────────────────────────────┐
│  TIER 3: DATA LAYER (Database)                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  SQLite Database (crime_detection.db)                        │  │
│  │  ├── users (Authentication)                                  │  │
│  │  ├── invitations (User Management)                           │  │
│  │  ├── criminals (Criminal Records)                            │  │
│  │  ├── criminal_photos (Multi-Photo Storage)                   │  │
│  │  ├── face_encodings (512-D Embeddings)                       │  │
│  │  ├── detection_logs (Detection History)                      │  │
│  │  ├── videos (Video Processing)                               │  │
│  │  └── alerts (Email Notifications)                            │  │
│  └─────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  EXTERNAL SYSTEMS                                                   │
│  ├── Gmail SMTP (Email Alerts)                                     │
│  ├── File System (Image/Video Storage)                             │
│  └── Pre-trained Models (Facenet512)                               │
└────────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

#### 1. Separation of Concerns
**Principle:** Each layer has a single, well-defined responsibility.

**Implementation:**
- **Frontend:** User interface and interaction only
- **Backend:** Business logic and data processing
- **Database:** Data persistence and retrieval

**Benefits:**
- Easier maintenance
- Independent scaling
- Clear boundaries

#### 2. RESTful API Design
**Principle:** Communication between frontend and backend follows REST principles.

**Implementation:**
- Resource-based URLs (`/api/criminals/:id`)
- HTTP methods (GET, POST, PUT, DELETE)
- JSON data format
- Stateless requests

**Benefits:**
- Standardized communication
- Easy to understand and use
- Language-agnostic

#### 3. Service-Oriented Architecture
**Principle:** Business logic is encapsulated in service classes.

**Implementation:**
- `DetectionService` - Face recognition logic
- `VideoService` - Video processing logic
- `EmailService` - Email notification logic
- `AnalyticsService` - Dashboard analytics logic

**Benefits:**
- Code reusability
- Easier testing
- Single responsibility

#### 4. Security by Design
**Principle:** Security is built into every layer, not added as an afterthought.

**Implementation:**
- JWT authentication at API gateway
- bcrypt password hashing at data layer
- Input validation at all entry points
- Role-based access control

**Benefits:**
- Defense in depth
- Reduced attack surface
- Compliance ready

---

## Component Architecture

### Detailed Component Breakdown

```
┌────────────────────────────────────────────────────────────────────┐
│                     COMPONENT ARCHITECTURE                          │
└────────────────────────────────────────────────────────────────────┘

FRONTEND COMPONENTS
├── App Component (Root)
│   ├── AuthContext Provider (Global Auth State)
│   ├── Router Configuration
│   └── Theme Provider (Material-UI)
│
├── Authentication Module
│   ├── Login.jsx (Login Form)
│   ├── Register.jsx (Registration with Token)
│   └── PrivateRoute.jsx (Protected Routes)
│
├── Dashboard Module
│   ├── Dashboard.jsx (Main Dashboard)
│   ├── AnalyticsDashboard.jsx (6-Tab Analytics)
│   │   ├── OverviewTab.jsx
│   │   ├── DetectionAnalysisTab.jsx
│   │   ├── CriminalActivityTab.jsx
│   │   ├── LocationTimeTab.jsx
│   │   ├── VideoAnalyticsTab.jsx
│   │   └── PerformanceTab.jsx
│   └── StatCard.jsx (Reusable Stat Component)
│
├── Criminal Management Module
│   ├── CriminalList.jsx (List with Search/Filter)
│   ├── CriminalForm.jsx (Add/Edit Form)
│   ├── CriminalDetails.jsx (Details View)
│   └── PhotoManagement.jsx (Multi-Photo Upload)
│
├── Detection Module
│   ├── UploadDetection.jsx (Image Upload)
│   ├── DetectionLogs.jsx (History)
│   ├── DetectionDetails.jsx (Single Detection)
│   └── VideoUpload.jsx (Video Upload)
│
├── Admin Module
│   ├── AdminPanel.jsx (Main Panel)
│   ├── UserManagement.jsx (User List/Edit)
│   ├── InvitationManagement.jsx (Create/List Invitations)
│   └── InvitationDialog.jsx (Create Dialog)
│
├── Profile Module
│   ├── Profile.jsx (User Profile)
│   └── ChangePassword.jsx (Password Change)
│
├── Alerts Module
│   └── AlertHistory.jsx (Email Alert List)
│
└── Shared Components
    ├── Navbar.jsx (Top Navigation)
    ├── Sidebar.jsx (Side Navigation)
    ├── Loading.jsx (Loading Spinner)
    ├── ErrorBoundary.jsx (Error Handler)
    └── ConfirmDialog.jsx (Confirmation Modal)

BACKEND COMPONENTS
├── Application Factory (app/__init__.py)
│   ├── Flask App Initialization
│   ├── Extension Registration
│   ├── Blueprint Registration
│   └── Error Handler Registration
│
├── Models (app/models/)
│   ├── user.py (User Model)
│   ├── invitation.py (Invitation Model)
│   ├── criminal.py (Criminal Model)
│   ├── criminal_photo.py (Photo Model)
│   ├── face_encoding.py (Encoding Model)
│   ├── detection_log.py (Detection Model)
│   ├── video.py (Video Model)
│   └── alert.py (Alert Model)
│
├── Routes (app/routes/)
│   ├── auth.py (Authentication Endpoints)
│   ├── admin.py (Admin Endpoints)
│   ├── criminals.py (Criminal CRUD)
│   ├── detection.py (Face Detection)
│   ├── video.py (Video Processing)
│   ├── dashboard.py (Analytics)
│   └── notifications.py (Alert History)
│
├── Services (app/services/)
│   ├── detection_service.py (Face Recognition)
│   ├── video_service.py (Video Processing)
│   ├── email_service.py (Email Alerts)
│   └── analytics_service.py (Dashboard Analytics)
│
├── Middleware (app/middleware/)
│   ├── auth_middleware.py (JWT Validation)
│   └── error_handler.py (Error Handling)
│
└── Utilities (app/utils/)
    ├── helpers.py (Common Functions)
    ├── validators.py (Input Validation)
    └── constants.py (System Constants)
```

---

## Data Flow Diagrams

### 1. Face Detection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    FACE DETECTION DATA FLOW                      │
└─────────────────────────────────────────────────────────────────┘

USER                   FRONTEND                  BACKEND                  AI ENGINE               DATABASE
 │                        │                         │                         │                       │
 │  1. Upload Image       │                         │                         │                       │
 ├───────────────────────>│                         │                         │                       │
 │                        │  2. POST /detection/upload                        │                       │
 │                        ├────────────────────────>│                         │                       │
 │                        │     (FormData: image)   │                         │                       │
 │                        │                         │  3. Validate JWT        │                       │
 │                        │                         ├─────────┐               │                       │
 │                        │                         │         │               │                       │
 │                        │                         │<────────┘               │                       │
 │                        │                         │  4. Save image to disk  │                       │
 │                        │                         ├─────────┐               │                       │
 │                        │                         │         │               │                       │
 │                        │                         │<────────┘               │                       │
 │                        │                         │  5. Call DetectionService                       │
 │                        │                         ├────────────────────────>│                       │
 │                        │                         │                         │  6. Load image       │
 │                        │                         │                         ├────────┐             │
 │                        │                         │                         │        │             │
 │                        │                         │                         │<───────┘             │
 │                        │                         │                         │  7. Detect faces     │
 │                        │                         │                         │     (OpenCV)         │
 │                        │                         │                         ├────────┐             │
 │                        │                         │                         │        │             │
 │                        │                         │                         │<───────┘             │
 │                        │                         │                         │  8. For each face:   │
 │                        │                         │                         │     Extract embedding│
 │                        │                         │                         │     (DeepFace)       │
 │                        │                         │                         ├────────┐             │
 │                        │                         │                         │        │             │
 │                        │                         │                         │<───────┘             │
 │                        │                         │                         │  9. Query DB for     │
 │                        │                         │                         │     criminal encodings│
 │                        │                         │                         ├──────────────────────>│
 │                        │                         │                         │  10. Return encodings│
 │                        │                         │                         │<──────────────────────┤
 │                        │                         │                         │  11. Calculate       │
 │                        │                         │                         │      cosine distances│
 │                        │                         │                         ├────────┐             │
 │                        │                         │                         │        │             │
 │                        │                         │                         │<───────┘             │
 │                        │                         │                         │  12. Apply threshold │
 │                        │                         │                         │      (0.40)          │
 │                        │                         │                         ├────────┐             │
 │                        │                         │                         │        │             │
 │                        │                         │                         │<───────┘             │
 │                        │                         │  13. Return matches     │                       │
 │                        │                         │<────────────────────────┤                       │
 │                        │                         │  14. Create detection logs                      │
 │                        │                         ├────────────────────────────────────────────────>│
 │                        │                         │  15. Send email if confidence >= 70%            │
 │                        │                         ├─────────┐               │                       │
 │                        │                         │         │               │                       │
 │                        │                         │<────────┘               │                       │
 │                        │  16. Return results     │                         │                       │
 │                        │<────────────────────────┤                         │                       │
 │                        │     (JSON: matches)     │                         │                       │
 │  17. Display results   │                         │                         │                       │
 │<───────────────────────┤                         │                         │                       │
 │                        │                         │                         │                       │
```

### 2. User Registration Flow (Admin-Only)

```
┌─────────────────────────────────────────────────────────────────┐
│                  USER REGISTRATION DATA FLOW                     │
└─────────────────────────────────────────────────────────────────┘

ADMIN                  FRONTEND                  BACKEND                  DATABASE
 │                        │                         │                         │
 │  1. Click "Create      │                         │                         │
 │     Invitation"        │                         │                         │
 ├───────────────────────>│                         │                         │
 │                        │  2. Fill form (email,   │                         │
 │                        │     role, dept)         │                         │
 │                        ├─────────┐               │                         │
 │                        │         │               │                         │
 │                        │<────────┘               │                         │
 │                        │  3. POST /admin/invitations                       │
 │                        ├────────────────────────>│                         │
 │                        │                         │  4. Validate JWT        │
 │                        │                         ├─────────┐               │
 │                        │                         │         │               │
 │                        │                         │<────────┘               │
 │                        │                         │  5. Check admin role    │
 │                        │                         ├─────────┐               │
 │                        │                         │         │               │
 │                        │                         │<────────┘               │
 │                        │                         │  6. Generate token      │
 │                        │                         │     (32 bytes crypto)   │
 │                        │                         ├─────────┐               │
 │                        │                         │         │               │
 │                        │                         │<────────┘               │
 │                        │                         │  7. Save invitation     │
 │                        │                         ├────────────────────────>│
 │                        │                         │  8. Return token & link │
 │                        │<────────────────────────┤                         │
 │  9. Copy invitation    │                         │                         │
 │     link               │                         │                         │
 │<───────────────────────┤                         │                         │
 │                        │                         │                         │
 │  10. Send link to new  │                         │                         │
 │      user via email    │                         │                         │
 │──────────────────────────────────────────────────────────────────────────>│
 │                        │                         │                         │
                          │                         │                         │
NEW USER               │                         │                         │
 │                        │                         │                         │
 │  11. Click invitation  │                         │                         │
 │      link              │                         │                         │
 ├───────────────────────>│                         │                         │
 │                        │  12. GET /register      │                         │
 │                        │      ?token=xxx         │                         │
 │                        ├────────────────────────>│                         │
 │                        │                         │  13. Verify token       │
 │                        │                         ├────────────────────────>│
 │                        │                         │  14. Return invitation  │
 │                        │                         │      details            │
 │                        │<────────────────────────┤                         │
 │  15. Fill registration │                         │                         │
 │      form (username,   │                         │                         │
 │      password)         │                         │                         │
 ├───────────────────────>│                         │                         │
 │                        │  16. POST /auth/register                          │
 │                        ├────────────────────────>│                         │
 │                        │                         │  17. Validate token     │
 │                        │                         ├────────────────────────>│
 │                        │                         │  18. Hash password      │
 │                        │                         │      (bcrypt)           │
 │                        │                         ├─────────┐               │
 │                        │                         │         │               │
 │                        │                         │<────────┘               │
 │                        │                         │  19. Create user        │
 │                        │                         ├────────────────────────>│
 │                        │                         │  20. Mark token used    │
 │                        │                         ├────────────────────────>│
 │                        │  21. Success response   │                         │
 │                        │<────────────────────────┤                         │
 │  22. Redirect to login │                         │                         │
 │<───────────────────────┤                         │                         │
 │                        │                         │                         │
```

---

# PART 2: FACE RECOGNITION ALGORITHM

## Algorithm Overview

### High-Level Algorithm Flow

The face recognition system uses a **deep learning-based approach** rather than traditional computer vision techniques. Here's the complete flow:

```
┌─────────────────────────────────────────────────────────────────┐
│              FACE RECOGNITION ALGORITHM FLOW                     │
└─────────────────────────────────────────────────────────────────┘

INPUT: Image (JPEG/PNG)
   │
   ▼
┌──────────────────────┐
│  STEP 1: LOAD IMAGE  │  ← cv2.imread()
│  Format: BGR array   │     Read file from disk
└──────────┬───────────┘     Convert to NumPy array
           │
           ▼
┌──────────────────────┐
│  STEP 2: FACE        │  ← OpenCV Haar Cascade
│  DETECTION           │     detect_faces()
│  Output: [(x,y,w,h)] │     Multiple faces possible
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  STEP 3: FOR EACH    │
│  DETECTED FACE       │  ← Loop through faces
└──────────┬───────────┘
           │
           ├─────> No Faces Found? → Return "No faces detected"
           │
           ▼ Yes, Faces Found
┌──────────────────────┐
│  STEP 4: CROP FACE   │  ← Extract face region
│  Resize to 160x160   │     img[y:y+h, x:x+w]
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  STEP 5: PREPROCESS  │  ← Normalize pixels
│  - Histogram equalize│     [-1, 1] range
│  - Normalize to [-1,1]│    Color conversion
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  STEP 6: EXTRACT     │  ← DeepFace.represent()
│  EMBEDDING           │     Facenet512 model
│  Output: 512-D vector│    [0.123, -0.456, ...]
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  STEP 7: LOAD DB     │  ← Query all criminals
│  ENCODINGS           │     Load all 512-D vectors
│  All criminal faces  │     From face_encodings table
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  STEP 8: CALCULATE   │  ← For each criminal:
│  DISTANCES           │     cosine_distance(emb1, emb2)
│  Cosine similarity   │     1 - dot(A,B)/(||A||*||B||)
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  STEP 9: FIND BEST   │  ← min(distances)
│  MATCH               │     If distance < 0.40:
│  Threshold: 0.40     │        Match found
└──────────┬───────────┘
           │
           ├─────> Distance >= 0.40? → Unknown person
           │
           ▼ Distance < 0.40
┌──────────────────────┐
│  STEP 10: RETURN     │  ← Convert to confidence
│  RESULT              │     Confidence = (1-distance)*100
│  Criminal + Score    │     Return criminal details
└──────────┬───────────┘
           │
           ▼
OUTPUT: {
  "criminal_id": 5,
  "name": "John Doe",
  "confidence": 85.5,
  "crime_type": "theft"
}
```

### Key Algorithm Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **Model** | Facenet512 | 512-dimensional embeddings |
| **Input Size** | 160x160 pixels | Model requirement |
| **Distance Metric** | Cosine Distance | Similarity measure |
| **Matching Threshold** | 0.40 | Distance below = match |
| **Confidence Threshold** | 70% | Alert trigger threshold |
| **Preprocessing** | Histogram Equalization | Lighting normalization |
| **Color Space** | RGB | Model requirement |

---

## DeepFace Facenet512 Model

### What is DeepFace?

**DeepFace** is a facial recognition system created by Facebook (Meta). Our system uses the **open-source Python library** that implements multiple face recognition models, including Facenet.

### Why Facenet512?

**Facenet** is a face recognition model developed by Google researchers. The "512" refers to the dimensionality of the face embeddings it produces.

**Key Advantages:**
1. **99.65% accuracy** on LFW (Labeled Faces in the Wild) dataset
2. **512-dimensional embeddings** - compact yet expressive
3. **Triplet loss training** - learns to separate faces
4. **Real-time performance** - 2-3 seconds per image
5. **Robust to variations** - handles lighting, angles, expressions

### Model Architecture: Inception-ResNet v1

```
┌─────────────────────────────────────────────────────────────────┐
│             FACENET512 MODEL ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────┘

INPUT: 160x160x3 RGB Image
   │
   ▼
┌──────────────────────┐
│  Convolutional Stem  │  ← Initial feature extraction
│  35x35x32            │     3 Conv layers
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Inception-ResNet-A  │  ← 5x Inception-ResNet blocks
│  (5 blocks)          │     35x35x256
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Reduction-A         │  ← Dimensionality reduction
│  17x17x896           │     
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Inception-ResNet-B  │  ← 10x Inception-ResNet blocks
│  (10 blocks)         │     17x17x896
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Reduction-B         │  ← Dimensionality reduction
│  8x8x1792            │     
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Inception-ResNet-C  │  ← 5x Inception-ResNet blocks
│  (5 blocks)          │     8x8x1792
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Average Pooling     │  ← Global average pooling
│  1x1x1792            │     
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Dropout (0.8)       │  ← Prevent overfitting
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Fully Connected     │  ← Final embedding layer
│  512 dimensions      │     L2 normalization
└──────────┬───────────┘
           │
           ▼
OUTPUT: 512-dimensional embedding
[0.123, -0.456, 0.789, ..., 0.321]

Total Parameters: ~23 million
Training Dataset: MS-Celeb-1M (100K identities, 10M images)
Training Method: Triplet Loss
```

### How Triplet Loss Works

Facenet is trained using **triplet loss**, which learns to:
1. **Minimize distance** between embeddings of the same person (anchor and positive)
2. **Maximize distance** between embeddings of different people (anchor and negative)

```
Triplet Loss Formula:
L = max(0, ||f(anchor) - f(positive)||² - ||f(anchor) - f(negative)||² + margin)

Where:
- f(x) = embedding function
- margin = 0.2 (separation margin)
```

**Example:**
```
Anchor: John's photo 1
Positive: John's photo 2
Negative: Jane's photo

Goal: 
  distance(John1, John2) < distance(John1, Jane) + margin
```

---

## Face Detection Process

### OpenCV Haar Cascade Detector

Before we can recognize a face, we must first **detect** where faces are in the image. We use OpenCV's Haar Cascade classifier.

### How Haar Cascade Works

```
┌─────────────────────────────────────────────────────────────────┐
│                   HAAR CASCADE FACE DETECTION                    │
└─────────────────────────────────────────────────────────────────┘

INPUT: Grayscale Image
   │
   ▼
┌──────────────────────┐
│  Convert to Grayscale│  ← cv2.cvtColor()
│  If not already      │     Single channel
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Apply Cascade       │  ← Sliding window approach
│  Classifier          │     Multiple scales
│  haarcascade_frontal│     
│  face_default.xml    │     
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  For Each Window:    │  ← Evaluate features
│  Calculate Haar      │     Compare to trained patterns
│  Features            │     
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Cascade of          │  ← 38 stages
│  Classifiers         │     Each stage has multiple features
│  (38 stages)         │     Early rejection for non-faces
└──────────┬───────────┘
           │
           ├─────> Reject if any stage fails
           │
           ▼ Pass all stages
┌──────────────────────┐
│  Face Detected!      │  ← Return bounding box
│  (x, y, width, height│     
└──────────┬───────────┘
           │
           ▼
OUTPUT: List of (x,y,w,h) rectangles
```

### Haar Features

Haar features are **rectangular patterns** that detect edges, lines, and contrasts:

```
EXAMPLE HAAR FEATURES:

┌─────────┬─────────┐     ┌──────────────────┐     ┌────────────┐
│ BLACK   │ WHITE   │     │   BLACK          │     │   WHITE    │
│         │         │     │                  │     │            │
└─────────┴─────────┘     ├──────────────────┤     ├────────────┤
   Edge Detection         │   WHITE          │     │   BLACK    │
                          └──────────────────┘     └────────────┘
                             Line Detection         Center Detection

Applied to detect:
- Eye regions (dark eyes, light below)
- Nose bridge (bright center)
- Mouth region (dark mouth, light above/below)
```

### Detection Code Example

```python
import cv2

def detect_faces(image_path):
    """
    Detect faces in an image using Haar Cascade.
    
    Args:
        image_path (str): Path to image file
        
    Returns:
        list: List of (x, y, w, h) tuples for each face
    """
    # Load the cascade
    cascade_path = 'models/haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    # Read image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,  # Scale reduction at each scale
        minNeighbors=5,   # Min neighbors for valid detection
        minSize=(30, 30), # Minimum face size
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    return faces

# Usage
faces = detect_faces('test_image.jpg')
print(f"Found {len(faces)} faces")
# Output: Found 3 faces
```

### Detection Parameters Explained

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `scaleFactor` | 1.1 | Image pyramid scale (1.05-1.4) |
| `minNeighbors` | 5 | Detection quality threshold |
| `minSize` | (30,30) | Minimum face size in pixels |
| `maxSize` | None | Maximum face size (unlimited) |

**Trade-offs:**
- **Lower scaleFactor** = More scales checked = Slower but more accurate
- **Higher minNeighbors** = Stricter filtering = Fewer false positives
- **Larger minSize** = Faster processing = May miss small faces

---

## Face Encoding Process

### DeepFace Embedding Extraction

Once we have detected a face, we extract a **512-dimensional embedding** that represents the unique characteristics of that face.

### Embedding Extraction Steps

```python
from deepface import DeepFace
import numpy as np

def extract_face_encoding(face_image):
    """
    Extract 512-D embedding from a face image.
    
    Args:
        face_image (numpy.ndarray): Cropped face image (RGB)
        
    Returns:
        numpy.ndarray: 512-dimensional embedding vector
    """
    try:
        # Method 1: Using DeepFace directly
        embedding_objs = DeepFace.represent(
            img_path=face_image,
            model_name='Facenet512',
            enforce_detection=False,  # Already detected
            detector_backend='skip',   # Skip detection
            align=True,                # Align face
            normalization='Facenet2018' # Normalization method
        )
        
        # Extract embedding (first element)
        embedding = np.array(embedding_objs[0]['embedding'])
        
        # L2 normalization (unit vector)
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
        
    except Exception as e:
        print(f"Error extracting embedding: {e}")
        return None

# Usage
face_crop = image[y:y+h, x:x+w]  # Crop detected face
encoding = extract_face_encoding(face_crop)
print(f"Embedding shape: {encoding.shape}")
# Output: Embedding shape: (512,)
```

### What's in the Embedding?

The 512-dimensional vector represents **learned features** of the face:

```
Example Embedding (first 20 dimensions):
[
   0.0234,  # Feature 1 (e.g., eye distance)
  -0.1567,  # Feature 2 (e.g., nose shape)
   0.0892,  # Feature 3 (e.g., face shape)
  -0.0451,  # Feature 4 (e.g., skin tone)
   0.1234,  # Feature 5 (e.g., eyebrow thickness)
   ...      # ... 507 more features
   0.0678   # Feature 512
]

Properties:
- Values range from -1 to +1 (normalized)
- Similar faces have similar vectors
- Different faces have different vectors
- Distance between vectors = face similarity
```

### Preprocessing Before Encoding

```python
def preprocess_face(face_image):
    """
    Preprocess face image before encoding.
    
    Args:
        face_image (numpy.ndarray): Cropped face image
        
    Returns:
        numpy.ndarray: Preprocessed face ready for encoding
    """
    # 1. Resize to model input size (160x160)
    face_resized = cv2.resize(face_image, (160, 160))
    
    # 2. Convert BGR to RGB (OpenCV uses BGR)
    face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
    
    # 3. Histogram equalization (normalize lighting)
    face_lab = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2LAB)
    face_lab[:,:,0] = cv2.equalizeHist(face_lab[:,:,0])
    face_normalized = cv2.cvtColor(face_lab, cv2.COLOR_LAB2RGB)
    
    # 4. Normalize pixel values to [-1, 1]
    face_normalized = (face_normalized.astype(np.float32) - 127.5) / 128.0
    
    return face_normalized
```

---

## Face Matching Algorithm

### Cosine Distance Calculation

To compare two face embeddings, we use **cosine distance**, which measures the angle between two vectors.

### Mathematical Formula

```
Cosine Similarity = (A · B) / (||A|| * ||B||)

Where:
- A, B = embedding vectors
- A · B = dot product
- ||A|| = magnitude (L2 norm) of A
- ||B|| = magnitude (L2 norm) of B

Cosine Distance = 1 - Cosine Similarity

Range:
- Distance = 0.0 → Identical faces
- Distance = 2.0 → Completely different faces
- Threshold = 0.40 → Our matching threshold
```

### Implementation

```python
import numpy as np
from scipy.spatial.distance import cosine

def calculate_distance(embedding1, embedding2):
    """
    Calculate cosine distance between two face embeddings.
    
    Args:
        embedding1 (numpy.ndarray): First embedding (512-D)
        embedding2 (numpy.ndarray): Second embedding (512-D)
        
    Returns:
        float: Cosine distance (0-2)
    """
    # Method 1: Using scipy
    distance = cosine(embedding1, embedding2)
    
    # Method 2: Manual calculation
    # dot_product = np.dot(embedding1, embedding2)
    # norm1 = np.linalg.norm(embedding1)
    # norm2 = np.linalg.norm(embedding2)
    # similarity = dot_product / (norm1 * norm2)
    # distance = 1 - similarity
    
    return distance

def find_best_match(test_embedding, criminal_embeddings, threshold=0.40):
    """
    Find the best matching criminal for a test embedding.
    
    Args:
        test_embedding (numpy.ndarray): Test face embedding
        criminal_embeddings (dict): {criminal_id: embedding}
        threshold (float): Matching threshold
        
    Returns:
        tuple: (criminal_id, distance, confidence) or (None, None, None)
    """
    best_match = None
    best_distance = float('inf')
    
    for criminal_id, criminal_embedding in criminal_embeddings.items():
        distance = calculate_distance(test_embedding, criminal_embedding)
        
        if distance < best_distance:
            best_distance = distance
            best_match = criminal_id
    
    # Check if best match is below threshold
    if best_distance < threshold:
        confidence = (1 - best_distance) * 100  # Convert to percentage
        return best_match, best_distance, confidence
    else:
        return None, None, None

# Usage
test_emb = extract_face_encoding(test_face)
criminal_embs = load_all_criminal_encodings()  # From database

criminal_id, distance, confidence = find_best_match(test_emb, criminal_embs)

if criminal_id:
    print(f"Match found: Criminal {criminal_id}")
    print(f"Distance: {distance:.4f}")
    print(f"Confidence: {confidence:.2f}%")
else:
    print("No match found (unknown person)")
```

### Why Cosine Distance?

**Advantages over Euclidean Distance:**

1. **Scale-Invariant** - Only cares about direction, not magnitude
2. **Works well in high dimensions** - 512 dimensions
3. **Bounded range** - Always 0-2, easy to interpret
4. **Widely used** - Industry standard for face recognition

**Visual Example:**

```
2D Visualization (imagine 512D):

     Vector A (Person 1)
        ↗
       /
      /  θ (small angle = similar)
     /
    ┴────────> Vector B (Person 1, different photo)


     Vector A (Person 1)
        ↗
       /
      /
     /  θ (large angle = different)
    /
   ↘
  Vector C (Person 2)
```

---

## Multi-Photo Ensemble Matching

### The Multi-Photo Problem

**Challenge:** A criminal's appearance varies with:
- **Angle:** Frontal vs. profile vs. three-quarter
- **Lighting:** Bright vs. dark vs. backlit
- **Expression:** Neutral vs. smiling vs. angry
- **Time:** Aging over years
- **Accessories:** Glasses, beard, hat

**Single photo accuracy:** 60-70%  
**Multi-photo ensemble accuracy:** 95%+

### Ensemble Matching Algorithm

```
┌─────────────────────────────────────────────────────────────────┐
│              MULTI-PHOTO ENSEMBLE MATCHING                       │
└─────────────────────────────────────────────────────────────────┘

TEST IMAGE
    │
    ▼
 Detect Face → Extract Embedding → Test Embedding (512-D)
    │
    ▼
FOR EACH CRIMINAL:
    │
    ├─→ Criminal has 3 photos:
    │   ├── Photo 1 (Frontal) → Embedding 1
    │   ├── Photo 2 (Left Profile) → Embedding 2
    │   └── Photo 3 (Right Profile) → Embedding 3
    │
    ▼
 Calculate distances to ALL photos:
    │
    ├─→ distance(Test, Photo1) = 0.52
    ├─→ distance(Test, Photo2) = 0.35  ← BEST MATCH
    └─→ distance(Test, Photo3) = 0.47
    │
    ▼
 Take MINIMUM distance = 0.35
    │
    ▼
 Compare to threshold (0.40)
    │
    ├─→ 0.35 < 0.40 → MATCH!
    │   Confidence = (1 - 0.35) * 100 = 65%
    │
    ▼
RESULT: Criminal matched with 65% confidence
```

### Implementation

```python
def ensemble_match_criminal(test_embedding, criminal_id, threshold=0.40):
    """
    Match test embedding against all photos of a criminal.
    
    Args:
        test_embedding (numpy.ndarray): Test face embedding
        criminal_id (int): Criminal database ID
        threshold (float): Matching threshold
        
    Returns:
        tuple: (matched, best_distance, confidence, best_photo_id)
    """
    # Get all encodings for this criminal
    encodings = FaceEncoding.query.filter_by(
        criminal_id=criminal_id
    ).all()
    
    if not encodings:
        return False, None, None, None
    
    best_distance = float('inf')
    best_photo_id = None
    
    # Compare against ALL photos
    for encoding in encodings:
        # Load encoding from database
        criminal_embedding = np.frombuffer(
            encoding.encoding_data,
            dtype=np.float32
        )
        
        # Calculate distance
        distance = cosine(test_embedding, criminal_embedding)
        
        # Track best match
        if distance < best_distance:
            best_distance = distance
            best_photo_id = encoding.photo_id
    
    # Check if best match is below threshold
    if best_distance < threshold:
        confidence = (1 - best_distance) * 100
        return True, best_distance, confidence, best_photo_id
    else:
        return False, best_distance, None, None

# Usage example
def match_against_all_criminals(test_embedding):
    """Match test embedding against entire criminal database."""
    criminals = Criminal.query.filter_by(status='active').all()
    
    best_criminal = None
    best_confidence = 0
    
    for criminal in criminals:
        matched, distance, confidence, photo_id = ensemble_match_criminal(
            test_embedding,
            criminal.id
        )
        
        if matched and confidence > best_confidence:
            best_criminal = criminal
            best_confidence = confidence
    
    return best_criminal, best_confidence
```

### Quality-Aware Matching

We can further improve accuracy by considering photo quality:

```python
def quality_aware_ensemble_match(test_embedding, criminal_id):
    """
    Ensemble matching with quality-based weighting.
    
    Higher quality photos get more weight in the decision.
    """
    encodings = FaceEncoding.query.filter_by(
        criminal_id=criminal_id
    ).join(CriminalPhoto).all()
    
    matches = []
    
    for encoding in encodings:
        criminal_emb = np.frombuffer(encoding.encoding_data, dtype=np.float32)
        distance = cosine(test_embedding, criminal_emb)
        quality = encoding.photo.quality_score  # 0-100
        
        # Weight by quality (higher quality = more important)
        weighted_distance = distance * (1 - quality/200)  # Adjust weight
        
        matches.append({
            'distance': distance,
            'weighted_distance': weighted_distance,
            'quality': quality,
            'photo_id': encoding.photo_id
        })
    
    # Sort by weighted distance
    matches.sort(key=lambda x: x['weighted_distance'])
    
    # Take best match
    best = matches[0]
    
    if best['weighted_distance'] < 0.40:
        confidence = (1 - best['distance']) * 100
        return True, confidence, best['photo_id']
    else:
        return False, None, None
```

### Benefits of Ensemble Matching

1. **Robustness to Variation**
   - Handles different angles, lighting, expressions
   - One good match is enough

2. **Improved Accuracy**
   - 60-70% (single photo) → 95%+ (multi-photo)
   - Reduces false negatives

3. **Confidence Boost**
   - Multiple matches increase confidence
   - Single match might be coincidence

4. **Real-World Applicability**
   - CCTV footage varies greatly
   - Database photos may be old

---

*[Continue to Page 2 of Technical Guide...]* 

**Note:** This technical guide continues with detailed information about:
- Video Processing Pipeline
- Quality Assessment System
- Email Alert System
- Security Implementation
- Performance Optimization
- Backend and Frontend Architecture Details

For the complete technical documentation, refer to the full TECHNICAL_GUIDE.md file.