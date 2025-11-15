from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
app = FastAPI()

class Asset(BaseModel):
    id: int
    name: str
    category: str # e.g., "3D Model", "Texture", "Audio"
    license_type: str # e.g., "Free", "Paid", "Creative Commons"
    source_url: str
    description: Optional[str] = None


assets_db = [
Asset(id=1, name="Medieval Sword", category="3D Model", license_type="Paid", source_url="http://example.com/sword", description="A high-poly medieval sword model."),
Asset(id=2, name="Forest Texture Pack", category="Texture", license_type="Free", source_url="http://example.com/forest-textures", description="A collection of seamless forest textures."),



]


assets = ["Asset1", "Asset2", "Asset3"]

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