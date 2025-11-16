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
    with open("templates/index.html", "r") as f:
        return f.read()