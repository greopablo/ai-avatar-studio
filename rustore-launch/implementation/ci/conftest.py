import pytest
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_app_data():
    return {
        "id": "app_test_123",
        "name": "Test Avatar App",
        "version": "1.0.0"
    }

@pytest.fixture
def mock_user_data():
    return {
        "id": "user_test_456",
        "phone": "+79001234567",
        "is_premium": False,
        "credits": 3
    }

@pytest.fixture
def mock_build_data():
    return {
        "version_code": 1,
        "version_name": "1.0.0",
        "status": "ready"
    }

@pytest.fixture
def api_client():
    return Mock()

@pytest.fixture
def mock_review_data():
    return {
        "rating": 4.5,
        "comment": "Great app!",
        "date": "2024-01-01"
    }
