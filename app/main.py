from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from enum import Enum
app = FastAPI()


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




assets_db = [
Asset(id=1, name="Medieval Sword", category=AssetCategory.MODEL_3D, license_type="Paid", source_url="http://example.com/sword", description="A high-poly medieval sword model."),
Asset(id=2, name="Forest Texture Pack", category=AssetCategory.TEXTURE, license_type="Free", source_url="http://example.com/forest-textures", description="A collection of seamless forest textures."),


]

users = ["Alice", "Bob", "Charlie"]

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/users")
async def get_users():
    return {"users": users}


@app.get("/assets")
async def get_assets():
    return {"assets": assets_db}   


@app.post("/assets")
async def create_asset(asset: Asset):
    new_id = max([a.id for a in assets_db], default=0) + 1
    asset.id = new_id
    assets_db.append(asset)
    return asset