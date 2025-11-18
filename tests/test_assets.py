import pytest
import io


def test_create_asset_success(client, auth_headers):
    """Test creating a new asset"""
    response = client.post(
        "/api/assets",
        headers=auth_headers,
        data={
            "name": "Test Asset",
            "description": "A test asset",
            "category": "Texture",  # Changed from "Textures" to match enum
            "tags": "test,demo",
            "license_type": "MIT",
            "source_url": "https://example.com",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Asset"
    # Tags are stored as comma-separated string
    assert data["tags"] == "test,demo"


def test_create_asset_with_file(client, auth_headers):
    """Test creating asset with file upload"""
    file_content = b"fake image content"
    files = {"file": ("test_image.png", io.BytesIO(file_content), "image/png")}
    
    response = client.post(
        "/api/assets",
        headers=auth_headers,
        data={
            "name": "Asset with File",
            "category": "Texture",
            "license_type": "CC0",
            "source_url": "https://example.com",
            "tags": "texture"
        },
        files=files
    )
    assert response.status_code == 200
    data = response.json()
    assert data["file_path"] is not None
    assert "test_image.png" in data["file_path"]


def test_get_assets_empty(client, auth_headers):
    """Test getting assets when none exist"""
    response = client.get("/api/assets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["assets"] == []


def test_get_assets_list(client, auth_headers):
    """Test listing assets"""
    # Create two assets
    for i in range(2):
        client.post(
            "/api/assets",
            headers=auth_headers,
            data={
                "name": f"Asset {i}",
                "category": "3D Model",
                "license_type": "MIT",
                "source_url": "https://example.com",
                "tags": f"tag{i}"
            }
        )
    
    response = client.get("/api/assets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["assets"]) == 2


def test_get_single_asset(client, auth_headers):
    """Test getting a specific asset by ID"""
    # Create asset
    create_response = client.post(
        "/api/assets",
        headers=auth_headers,
        data={
            "name": "Specific Asset",
            "category": "2D Sprite",
            "license_type": "GPL",
            "source_url": "https://example.com",
        }
    )
    asset_id = create_response.json()["id"]
    
    # Get asset
    response = client.get(f"/api/assets/{asset_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Specific Asset"
    assert data["id"] == asset_id


def test_get_nonexistent_asset(client, auth_headers):
    """Test getting asset that doesn't exist"""
    response = client.get("/api/assets/99999", headers=auth_headers)
    assert response.status_code == 404


def test_update_asset(client, auth_headers):
    """Test updating an existing asset"""
    # Create asset
    create_response = client.post(
        "/api/assets",
        headers=auth_headers,
        data={
            "name": "Original Name",
            "category": "Music",
            "license_type": "MIT",
            "source_url": "https://example.com",
        }
    )
    asset_id = create_response.json()["id"]
    
    # Update asset
    response = client.put(
        f"/api/assets/{asset_id}",
        headers=auth_headers,
        data={
            "name": "Updated Name",
            "category": "Sound Effect",
            "license_type": "CC0",
            "source_url": "https://newurl.com",
            "description": "Updated description"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["category"] == "Sound Effect"
    assert data["description"] == "Updated description"


def test_delete_asset(client, auth_headers):
    """Test deleting an asset"""
    # Create asset
    create_response = client.post(
        "/api/assets",
        headers=auth_headers,
        data={
            "name": "To Delete",
            "category": "Script",
            "license_type": "MIT",
            "source_url": "https://example.com",
        }
    )
    asset_id = create_response.json()["id"]
    
    # Delete asset
    response = client.delete(f"/api/assets/{asset_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f"/api/assets/{asset_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_filter_by_category(client, auth_headers):
    """Test filtering assets by category"""
    # Create assets with different categories
    categories = ["3D Model", "2D Sprite", "3D Model"]
    for cat in categories:
        client.post(
            "/api/assets",
            headers=auth_headers,
            data={
                "name": f"Asset {cat}",
                "category": cat,
                "license_type": "MIT",
                "source_url": "https://example.com",
            }
        )
    
    # Filter by 3D Model
    response = client.get("/api/assets?category=3D Model", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["assets"]) == 2
    assert all(a["category"] == "3D Model" for a in data["assets"])


def test_filter_by_tags(client, auth_headers):
    """Test filtering assets by tags"""
    # Create assets with different tags
    client.post(
        "/api/assets",
        headers=auth_headers,
        data={
            "name": "Asset 1",
            "category": "Texture",
            "license_type": "MIT",
            "source_url": "https://example.com",
            "tags": "fantasy,medieval"
        }
    )
    client.post(
        "/api/assets",
        headers=auth_headers,
        data={
            "name": "Asset 2",
            "category": "Texture",
            "license_type": "MIT",
            "source_url": "https://example.com",
            "tags": "scifi,futuristic"
        }
    )
    
    # Filter by fantasy tag
    response = client.get("/api/assets?tags=fantasy", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["assets"]) == 1
    assert "fantasy" in data["assets"][0]["tags"]


def test_user_isolation(client, test_user):
    """Test that users can only see their own assets"""
    # Login as first user
    login1 = client.post("/api/auth/login", json=test_user)
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    # Create asset as first user
    client.post(
        "/api/assets",
        headers=headers1,
        data={
            "name": "User 1 Asset",
            "category": "3D Model",
            "license_type": "MIT",
            "source_url": "https://example.com",
        }
    )
    
    # Register and login as second user
    client.post("/api/auth/register", json={"username": "user2", "password": "pass2"})
    login2 = client.post("/api/auth/login", json={"username": "user2", "password": "pass2"})
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Second user should not see first user's assets
    response = client.get("/api/assets", headers=headers2)
    assert response.status_code == 200
    assert len(response.json()["assets"]) == 0