# Crime Detection System - QA Test Suite

Complete test automation suite for the Crime Detection System with AI-powered face recognition.

## 📋 Table of Contents

- [Overview](#overview)
- [Test Coverage](#test-coverage)
- [Setup](#setup)
- [Running Tests](#running-tests)
- [Test Reports](#test-reports)
- [CI/CD Integration](#cicd-integration)
- [Contributing](#contributing)

## 🎯 Overview

This QA test suite provides comprehensive testing for the Crime Detection System:

- **Unit Tests**: 150+ tests for individual components
- **Integration Tests**: 50+ tests for API endpoints and workflows
- **E2E Tests**: 20+ tests for complete user journeys
- **Performance Tests**: Load testing with Locust
- **Security Tests**: SQL injection, XSS, authentication tests

### Test Statistics

- **Total Test Cases**: 233+ (includes 13 critical multi-photo matching tests)
- **Code Coverage Target**: 80%+
- **Estimated Test Execution Time**: 5-10 minutes
- **Supported Python Versions**: 3.10+

### ⭐ Critical Features Validated

- ✅ **Multi-Photo Face Matching**: 13 dedicated tests validate matching against criminals with multiple reference photos
  - See [MULTI_PHOTO_VALIDATION.md](MULTI_PHOTO_VALIDATION.md) for details
- ✅ **Face Recognition**: DeepFace/Facenet512 with 99.65% accuracy target
- ✅ **Security**: SQL injection, XSS, JWT authentication
- ✅ **Performance**: Load testing with realistic user scenarios

## 📊 Test Coverage

### By Module

| Module | Unit | Integration | E2E | Total |
|--------|------|-------------|-----|-------|
| Authentication | 25 | 5 | 3 | 33 |
| Criminal Management | 35 | 12 | 5 | 52 |
| **Face Detection** | **45** | **10** | **10** | **65** |
| **└─ Multi-Photo Matching** | **5** | **3** | **5** | **13** ⭐ |
| Alert System | 15 | 6 | 2 | 23 |
| Dashboard | 20 | 8 | 2 | 30 |
| Database | 15 | 15 | 0 | 30 |

### Test Categories

- ✅ **Functional Tests**: Core business logic
- ✅ **Security Tests**: Authentication, authorization, injection attacks
- ✅ **Performance Tests**: Load testing, benchmarks
- ✅ **Data Validation Tests**: Input validation, edge cases
- ✅ **Error Handling Tests**: Exception handling, error responses

## 🚀 Setup

### Prerequisites

- Python 3.10 or higher
- Virtual environment activated
- Backend dependencies installed

### Install Test Dependencies

```powershell
# Navigate to crime_detection directory
cd crime_detection

# Activate virtual environment (already done)
.\.venv\Scripts\Activate.ps1

# Install test requirements
pip install -r QA\requirements-test.txt
```

### Setup Test Environment

```powershell
# Create test directories
mkdir QA\reports\coverage -Force
mkdir tests\test_data\images -Force
mkdir tests\temp -Force

# Set environment variables for testing
$env:FLASK_ENV = "testing"
$env:DATABASE_URL = "sqlite:///:memory:"
```

## 🧪 Running Tests

### Run All Tests

```powershell
# Run complete test suite
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=backend/app --cov-report=html
```

### Run by Test Category

```powershell
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# E2E tests only
pytest -m e2e

# Security tests only
pytest -m security

# Performance tests (slow)
pytest -m slow
```

### Run by Module

```powershell
# Authentication tests
pytest QA\tests\unit\test_auth.py

# Criminal management tests
pytest QA\tests\unit\test_criminal.py

# Face detection tests
pytest QA\tests\unit\test_face_detection.py

# Integration tests
pytest QA\tests\integration\test_api_integration.py

# E2E workflow tests
pytest QA\tests\e2e\test_workflows.py
```

### Run Specific Tests

```powershell
# Run single test class
pytest QA\tests\unit\test_auth.py::TestUserLogin

# Run single test function
pytest QA\tests\unit\test_auth.py::TestUserLogin::test_login_valid_credentials

# Run tests matching pattern
pytest -k "login"
```

### Parallel Execution

```powershell
# Run tests in parallel (4 workers)
pytest -n 4

# Run tests in parallel (auto-detect cores)
pytest -n auto
```

## 📈 Performance Testing

### Load Testing with Locust

```powershell
# Start Locust web interface
locust -f QA\tests\performance\test_load.py --host=http://localhost:5000

# Then open http://localhost:8089 in browser

# Or run headless
locust -f QA\tests\performance\test_load.py \
  --host=http://localhost:5000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --headless
```

### Performance Benchmarks

```powershell
# Run benchmark tests
pytest --benchmark-only

# Compare benchmark results
pytest --benchmark-compare
```

## 📊 Test Reports

### Coverage Reports

```powershell
# Generate HTML coverage report
pytest --cov=backend/app --cov-report=html

# Open report
start QA\reports\coverage\html\index.html

# Generate terminal report
pytest --cov=backend/app --cov-report=term-missing

# Generate XML report (for CI/CD)
pytest --cov=backend/app --cov-report=xml
```

### Test Execution Reports

```powershell
# Generate HTML test report
pytest --html=QA\reports\test-report.html --self-contained-html

# Generate JSON report
pytest --json-report --json-report-file=QA\reports\test-report.json

# Open HTML report
start QA\reports\test-report.html
```

### Test Results Location

- **HTML Coverage**: `QA/reports/coverage/html/index.html`
- **XML Coverage**: `QA/reports/coverage/coverage.xml`
- **HTML Test Report**: `QA/reports/test-report.html`
- **JSON Test Report**: `QA/reports/test-report.json`

## 🔍 Code Quality

### Run Linters

```powershell
# Flake8
flake8 backend/app

# Pylint
pylint backend/app

# Black (code formatter)
black backend/app --check

# MyPy (type checking)
mypy backend/app
```

### Security Scanning

```powershell
# Bandit (security issues)
bandit -r backend/app

# Safety (dependency vulnerabilities)
safety check
```

## 🏗️ Test Structure

```
QA/
├── tests/
│   ├── conftest.py              # Pytest configuration and fixtures
│   ├── factories.py             # Test data factories
│   ├── unit/                    # Unit tests
│   │   ├── test_auth.py
│   │   ├── test_criminal.py
│   │   └── test_face_detection.py
│   ├── integration/             # Integration tests
│   │   └── test_api_integration.py
│   ├── e2e/                     # End-to-end tests
│   │   └── test_workflows.py
│   ├── performance/             # Performance tests
│   │   └── test_load.py
│   └── utils/                   # Test utilities
│       └── test_helpers.py
├── reports/                     # Test reports (generated)
│   ├── coverage/
│   ├── test-report.html
│   └── test-report.json
├── requirements-test.txt        # Test dependencies
├── TEST_PLAN.md                # Comprehensive test plan
└── BUG_REPORT.md               # Known bugs and issues
```

## 🔧 Configuration

### pytest.ini

Located in project root, configures pytest behavior:
- Test discovery paths
- Coverage settings
- Report formats
- Test markers

### Environment Variables

```powershell
# Testing environment
$env:FLASK_ENV = "testing"

# Database (use in-memory for tests)
$env:DATABASE_URL = "sqlite:///:memory:"

# Disable email in tests
$env:SMTP_EMAIL = ""

# Shorter JWT expiry for testing
$env:JWT_ACCESS_TOKEN_EXPIRES = "300"  # 5 minutes
```

## 🤖 CI/CD Integration

### GitHub Actions Example

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install -r QA/requirements-test.txt
    
    - name: Run tests
      run: |
        pytest --cov=backend/app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## 📝 Writing New Tests

### Test Template

```python
import pytest
from flask import json

@pytest.mark.unit  # or integration, e2e
class TestMyFeature:
    """Test description."""
    
    def test_something(self, client, db_session, admin_token):
        """Test case description."""
        # Arrange
        data = {'key': 'value'}
        
        # Act
        response = client.post(
            '/api/endpoint',
            headers={'Authorization': f'Bearer {admin_token}'},
            json=data
        )
        
        # Assert
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
```

### Using Factories

```python
from tests.factories import CriminalFactory, UserFactory

def test_with_factory(db_session):
    # Create test data
    criminal = CriminalFactory()
    users = UserFactory.create_batch(5)
    
    # Use in test
    assert criminal.name is not None
    assert len(users) == 5
```

## 🐛 Known Issues

See [BUG_REPORT.md](BUG_REPORT.md) for comprehensive list of:
- 3 Critical bugs (P0)
- 7 High priority bugs (P1)
- 9 Medium priority bugs (P2)
- 4 Low priority bugs (P3)

## 📈 Test Metrics Goals

| Metric | Target | Current |
|--------|--------|---------|
| Code Coverage | 80%+ | TBD |
| Test Pass Rate | 95%+ | TBD |
| API Response Time | < 1s | TBD |
| Face Detection Time | < 3s | TBD |
| False Positive Rate | < 5% | TBD |
| False Negative Rate | < 5% | TBD |

## 🤝 Contributing

When adding new features, please:

1. Write tests first (TDD approach)
2. Aim for 80%+ coverage
3. Include unit, integration, and E2E tests
4. Document test cases in code
5. Update TEST_PLAN.md if needed

## 📚 Additional Resources

- [TEST_PLAN.md](TEST_PLAN.md) - Comprehensive test strategy
- [BUG_REPORT.md](BUG_REPORT.md) - Known bugs and issues
- [Pytest Documentation](https://docs.pytest.org/)
- [Locust Documentation](https://docs.locust.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

## 📞 Support

For issues or questions about testing:
- Create an issue in the repository
- Contact QA team
- Review test documentation

---

**Last Updated**: December 24, 2025  
**QA Version**: 1.0  
**Maintained by**: AI QA Team
