from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import os
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
import shutil

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Test mode constants
TEST_USERNAME = "test"
TEST_PASSWORD = "test"
TEST_USER_ID = 9999

# Pydantic models for request validation
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class AssetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    tags: Optional[str] = None
    license_type: Optional[str] = None
    source_url: Optional[str] = None

# Ensure Upload Directory Exists
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploaded_assets"))
UPLOAD_DIR.mkdir(exist_ok=True)

# Asset categories enum (Must match Frontend)
class AssetCategory(str, Enum):
    TEXTURE = "Texture"
    MODEL = "3D Model"
    AUDIO = "Audio"
    SCRIPT = "Script"
    ANIMATION = "Animation"
    OTHER = "Other"

# Initialize FastAPI app
app = FastAPI()

# --- ADD/REPLACE THIS SECTION ---
# Get the absolute path to the project root
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Mount static files with absolute path
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Configure templates with absolute path
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
# --------------------------------

# ADD CORS MIDDLEWARE HERE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# OAuth2 scheme 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()

# Database configuration
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Create database engine - remove SQLite-specific connect_args for PostgreSQL
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a session
db = SessionLocal()

# Base class for declarative models
Base = declarative_base()

# JWT secret key and algorithm
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# SQLAlchemy models
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    assets = relationship("AssetDB", back_populates="owner")

