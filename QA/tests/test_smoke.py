"""
Smoke Tests - Quick verification that basic setup works
Run these tests first to verify test framework is working
"""

import pytest
import sys
import os


@pytest.mark.unit
def test_python_version():
    """Verify Python version is 3.10 or higher."""
    version = sys.version_info
    assert version.major == 3
    assert version.minor >= 10, f"Python 3.10+ required, found {version.major}.{version.minor}"


@pytest.mark.unit
def test_pytest_working():
    """Verify pytest is working."""
    assert True


@pytest.mark.unit
def test_imports():
    """Verify critical imports work."""
    try:
        import pytest
        import flask
        import numpy
        import PIL
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


@pytest.mark.unit
def test_backend_structure():
    """Verify backend directory structure exists."""
    backend_path = os.path.join(os.getcwd(), 'backend')
    assert os.path.exists(backend_path), "backend directory not found"
    
    app_path = os.path.join(backend_path, 'app')
    assert os.path.exists(app_path), "backend/app directory not found"


@pytest.mark.unit
def test_test_structure():
    """Verify QA test structure exists."""
    qa_path = os.path.join(os.getcwd(), 'QA')
    assert os.path.exists(qa_path), "QA directory not found"
    
    tests_path = os.path.join(qa_path, 'tests')
    assert os.path.exists(tests_path), "QA/tests directory not found"


@pytest.mark.unit
class TestBasicMath:
    """Basic sanity tests."""
    
    def test_addition(self):
        """Test addition works."""
        assert 1 + 1 == 2
    
    def test_subtraction(self):
        """Test subtraction works."""
        assert 5 - 3 == 2
    
    def test_multiplication(self):
        """Test multiplication works."""
        assert 3 * 4 == 12


@pytest.mark.unit
def test_fixtures_available(client):
    """Test that pytest fixtures are available."""
    assert client is not None


@pytest.mark.unit  
def test_database_fixture(db_session):
    """Test that database fixture is available."""
    assert db_session is not None


if __name__ == '__main__':
    # Allow running this file directly
    pytest.main([__file__, '-v'])
