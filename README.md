# Game Dev Asset Catalogue

A production-ready Asset Management System for game developers. It features a robust REST API backend and a clean, responsive frontend interface for managing textures, models, audio, and scripts.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)

## 🎯 Features

- **User Authentication** – JWT-based auth with secure password hashing (`pbkdf2_sha256`)
- **Asset Management** – Create, read, update, delete assets with rich metadata
- **File Uploads** – Upload and manage asset files with instant preview support
- **Visual Interface** – Clean, responsive dashboard to browse and manage assets
- **Search & Filter** – Filter by category, tags, and search metadata
- **User Isolation** – Users only see and manage their own assets
- **RESTful API** – Fully documented endpoints with OpenAPI/Swagger

## 🛠 Tech Stack

- **Backend**: FastAPI (Async Python)
- **Database**: PostgreSQL (via Docker) with SQLAlchemy ORM
- **Frontend**: Vanilla JavaScript, HTML5, CSS3 (served via Jinja2 templates)
- **Auth**: JWT (JSON Web Tokens) + Passlib (pbkdf2_sha256)
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest + pytest-asyncio

## 🚀 Quick Start (Recommended)

The easiest way to run the project is with Docker Compose.

### 1. Clone & Run

```bash
git clone <repo-url>
cd GameDevAssetCatalogue

# Build and start the services
docker-compose up --build
```

This will start the backend API, database, and frontend interface. Access the app at `http://localhost:8000`.

### 2. Configure Environment

Copy the example environment file and update the settings:

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials and a secure secret key:

```env
DATABASE_URL=postgresql://user:password@db/asset_catalogue
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Access the App

- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:8000

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

## 🧪 Test Mode

Try the app without creating an account:

**Login credentials:**
- Username: `test`
- Password: `test`

Test mode comes pre-populated with sample assets so you can immediately explore the full API. Tokens expire after 1 hour.

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'
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
│   ├── main.py              # FastAPI application & logic
│   └── __init__.py
├── static/                  # Frontend assets
│   ├── css/
│   └── js/
├── templates/               # HTML templates (Jinja2)
│   └── index.html
├── tests/                   # Test suite
├── uploaded_assets/         # Storage for user uploads
├── docker-compose.yml       # Container orchestration
├── Dockerfile               # API container definition
├── requirements.txt         # Python dependencies
└── README.md                # This file
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

**Dustin Olsen** (v01d / v01dworks)

Built as a portfolio project demonstrating production-ready backend architecture, secure authentication flows, and full-stack integration.

[![Ko-Fi](https://img.shields.io/badge/Support%20my%20work-Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/v01dworks)

## 📞 Support

For issues, questions, or suggestions, open a GitHub issue or contact the maintainer.

---

**Getting Started?** Start with the Quick Start section above, then check out the API Examples to understand the endpoints. Run tests with `pytest` to verify everything works.
