from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from typing import Optional
from enum import Enum
from fastapi.params import Query
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import os
import shutil
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

load_dotenv()

app = FastAPI()
security = HTTPBearer()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploaded_assets")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Directory to store uploaded asset files
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

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# SQLAlchemy models
class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    assets = relationship("AssetDB", back_populates="owner")

class AssetDB(Base):
    __tablename__ = "assets_db"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    license_type = Column(String)
    source_url = Column(String)
    description = Column(Text, nullable=True)
    tags = Column(String)
    file_path = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("UserDB", back_populates="assets")

Base.metadata.create_all(bind=engine)

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    db = SessionLocal()
    user = db.query(UserDB).filter(UserDB.username == username).first()
    db.close()
    
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Auth endpoints
@app.post("/api/auth/register")
async def register(user: UserRegister):
    db = SessionLocal()
    existing_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing_user:
        db.close()
        raise HTTPException(status_code=400, detail="Username already taken")
    
    db_user = UserDB(
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.close()
    
    return {"message": "User created successfully"}

TEST_USERNAME = "test"
TEST_PASSWORD = "test"
TEST_USER_ID = 9999  # Use a reserved ID for test user

@app.post("/api/auth/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login endpoint with test mode support"""
    
    # Check for test mode
    if credentials.username == TEST_USERNAME and credentials.password == TEST_PASSWORD:
        # Generate token for test user
        access_token = create_access_token(
            data={"sub": TEST_USERNAME, "user_id": TEST_USER_ID},
            expires_delta=timedelta(hours=1)  # Short-lived test token
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "is_test_mode": True,  # Flag to frontend
            "message": "Welcome to test mode! Your demo resets every hour."
        }
    
    # Normal login flow
    user = db.query(UserDB).filter(UserDB.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "is_test_mode": False
    }

# Asset endpoints (updated for ownership)
@app.get("/api/assets/{asset_id}")
async def get_asset(asset_id: int, current_user: UserDB = Depends(get_current_user)):
    db = SessionLocal()
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    db.close()
    
    if asset:
        return {
            "id": asset.id,
            "name": asset.name,
            "category": asset.category,
            "license_type": asset.license_type,
            "source_url": asset.source_url,
            "description": asset.description,
            "tags": asset.tags.split(",") if asset.tags else [],
            "file_path": asset.file_path,
            "owner_id": asset.owner_id
        }
    raise HTTPException(status_code=404, detail="Asset not found")

@app.post("/api/assets")
async def create_asset(
    name: str = Form(...),
    category: AssetCategory = Form(...),
    license_type: str = Form(...),
    source_url: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: UserDB = Depends(get_current_user)
):
    db = SessionLocal()
    
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
    
    file_path = None
    if file is not None and file.filename:
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
        file_path=file_path,
        owner_id=current_user.id
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    db.close()
    
    return db_asset

@app.get("/api/assets")
def get_assets(
    category: Optional[str] = None,
    tags: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's assets with auto-seeding for test user"""
    
    user_id = current_user.get("user_id")
    is_test_mode = user_id == TEST_USER_ID
    
    # Auto-seed test data on first access
    if is_test_mode:
        existing_count = db.query(Asset).filter(Asset.user_id == TEST_USER_ID).count()
        if existing_count == 0:
            # Seed demo data automatically
            demo_assets = [
                Asset(
                    name="Rusty Metal Texture",
                    description="High-res rusty metal surface",
                    category="Texture",
                    tags="metal,rust,pbr",
                    license_type="CC0",
                    source_url="https://example.com",
                    user_id=TEST_USER_ID
                ),
                Asset(
                    name="Forest Ambience",
                    description="Looping forest background music",
                    category="Audio",
                    tags="music,ambient,forest",
                    license_type="MIT",
                    source_url="https://example.com",
                    user_id=TEST_USER_ID
                ),
            ]
            db.add_all(demo_assets)
            db.commit()
    
    query = db.query(Asset).filter(Asset.user_id == user_id)
    
    if category:
        query = query.filter(Asset.category == category)
    
    if tags:
        query = query.filter(Asset.tags.contains(tags))
    
    return query.all()

@app.get("/api/assets/{asset_id}/file")
async def get_asset_file(asset_id: int, current_user: UserDB = Depends(get_current_user)):
    db = SessionLocal()
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    db.close()
    
    if not asset or asset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if asset.file_path and os.path.exists(asset.file_path):
        # Extract original filename
        filename = os.path.basename(asset.file_path)
        # Remove the "ID_" prefix (e.g., "123_myfile.png" -> "myfile.png")
        if '_' in filename:
            filename = filename.split('_', 1)[1]
        
        return FileResponse(
            asset.file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/api/assets/{asset_id}/file-preview")
async def get_asset_file_preview(asset_id: int, current_user: UserDB = Depends(get_current_user)):
    db = SessionLocal()
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    db.close()
    
    if not asset or asset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if asset.file_path and os.path.exists(asset.file_path):
        return FileResponse(asset.file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.delete("/api/assets/{asset_id}")
async def delete_asset(asset_id: int, current_user: UserDB = Depends(get_current_user)):
    db = SessionLocal()
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    
    if not asset or asset.owner_id != current_user.id:
        db.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if asset.file_path and os.path.exists(asset.file_path):
        os.remove(asset.file_path)
    db.delete(asset)
    db.commit()
    db.close()
    
    return {"message": f"Asset {asset_id} deleted successfully"}

@app.put("/api/assets/{asset_id}")
async def update_asset(
    asset_id: int,
    name: str = Form(...),
    category: AssetCategory = Form(...),
    license_type: str = Form(...),
    source_url: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: UserDB = Depends(get_current_user)
):
    db = SessionLocal()
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    
    if not asset or asset.owner_id != current_user.id:
        db.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
    
    asset.name = name
    asset.category = category.value
    asset.license_type = license_type
    asset.source_url = source_url
    asset.description = description
    asset.tags = ",".join(tag_list)
    
    if file is not None and file.filename:
        if asset.file_path and os.path.exists(asset.file_path):
            os.remove(asset.file_path)
        
        file_path = f"{UPLOAD_DIR}/{asset_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        asset.file_path = file_path
    
    db.commit()
    db.refresh(asset)
    db.close()
    
    return asset

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    html_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
    with open(html_path, "r") as f:
        return f.read()

@app.get("/api/users/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return {
        "user_id": current_user.get("user_id"),
        "username": current_user.get("sub"),
        "is_test_mode": current_user.get("user_id") == TEST_USER_ID
    }

@app.post("/api/test/seed-demo-data")
def seed_demo_data(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Seed demo assets for test user (test mode only)"""
    
    # Only allow test user
    if current_user.get("user_id") != TEST_USER_ID:
        raise HTTPException(status_code=403, detail="Test data seeding only available in test mode")
    
    demo_assets = [
        {
            "name": "Rusty Metal Texture",
            "description": "High-res rusty metal surface for game environments",
            "category": "Texture",
            "tags": "metal,rust,pbr,scifi",
            "license_type": "CC0",
            "source_url": "https://example.com",
            "user_id": TEST_USER_ID
        },
        {
            "name": "Forest Ambience",
            "description": "Looping forest background music and ambience",
            "category": "Audio",
            "tags": "music,ambient,nature,forest",
            "license_type": "MIT",
            "source_url": "https://example.com",
            "user_id": TEST_USER_ID
        },
        {
            "name": "Character Model Pack",
            "description": "Stylized character models with animations",
            "category": "Model",
            "tags": "character,3d,animated,rigged",
            "license_type": "Commercial",
            "source_url": "https://example.com",
            "user_id": TEST_USER_ID
        },
    ]
    
    for asset_data in demo_assets:
        existing = db.query(Asset).filter(
            Asset.name == asset_data["name"],
            Asset.user_id == TEST_USER_ID
        ).first()
        
        if not existing:
            new_asset = Asset(**asset_data)
            db.add(new_asset)
    
    db.commit()
    
    return {
        "message": "Demo data seeded successfully!",
        "assets_count": len(demo_assets)
    }