# Game Dev Asset Catalogue

A modern, multi-user web application for cataloguing and managing game development assets. Built with FastAPI and PostgreSQL, it provides a clean interface for organizing 3D models, sprites, textures, audio files, scripts, and more.

## Features

- 🔐 **Multi-User Authentication** - Secure user registration and login with JWT tokens
- 📦 **Asset Management** - Full CRUD operations for your game assets
- 🏷️ **Smart Categorization** - Organize by type: 3D Models, 2D Sprites, Textures, Music, Sound Effects, Scripts, Tilemaps
- 🔖 **Flexible Tagging** - Add custom tags for powerful organization and search
- 📁 **File Storage** - Upload and download asset files with preserved filenames
- 🖼️ **Image Previews** - Automatic thumbnail generation for image assets
- 🔍 **Advanced Filtering** - Filter by category and tags in real-time
- 💾 **PostgreSQL Database** - Robust, scalable data persistence
- 🎨 **Modern UI** - Clean, responsive interface with separated HTML/CSS/JS
- 📡 **REST API** - Full programmatic access with automatic documentation
- 🐳 **Docker Ready** - One-command deployment with Docker Compose

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Database**: PostgreSQL 15 with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **Frontend**: Vanilla JavaScript, modern CSS
- **Server**: Uvicorn (ASGI)
- **Containerization**: Docker & Docker Compose

## Quick Start (Docker)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GameDevAssetCatalogue/GameDevAssetCatalogue
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set a secure `SECRET_KEY`:
   ```env
   SECRET_KEY=your-super-secret-key-here-change-this
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Web UI: `http://localhost:8000/`
   - API Docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

5. **Create your account**
   - Click "Register" to create your first user account
   - Login and start cataloguing your assets!

## Manual Installation (Local Development)

### Prerequisites
- Python 3.11+
- PostgreSQL 15+

### Setup

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

4. **Set up PostgreSQL**
   ```bash
   createdb assets_db
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```env
   DATABASE_URL=postgresql://username:password@localhost/assets_db
   UPLOAD_DIR=uploaded_assets
   SECRET_KEY=your-super-secret-key-change-in-production
   ```

6. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access the application**
   - Web UI: `http://localhost:8000/`
   - API Docs: `http://localhost:8000/docs`

## Usage

### Web Interface

**Getting Started**
1. Register a new account or login with existing credentials
2. Click "+ Add New Asset" to create your first entry
3. Upload files, add tags, and organize your assets

**Managing Assets**
- **Add**: Click "+ Add New Asset", fill the form, optionally upload a file
- **Edit**: Click "Edit" on any asset to modify its details
- **Delete**: Click "Delete" to remove an asset (confirms before deletion)
- **Download**: Click "Download" to get the original uploaded file
- **Filter**: Use category dropdown and tag search to find specific assets

**Image Assets**
- Image files (PNG, JPG, GIF, etc.) automatically show thumbnails
- Click thumbnail or download link to get the full file

### API Endpoints

#### Authentication
- `POST /api/auth/register` - Create new user account
- `POST /api/auth/login` - Login and receive JWT token

#### Assets (Requires Authentication)
- `GET /api/assets` - List all user's assets
  - Query params: `category`, `tags` (comma-separated)
- `GET /api/assets/{id}` - Get specific asset details
- `POST /api/assets` - Create new asset (multipart/form-data)
- `PUT /api/assets/{id}` - Update existing asset
- `DELETE /api/assets/{id}` - Delete asset and its file
- `GET /api/assets/{id}/file` - Download asset file
- `GET /api/assets/{id}/file-preview` - Preview asset file

**Example API Usage**
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'

# Get assets (use token from login)
curl http://localhost:8000/api/assets \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Asset Categories

- **3D Model** - FBX, OBJ, GLTF, Blender files
- **2D Sprite** - Character sprites, UI elements
- **Tilemap** - Tile sets for level design
- **Texture** - Materials, PBR textures, patterns
- **Music** - Background music, themes
- **Sound Effect** - SFX, UI sounds, ambient audio
- **Script** - C#, GDScript, Lua, shader code
- **Other** - Anything else!

## Project Structure

```
GameDevAssetCatalogue/
├── app/
│   └── main.py                 # FastAPI application & API routes
├── templates/
│   └── index.html              # Main HTML structure
├── static/
│   ├── css/
│   │   └── style.css           # Application styles
│   └── js/
│       └── app.js              # Frontend logic
├── uploaded_assets/            # User uploaded files (auto-created)
├── Dockerfile                  # Docker image configuration
├── docker-compose.yml          # Multi-container setup
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `UPLOAD_DIR` | Directory for uploaded files | `uploaded_assets` |
| `SECRET_KEY` | JWT token secret (keep secure!) | Required |

## Docker Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild after code changes
docker-compose up --build

# Stop services
docker-compose down

# Reset database (WARNING: deletes all data)
docker-compose down -v

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f gamedev_app
```

## Security Best Practices

1. **Change the SECRET_KEY** - Use a long, random string in production
2. **Use HTTPS** - Deploy behind a reverse proxy with SSL/TLS
3. **Strong Passwords** - Enforce password requirements for users
4. **Regular Backups** - Backup PostgreSQL database regularly
5. **Update Dependencies** - Keep packages up to date for security patches

## Development

### Adding New Asset Categories

1. Update `AssetCategory` enum in `app/main.py`:
   ```python
   class AssetCategory(str, Enum):
       NEW_TYPE = "New Type Name"
   ```

2. Add to both dropdown menus in `templates/index.html`:
   ```html
   <option value="New Type Name">New Type Name</option>
   ```

### Running Tests
```bash
# Install dev dependencies
pip install pytest pytest-asyncio httpx

# Run tests (coming soon)
pytest
```

## Troubleshooting

**Can't login after registering?**
- Check browser console for errors (F12)
- Verify token is being stored in localStorage
- Ensure SECRET_KEY is set in .env

**Assets not showing up?**
- Verify you're logged in as the correct user (users only see their own assets)
- Check Docker logs: `docker-compose logs -f`

**File uploads failing?**
- Ensure `uploaded_assets/` directory exists and is writable
- Check file size limits in your deployment environment

**Database connection errors?**
- Verify PostgreSQL is running: `docker-compose ps`
- Check DATABASE_URL in .env matches your database credentials

## Future Enhancements

- [ ] Asset versioning and revision history
- [ ] Bulk import/export functionality
- [ ] Asset sharing between users/teams
- [ ] Advanced search with full-text capabilities
- [ ] Asset collections/favorites
- [ ] API rate limiting
- [ ] User roles and permissions
- [ ] Asset usage tracking
- [ ] Integration with game engines (Unity, Godot, Unreal)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Author

**Dustin Olsen** (v01d / v01dworks)

## Support

If you find this project helpful, consider supporting my work:

[![Support me on Ko-fi](https://img.shields.io/badge/Support%20on%20Ko--fi-FF5E8A?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/v01dworks)

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [PostgreSQL](https://www.postgresql.org/) - Powerful open source database
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit
- [Docker](https://www.docker.com/) - Container platform

---

**Made with ❤️ for game developers**
