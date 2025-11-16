from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from fastapi.params import Query
from fastapi.responses import FileResponse, HTMLResponse
import os
import shutil
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Directory to store uploaded asset files
UPLOAD_DIR = "uploaded_assets"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


class AssetCategory(str, Enum):
    MODEL_3D = "3D Model"
    SPRITE_2D = "2D Sprite"
    TEXTURE = "Texture"
    MUSIC = "Music"
    SFX = "Sound Effect"
    SCRIPT = "Script"
    OTHER = "Other"

class Asset(BaseModel):
    id: Optional[int] = None
    name: str
    category: AssetCategory
    license_type: str # e.g., "Free", "Paid", "Creative Commons"
    source_url: str
    description: Optional[str] = None
    tags: list[str] = [] 
    file_path: Optional[str] = None  # Add this to store file location




# Placeholder in-memory asset storage
# In a real application, this would be replaced with a database
assets_db = [
    Asset(id=1, name="Medieval Sword", category=AssetCategory.MODEL_3D, license_type="Paid", source_url="http://example.com/sword", description="A high-poly medieval sword model.", tags=["weapon", "medieval"]),
    Asset(id=2, name="Forest Texture Pack", category=AssetCategory.TEXTURE, license_type="Free", source_url="http://example.com/forest-textures", description="A collection of seamless forest textures.", tags=["forest", "nature", "seamless"]),
]


# Get specific Asset by ID
@app.get("/api/assets/{asset_id}")
async def get_asset(asset_id: int):
    for asset in assets_db:
        if asset.id == asset_id:
            return asset
    return {"error": "Asset not found"}


# Create a new Asset with optional file upload
@app.post("/api/assets")
async def create_asset(
    name: str = Form(...),
    category: AssetCategory = Form(...),
    license_type: str = Form(...),
    source_url: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    new_id = max([a.id for a in assets_db], default=0) + 1
    
    # Fix: Only split tags if they're not empty
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
    
    file_path = None
    # Check if file exists AND has a filename (not empty)
    if file is not None and file.filename:
        file_path = f"{UPLOAD_DIR}/{new_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    
    asset = Asset(
        id=new_id,
        name=name,
        category=category,
        license_type=license_type,
        source_url=source_url,
        description=description,
        tags=tag_list,
        file_path=file_path
    )
    assets_db.append(asset)
    return asset

# Get all Assets in the catalogue (with optional category and tag filters)
@app.get("/api/assets")
async def get_assets(category: Optional[AssetCategory] = Query(None), tags: Optional[str] = Query(None)):
    filtered_assets = assets_db
    
    if category is not None:
        filtered_assets = [asset for asset in filtered_assets if asset.category == category]
    
    if tags is not None:
        tag_list = [tag.strip() for tag in tags.split(",")]
        filtered_assets = [asset for asset in filtered_assets if any(tag in asset.tags for tag in tag_list)]
    
    return {"assets": filtered_assets}

# Download/view uploaded file
@app.get("/api/assets/{asset_id}/file")
async def get_asset_file(asset_id: int):
    for asset in assets_db:
        if asset.id == asset_id:
            if asset.file_path and os.path.exists(asset.file_path):
                return FileResponse(asset.file_path)
            return {"error": "File not found"}
    return {"error": "Asset not found"}

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Game Dev Asset Catalogue</title>
        <style>
            body { font-family: Arial; margin: 20px; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
            tr:hover { background-color: #f5f5f5; }
            a { color: #4CAF50; text-decoration: none; }
            button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer; font-size: 16px; }
            button:hover { background-color: #45a049; }
            form { display: none; background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; margin-bottom: 20px; }
            form.show { display: block; }
            input, select, textarea { width: 100%; padding: 8px; margin: 5px 0 15px 0; box-sizing: border-box; }
            label { display: block; font-weight: bold; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>Game Dev Asset Catalogue</h1>
        <button onclick="toggleForm()">+ Add New Asset</button>

        <form id="assetForm" class="show">
            <h2>Create New Asset</h2>
            <label>Name:</label>
            <input type="text" id="name" required>
            
            <label>Category:</label>
            <select id="category" required>
                <option value="3D Model">3D Model</option>
                <option value="2D Sprite">2D Sprite</option>
                <option value="Texture">Texture</option>
                <option value="Music">Music</option>
                <option value="Sound Effect">Sound Effect</option>
                <option value="Script">Script</option>
                <option value="Other">Other</option>
            </select>
            
            <label>License Type:</label>
            <input type="text" id="license_type" required>
            
            <label>Source URL:</label>
            <input type="url" id="source_url" required>
            
            <label>Description:</label>
            <textarea id="description" rows="3"></textarea>
            
            <label>Tags (comma-separated):</label>
            <input type="text" id="tags">
            
            <label>File (optional):</label>
            <input type="file" id="file">
            
            <button type="button" onclick="submitForm()">Create Asset</button>
            <button type="button" onclick="toggleForm()">Cancel</button>
        </form>

        <table id="assetsTable">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Category</th>
                    <th>License</th>
                    <th>Tags</th>
                    <th>Source</th>
                    <th>File</th>
                </tr>
            </thead>
            <tbody id="tableBody"></tbody>
        </table>

        <script>
            function toggleForm() {
                const form = document.getElementById('assetForm');
                form.classList.toggle('show');
            }

            async function loadAssets() {
                const response = await fetch('/api/assets');
                const data = await response.json();
                const tbody = document.getElementById('tableBody');
                tbody.innerHTML = '';
                
                data.assets.forEach(asset => {
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td>${asset.id}</td>
                        <td>${asset.name}</td>
                        <td>${asset.category}</td>
                        <td>${asset.license_type}</td>
                        <td>${asset.tags.join(', ')}</td>
                        <td><a href="${asset.source_url}" target="_blank">Link</a></td>
                        <td>${asset.file_path ? `<a href="/api/assets/${asset.id}/file">View</a>` : 'None'}</td>
                    `;
                });
            }

            async function submitForm() {
                const formData = new FormData();
                formData.append('name', document.getElementById('name').value);
                formData.append('category', document.getElementById('category').value);
                formData.append('license_type', document.getElementById('license_type').value);
                formData.append('source_url', document.getElementById('source_url').value);
                
                const description = document.getElementById('description').value;
                if (description) {
                    formData.append('description', description);
                }
                
                const tags = document.getElementById('tags').value;
                if (tags) {
                    formData.append('tags', tags);
                }
                
                const file = document.getElementById('file').files[0];
                if (file) {
                    formData.append('file', file);
                }

                const response = await fetch('/api/assets', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    document.getElementById('assetForm').reset();
                    toggleForm();
                    loadAssets();
                } else {
                    const error = await response.json();
                    alert('Error creating asset: ' + JSON.stringify(error));
                }
            }

            loadAssets();
        </script>
    </body>
    </html>
    """