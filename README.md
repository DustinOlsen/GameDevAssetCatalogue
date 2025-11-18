# Game Dev Asset Catalogue

A production-ready REST API for managing game development assets (textures, models, audio, etc.) with user authentication, file uploads, and asset organization.

## 🎯 Features

- **User Authentication** – JWT-based auth with secure password hashing (bcrypt)
- **Asset Management** – Create, read, update, delete assets with rich metadata
- **File Uploads** – Upload and manage asset files with preview support
- **Search & Filter** – Filter by category, tags, and search metadata
- **User Isolation** – Users only see their own assets
- **RESTful API** – Clean, documented endpoints with OpenAPI/Swagger

## 🛠 Tech Stack

- **Framework**: FastAPI (async, modern Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Auth**: JWT (python-jose) + bcrypt password hashing
- **Testing**: pytest + pytest-asyncio (22 tests, 100% passing)
- **Server**: Uvicorn (ASGI)

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 12+
- pip / virtualenv

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone <repo-url>
cd GameDevAssetCatalogue
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
DATABASE_URL=postgresql://user:password@localhost/asset_catalogue
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Setup Database

```bash
# Create database (if not exists)
createdb asset_catalogue

# Run migrations (future: with Alembic)
python -c "from app.main import Base, engine; Base.metadata.create_all(engine)"
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`

### 5. View API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Examples

### Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "artist",
    "password": "securepassword123"
  }'
```

**Response** (201):
```json
{
  "user_id": 1,
  "username": "artist"
}
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "artist",
    "password": "securepassword123"
  }'
```

**Response** (200):
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Create an Asset

```bash
curl -X POST http://localhost:8000/api/assets \
  -H "Authorization: Bearer <your-token>" \
  -F "name=Metal Texture" \
  -F "description=Rusty metal surface" \
  -F "category=Texture" \
  -F "tags=metal,rust,pbr" \
  -F "license_type=MIT" \
  -F "source_url=https://example.com" \
  -F "file=@metal_texture.png"
```

### Get User's Assets

```bash
curl -X GET http://localhost:8000/api/assets \
  -H "Authorization: Bearer <your-token>"
```

### Filter by Category

```bash
curl -X GET "http://localhost:8000/api/assets?category=Texture" \
  -H "Authorization: Bearer <your-token>"
```

### Download Asset File

```bash
curl -X GET http://localhost:8000/api/assets/1/download \
  -H "Authorization: Bearer <your-token>" \
  -o downloaded_asset.png
```

## 🧪 Testing

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

Run a specific test:

```bash
pytest tests/test_auth.py::test_login_success -v
```

**Test Coverage**: 22 tests covering authentication, asset CRUD, file uploads, filtering, and user isolation.

## 📁 Project Structure

```
GameDevAssetCatalogue/
├── app/
│   ├── main.py              # FastAPI app, routes, models
│   └── __init__.py
├── tests/
│   ├── conftest.py          # Pytest fixtures (DB, auth, client)
│   ├── test_auth.py         # Auth endpoints tests
│   ├── test_assets.py       # Asset CRUD tests
│   └── test_files.py        # File upload/download tests
├── requirements.txt         # Python dependencies
├── pytest.ini               # Pytest config
├── README.md                # This file
└── .env.example             # Environment template
```

## 🔐 Security

- **Password Hashing**: bcrypt with passlib
- **JWT Tokens**: Secure token generation and validation
- **User Isolation**: Each user only accesses their own assets
- **HTTPS Ready**: Deploy behind a reverse proxy (Nginx, Caddy) for production
- **CORS**: Configure as needed in `main.py`

## 🚢 Deployment

### Using Docker (recommended)

```bash
docker build -t asset-catalogue .
docker run -p 8000:8000 --env-file .env asset-catalogue
```

### Using Heroku / Cloud Run

Deploy with Gunicorn:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Environment Variables Required

- `DATABASE_URL` – PostgreSQL connection string
- `SECRET_KEY` – JWT secret (min 32 chars, use `openssl rand -hex 32`)
- `ALGORITHM` – JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` – Token TTL (default: 30)

## 🎨 Design Decisions

1. **FastAPI**: Modern async framework with automatic OpenAPI docs and strong validation via Pydantic.
2. **PostgreSQL + SQLAlchemy**: Reliable, scalable relational DB with ORM for type safety.
3. **JWT + bcrypt**: Industry-standard auth without session state; easy to scale horizontally.
4. **Async/await**: Built-in for I/O-bound operations (file uploads, DB queries).
5. **User Isolation**: Every query filters by authenticated user to prevent data leaks.
6. **Comprehensive Tests**: Full coverage of happy paths, error cases, and edge cases (22 tests).

## 🐛 Known Limitations / Future Work

- [ ] Migrations with Alembic for safe schema changes
- [ ] Rate limiting (slowapi) for API abuse prevention
- [ ] Caching (Redis) for frequently accessed assets
- [ ] Asset versioning and rollback
- [ ] Batch upload / folder support
- [ ] S3 / cloud storage integration (currently local disk)
- [ ] Admin panel for user/asset management
- [ ] Advanced search (full-text, faceted filters)
- [ ] Async file processing (thumbnails, format conversion)

## 📝 License

MIT License – See LICENSE file for details.

## 👤 Author

Built as a learning project to demonstrate backend development best practices:
- Clean REST API design
- Secure authentication & authorization
- Comprehensive test coverage
- Production-ready code structure

## 📞 Support

For issues, questions, or suggestions, open a GitHub issue or contact the maintainer.

---

**Getting Started?** Start with the Quick Start section above, then check out the API Examples to understand the endpoints. Run tests with `pytest` to verify everything works.
