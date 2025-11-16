from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from fastapi.params import Query
from fastapi.responses import FileResponse, HTMLResponse
import os
import shutil
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Directory to store uploaded asset files
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploaded_assets")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


class AssetCategory(str, Enum):
    MODEL_3D = "3D Model"
    SPRITE_2D = "2D Sprite"
    TILEMAP = "Tilemap"
    TEXTURE = "Texture"
    MUSIC = "Music"
    SFX = "Sound Effect"
    SCRIPT = "Script"
    OTHER = "Other"

class Asset(BaseModel):
    id: Optional[int] = None
    name: str
    category: AssetCategory
    license_type: str
    source_url: str
    description: Optional[str] = None
    tags: list[str] = [] 
    file_path: Optional[str] = None




# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy model (database table)
class AssetDB(Base):
    __tablename__ = "assets_db"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    license_type = Column(String)
    source_url = Column(String)
    description = Column(Text, nullable=True)
    tags = Column(String)  # Store as comma-separated string
    file_path = Column(String, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)


# Get specific Asset by ID
@app.get("/api/assets/{asset_id}")
async def get_asset(asset_id: int):
    db = SessionLocal()
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    db.close()
    if asset:
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
    db = SessionLocal()
    
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
    
    file_path = None
    if file is not None and file.filename:
        # Get next ID
        last_asset = db.query(AssetDB).order_by(AssetDB.id.desc()).first()
        new_id = (last_asset.id + 1) if last_asset else 1
        
        file_path = f"{UPLOAD_DIR}/{new_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    
    db_asset = AssetDB(
        name=name,
        category=category.value,
        license_type=license_type,
        source_url=source_url,
        description=description,
        tags=",".join(tag_list),
        file_path=file_path
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    db.close()
    
    return db_asset

# Get all Assets in the catalogue (with optional category and tag filters)
@app.get("/api/assets")
async def get_assets(category: Optional[AssetCategory] = Query(None), tags: Optional[str] = Query(None)):
    db = SessionLocal()
    query = db.query(AssetDB)
    
    if category is not None:
        query = query.filter(AssetDB.category == category.value)
    
    if tags is not None:
        tag_list = [tag.strip() for tag in tags.split(",")]
        assets = query.all()
        filtered_assets = [a for a in assets if any(tag in a.tags.split(",") for tag in tag_list)]
    else:
        filtered_assets = query.all()
    
    db.close()
    
    # Convert tags back to arrays for frontend
    result = []
    for asset in filtered_assets:
        asset_dict = {
            "id": asset.id,
            "name": asset.name,
            "category": asset.category,
            "license_type": asset.license_type,
            "source_url": asset.source_url,
            "description": asset.description,
            "tags": asset.tags.split(",") if asset.tags else [],
            "file_path": asset.file_path
        }
        result.append(asset_dict)
    
    return {"assets": result}

# Download/view uploaded file
@app.get("/api/assets/{asset_id}/file")
async def get_asset_file(asset_id: int):
    db = SessionLocal()
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    db.close()
    
    if asset:
        if asset.file_path and os.path.exists(asset.file_path):
            return FileResponse(asset.file_path)
        return {"error": "File not found"}
    return {"error": "Asset not found"}



# Delete an Asset by ID
@app.delete("/api/assets/{asset_id}")
async def delete_asset(asset_id: int):
    db = SessionLocal()
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    
    if asset:
        if asset.file_path and os.path.exists(asset.file_path):
            os.remove(asset.file_path)
        db.delete(asset)
        db.commit()
        db.close()
        return {"message": f"Asset {asset_id} deleted successfully"}
    
    db.close()
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
            .filter-section { background-color: #f0f0f0; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
            .filter-section label { display: inline-block; margin-right: 15px; font-weight: bold; }
            .filter-section select, .filter-section input { padding: 8px; margin-right: 10px; }
            .filter-section button { background-color: #4CAF50; color: white; padding: 8px 15px; border: none; cursor: pointer; }
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

        <div class="filter-section">
            <label>Filter by Category:</label>
            <select id="filterCategory">
                <option value="">All Categories</option>
                <option value="3D Model">3D Model</option>
                <option value="2D Sprite">2D Sprite</option>
                <option value="Texture">Texture</option>
                <option value="Tilemap">Tilemap</option>
                <option value="Music">Music</option>
                <option value="Sound Effect">Sound Effect</option>
                <option value="Script">Script</option>
                <option value="Other">Other</option>
            </select>
            
            <label>Filter by Tags (comma-separated):</label>
            <input type="text" id="filterTags" placeholder="e.g., weapon, fantasy">
            
            <button onclick="applyFilters()">Apply Filters</button>
            <button onclick="clearFilters()">Clear Filters</button>
        </div>

        <form id="assetForm" class="show">
            <h2>Create New Asset</h2>
            <label>Name:</label>
            <input type="text" id="name" required>
            
            <label>Category:</label>
            <select id="category" required>
                <option value="3D Model">3D Model</option>
                <option value="2D Sprite">2D Sprite</option>
                <option value="Texture">Texture</option>
                <option value="Tilemap">Tilemap</option>
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
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="tableBody"></tbody>
        </table>

        <script>
            function toggleForm() {
                const form = document.getElementById('assetForm');
                form.classList.toggle('show');
            }

            async function loadAssets(category = '', tags = '') {
                let url = '/api/assets';
                const params = new URLSearchParams();
                
                if (category) {
                    params.append('category', category);
                }
                if (tags) {
                    params.append('tags', tags);
                }
                
                if (params.toString()) {
                    url += '?' + params.toString();
                }
                
                const response = await fetch(url);
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
                        <td><button onclick="deleteAsset(${asset.id})">Delete</button></td>
                    `;
                });
            }

            function applyFilters() {
                const category = document.getElementById('filterCategory').value;
                const tags = document.getElementById('filterTags').value;
                loadAssets(category, tags);
            }

            function clearFilters() {
                document.getElementById('filterCategory').value = '';
                document.getElementById('filterTags').value = '';
                loadAssets();
            }

            async function deleteAsset(asset_id) {
                if (confirm('Are you sure you want to delete this asset?')) {
                    const response = await fetch(`/api/assets/${asset_id}`, {
                        method: 'DELETE'
                    });

                    if (response.ok) {
                        applyFilters();
                    } else {
                        alert('Error deleting asset');
                    }
                }
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
                    clearFilters();
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