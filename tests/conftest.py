import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import tempfile
import shutil
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app, Base, get_db

# Use in-memory SQLite for tests (no .env needed)
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test upload directory
TEST_UPLOAD_DIR = tempfile.mkdtemp()


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """Create a test client with a fresh database for each test"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db
    
    # Set test upload directory
    os.environ['UPLOAD_DIR'] = TEST_UPLOAD_DIR
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(client):
    """Create a test user and return credentials with token"""
    username = "testuser"
    password = "testpass123"
    
    # Register user
    response = client.post(
        "/api/auth/register",
        json={"username": username, "password": password}
    )
    
    # Login to get token
    login_response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password}
    )
    
    token = login_response.json()["access_token"]
    
    return {
        "username": username,
        "password": password,
        "token": token,  # Changed from "access_token" to "token"
        "id": response.json().get("user_id")
    }


@pytest.fixture(scope="function")
def auth_token(client, test_user):
    """Login and return authentication token"""
    response = client.post(
        "/api/auth/login",
        json={"username": test_user["username"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """Return authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(autouse=True)
def cleanup_uploads():
    """Clean up test uploads after each test"""
    yield
    # Remove all files in test upload directory
    for filename in os.listdir(TEST_UPLOAD_DIR):
        filepath = os.path.join(TEST_UPLOAD_DIR, filename)
        try:
            if os.path.isfile(filepath):
                os.unlink(filepath)
        except Exception as e:
            print(f"Error deleting {filepath}: {e}")