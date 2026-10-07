# Tech Stack

## Core Framework

- **FastAPI** (0.95.0) — ASGI web framework for building REST APIs
- **Uvicorn** (0.20.0) — ASGI server
- **Python 3.11** — Language runtime

## Database

- **PostgreSQL** — Primary database (via `asyncpg`)
- **SQLAlchemy** (1.4.41) + **SQLModel** (0.0.8) — Async ORM
- **Alembic** (1.9.4) — Database migrations
- **fastapi-async-sqlalchemy** (0.3.12) — SQLAlchemy middleware integration

Connection string configured via `DB_CONFIG` env var in `_staging.env` / `_prod.env`.

## Key Libraries

| Library | Purpose |
|---|---|
| `fastapi-pagination` (0.12.1) | Paginated endpoint responses |
| `pydantic` (1.10.4) | Schema validation and serialization |
| `stringcase` (1.2.0) | Snake case table name generation |
| `httpx` (0.23.3) | Async HTTP client for external API calls |
| `reportlab` (4.0.4) | PDF generation (vouchers, reports) |
| `openpyxl` (3.1.2) | Excel file generation |
| `num2words` (0.5.12) | Number to words conversion for documents |
| `google-cloud-tasks` (2.16.4) | Google Cloud Task queue integration |
| `python-dotenv` (1.0.0) | Environment variable management |

## Authentication & Authorization

- **OAuth2 Bearer Token** — Token validation via external OAuth service
- **Permission Middleware** — `configs/permission.py` validates roles:
  - `RFPGL_USER` — Internal user access
  - `RFPGL_CLIENT` — External client system access
  - Self-signed token for Cloud Task callbacks

## Deployment

- **Docker** — Containerized via `Dockerfile` (Python 3.11-slim base)
- **Azure Pipelines** — CI/CD pipeline builds and pushes to Google Artifact Registry
  - Triggers on: `master`, `staging`, `dev` branches
  - Image naming: `sedayuone/rfpgl/{branch}/rfpgl-api`
- **Port** — Default 8701 (configured in Dockerfile CMD)

## Common Commands

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8701

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

### Docker

```bash
# Build image
docker build -t rfpgl-api .

# Run container
docker run -p 8701:8701 --env-file _staging.env rfpgl-api
```

### Testing

No test suite is currently configured. Manual testing via:
- FastAPI interactive docs: `http://localhost:8701/rfpgl/docs`
- ReDoc: `http://localhost:8701/rfpgl/redoc`