class AssetDB(Base):
    __tablename__ = "assets"  # Ensure this is "assets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)
    tags = Column(String)
    license_type = Column(String)
    source_url = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("UserDB", back_populates="assets")

Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    """Verify JWT token and return current user info"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        return {"sub": username, "user_id": user_id}
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# Auth endpoints
@app.post("/api/auth/register")
async def register(user: UserRegister):
    # DEMO MODE: Disable registration
    raise HTTPException(
        status_code=403, 
        detail="Registration is disabled for this demo. Please log in with username 'test' and password 'test'."
    )

@app.post("/api/auth/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # 1. Check for Test User Login
    if credentials.username == TEST_USERNAME and credentials.password == TEST_PASSWORD:

        db_test_user = db.query(UserDB).filter(UserDB.id == TEST_USER_ID).first()
        
        if not db_test_user:
            # Create the test user on the fly
            test_user = UserDB(
                id=TEST_USER_ID,
                username=TEST_USERNAME,
                hashed_password=pwd_context.hash(TEST_PASSWORD)
            )
            db.add(test_user)
            db.commit()
            print(f"Created Test User (ID: {TEST_USER_ID}) in database.")

        # Generate token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": TEST_USERNAME, "user_id": TEST_USER_ID},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "is_test_mode": True
        }

    # 2. Regular User Login
    user = db.query(UserDB).filter(UserDB.username == credentials.username).first()
    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "is_test_mode": False
    }

# Asset endpoints (updated for ownership)
@app.get("/api/assets/{asset_id}")
async def get_asset(asset_id: int, current_user: dict = Depends(get_current_user)):
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
            "created_at": asset.created_at.isoformat() if asset.created_at else None, # ADDED THIS FIELD
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
    current_user: dict = Depends(get_current_user)  # CHANGED
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
        owner_id=current_user["user_id"]  # CHANGED
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
    user_id = current_user.get("user_id")
    is_test_mode = user_id == TEST_USER_ID
    
    # 1. Handle Test User & Seeding
    if is_test_mode:
        # Ensure Test User exists
        db_test_user = db.query(UserDB).filter(UserDB.id == TEST_USER_ID).first()
        if not db_test_user:
            test_user = UserDB(
                id=TEST_USER_ID,
                username=TEST_USERNAME,
                hashed_password=pwd_context.hash(TEST_PASSWORD)
            )
            db.add(test_user)
            db.commit()

        # Seed assets if empty
        if db.query(AssetDB).filter(AssetDB.owner_id == TEST_USER_ID).count() == 0:
            demo_assets = [
                AssetDB(
                    name="Rusty Metal Texture",
                    description="High-res rusty metal surface",
                    category="Texture",
                    tags="metal,rust,pbr",
                    license_type="CC0",
                    source_url="https://example.com",
                    owner_id=TEST_USER_ID
                ),
                AssetDB(
                    name="Forest Ambience",
                    description="Looping forest background music",
                    category="Audio",
                    tags="music,ambient,forest",
                    license_type="MIT",
                    source_url="https://example.com",
                    owner_id=TEST_USER_ID
                ),
            ]
            db.add_all(demo_assets)
            db.commit()
    
    # Query Logic
    query = db.query(AssetDB).filter(AssetDB.owner_id == user_id)
    
    if category:
        query = query.filter(AssetDB.category == category)
    
    if tags:
        query = query.filter(AssetDB.tags.contains(tags))
    
    assets = query.all()

    return {
        "assets": [
            {
                "id": asset.id,
                "name": asset.name,
                "description": asset.description,
                "category": asset.category,
                "tags": asset.tags.split(",") if asset.tags else [],
                "license_type": asset.license_type,
                "source_url": asset.source_url,
                "file_path": asset.file_path,
                "created_at": asset.created_at.isoformat() if asset.created_at else None,
                "owner_id": asset.owner_id
            }
            for asset in assets
        ]
    }

@app.get("/api/assets/{asset_id}/file")
async def get_asset_file(asset_id: int, current_user: dict = Depends(get_current_user)):  # CHANGED
    db = SessionLocal()
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    db.close()
    
    if not asset or asset.owner_id != current_user["user_id"]:  # CHANGED
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if asset.file_path and os.path.exists(asset.file_path):
        filename = os.path.basename(asset.file_path)
        if '_' in filename:
            filename = filename.split('_', 1)[1]
        
        return FileResponse(
            asset.file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/api/assets/{asset_id}/file-preview")
async def get_asset_file_preview(asset_id: int, current_user: dict = Depends(get_current_user)):  # CHANGED
    db = SessionLocal()
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    db.close()
    
    if not asset or asset.owner_id != current_user["user_id"]:  # CHANGED
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if asset.file_path and os.path.exists(asset.file_path):
        return FileResponse(asset.file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.delete("/api/assets/{asset_id}")
async def delete_asset(asset_id: int, current_user: dict = Depends(get_current_user)):  # CHANGED
    db = SessionLocal()
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    
    if not asset or asset.owner_id != current_user["user_id"]:  # CHANGED
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
    current_user: dict = Depends(get_current_user)  # CHANGED
):
    db = SessionLocal()
    asset = db.query(AssetDB).filter(AssetDB.id == asset_id).first()
    
    if not asset or asset.owner_id != current_user["user_id"]:  # CHANGED
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
    
    # Use AssetDB objects directly
    demo_assets = [
        AssetDB(
            name="Rusty Metal Texture",
            description="High-res rusty metal surface for game environments",
            category="Texture",
            tags="metal,rust,pbr,scifi",
            license_type="CC0",
            source_url="https://example.com",
            owner_id=TEST_USER_ID
        ),
        AssetDB(
            name="Forest Ambience",
            description="Looping forest background music and ambience",
            category="Audio",
            tags="music,ambient,nature,forest",
            license_type="MIT",
            source_url="https://example.com",
            owner_id=TEST_USER_ID
        ),
        AssetDB(
            name="Character Model Pack",
            description="Stylized character models with animations",
            category="3D Model",
            tags="character,3d,animated,rigged",
            license_type="Commercial",
            source_url="https://example.com",
            owner_id=TEST_USER_ID
        ),
    ]
    
    for asset in demo_assets:
        existing = db.query(AssetDB).filter(
            AssetDB.name == asset.name,
            AssetDB.owner_id == TEST_USER_ID
        ).first()
        
        if not existing:
            db.add(asset)
    
    db.commit()
    
    return {
        "message": "Demo data seeded successfully!",
        "assets_count": len(demo_assets)
    }