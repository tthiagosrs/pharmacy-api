import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_supabase():
    with patch("app.routers.auth.supabase") as mock:
        yield mock