from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from fastapi.params import Query
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
    tags: list[str] = [] 



# Placeholder in-memory asset storage
# In a real application, this would be replaced with a database
assets_db = [
    Asset(id=1, name="Medieval Sword", category=AssetCategory.MODEL_3D, license_type="Paid", source_url="http://example.com/sword", description="A high-poly medieval sword model.", tags=["weapon", "medieval"]),
    Asset(id=2, name="Forest Texture Pack", category=AssetCategory.TEXTURE, license_type="Free", source_url="http://example.com/forest-textures", description="A collection of seamless forest textures.", tags=["forest", "nature", "seamless"]),
]


# Get specific Asset by ID
@app.get("/assets/{asset_id}")
async def get_asset(asset_id: int):
    for asset in assets_db:
        if asset.id == asset_id:
            return asset
    return {"error": "Asset not found"}


# Create a new Asset in the catalogue
@app.post("/assets")
async def create_asset(asset: Asset):
    new_id = max([a.id for a in assets_db], default=0) + 1
    asset.id = new_id
    assets_db.append(asset)
    return asset


# Get all Assets in the catalogue (with optional category filter)
@app.get("/assets")
async def get_assets(category: Optional[AssetCategory] = Query(None)):
    if category is None:
        return {"assets": assets_db}
    
    filtered_assets = [asset for asset in assets_db if asset.category == category]
    return {"assets": filtered_assets}