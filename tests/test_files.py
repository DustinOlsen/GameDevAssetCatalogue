import pytest
import io


def test_download_file(client, auth_headers):
    """Test downloading an uploaded file"""
    file_content = b"test file content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    
    # Create asset with file
    create_response = client.post(
        "/api/assets",
        headers=auth_headers,
        data={
            "name": "File Asset",
            "category": "Script",
            "license_type": "MIT",
            "source_url": "https://example.com",
        },
        files=files
    )
    asset_id = create_response.json()["id"]
    
    # Download file
    response = client.get(f"/api/assets/{asset_id}/file", headers=auth_headers)
    assert response.status_code == 200
    assert response.content == file_content


def test_download_file_unauthorized(client, auth_headers, test_user):
    """Test that users cannot download other users' files"""
    file_content = b"private content"
    files = {"file": ("private.txt", io.BytesIO(file_content), "text/plain")}
    
    # Create asset as first user
    create_response = client.post(
        "/api/assets",
        headers=auth_headers,
        data={
            "name": "Private Asset",
            "category": "Script",
            "license_type": "MIT",
            "source_url": "https://example.com",
        },
        files=files
    )
    asset_id = create_response.json()["id"]
    
    # Register second user
    client.post("/api/auth/register", json={"username": "user2", "password": "pass2"})
    login2 = client.post("/api/auth/login", json={"username": "user2", "password": "pass2"})
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Try to download as second user
    response = client.get(f"/api/assets/{asset_id}/file", headers=headers2)
    assert response.status_code == 403


def test_download_nonexistent_file(client, auth_headers):
    """Test downloading file that doesn't exist"""
    response = client.get("/api/assets/99999/file", headers=auth_headers)
    assert response.status_code == 403  # Will fail authorization first


def test_file_preview(client, auth_headers):
    """Test file preview endpoint"""
    file_content = b"image data"
    files = {"file": ("image.png", io.BytesIO(file_content), "image/png")}
    
    # Create asset with image
    create_response = client.post(
        "/api/assets",
        headers=auth_headers,
        data={
            "name": "Image Asset",
            "category": "Texture",
            "license_type": "CC0",
            "source_url": "https://example.com",
        },
        files=files
    )
    asset_id = create_response.json()["id"]
    
    # Get preview
    response = client.get(f"/api/assets/{asset_id}/file-preview", headers=auth_headers)
    assert response.status_code == 200
    assert response.content == file_content