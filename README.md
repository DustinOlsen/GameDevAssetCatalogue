# Game Dev Asset Catalogue

A FastAPI-based web application for cataloguing and managing game development assets. Store, organize, and retrieve 3D models, sprites, textures, audio files, scripts, and more.

## Features

- 📦 **Asset Management** - Create, read, update, and delete assets
- 🏷️ **Categorization** - Organize assets by category (3D Model, 2D Sprite, Texture, Music, Sound Effects, Scripts, Tilemaps, etc.)
- 🔖 **Tagging System** - Add custom tags to assets for flexible organization
- 📁 **File Upload** - Optional file storage for assets
- 🔍 **Filtering** - Filter assets by category and tags
- 💾 **Database** - PostgreSQL backend for persistent storage
- 🌐 **Web UI** - Simple, intuitive web interface for managing assets
- 📡 **REST API** - Full API for programmatic access

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Frontend**: HTML/CSS/JavaScript
- **Server**: Uvicorn
- **Containerization**: Docker & Docker Compose

## Quick Start (Docker)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GameDevAssetCatalogue/GameDevAssetCatalogue
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Web UI: `http://localhost:8000/`
   - API Docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

That's it! The database will automatically initialize.

## Manual Installation (Local Development)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GameDevAssetCatalogue/GameDevAssetCatalogue
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your PostgreSQL credentials:
   ```
   DATABASE_URL=postgresql://your_username:your_password@localhost/assets_db
   UPLOAD_DIR=uploaded_assets
   ```

5. **Create the PostgreSQL database**
   ```bash
   createdb assets_db
   ```

6. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access the application**
   - Web UI: `http://localhost:8000/`
   - API Docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## Usage

### Web UI
- **Add Asset**: Click "+ Add New Asset" and fill in the form
- **Filter**: Use the filter section to search by category or tags
- **View File**: Click "View" to download/view uploaded files
- **Delete**: Click "Delete" to remove an asset

### API Endpoints

**GET** `/api/assets`
- Get all assets (supports filtering)
- Query parameters:
  - `category`: Filter by category
  - `tags`: Filter by tags (comma-separated)

**GET** `/api/assets/{asset_id}`
- Get a specific asset by ID

**POST** `/api/assets`
- Create a new asset
- Supports multipart form data with optional file upload

**GET** `/api/assets/{asset_id}/file`
- Download/view an asset's uploaded file

**DELETE** `/api/assets/{asset_id}`
- Delete an asset

## Asset Categories

- 3D Model
- 2D Sprite
- Tilemap
- Texture
- Music
- Sound Effect
- Script
- Other

## Project Structure

```
GameDevAssetCatalogue/
├── app/
│   └── main.py              # FastAPI application
├── templates/
│   └── index.html           # Web UI
├── uploaded_assets/         # Uploaded files directory
├── Dockerfile               # Docker image configuration
├── docker-compose.yml       # Docker Compose setup
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore file
└── README.md                # This file
```

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `UPLOAD_DIR` - Directory for storing uploaded files (default: `uploaded_assets`)

See `.env.example` for reference.

## Development

To add a new asset category:

1. Add to the `AssetCategory` enum in `app/main.py`
2. Add to both dropdown menus in `templates/index.html`

## Docker Commands

```bash
# Start containers
docker-compose up

# Start in background
docker-compose up -d

# Stop containers
docker-compose down

# Remove volumes (reset database)
docker-compose down -v

# View logs
docker-compose logs -f
```

## Future Enhancements

- User authentication
- Advanced search functionality
- Asset preview thumbnails
- Bulk operations
- Asset versioning
- API rate limiting

## License

MIT

## Author

Dustin Olsen / v01d / v01dworks

## Support

If you find this project helpful, consider supporting my work:

[![Support me on Ko-fi](https://img.shields.io/badge/Support%20on%20Ko--fi-FF5E8A?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/v01dworks)
