# Finance Copilot Backend

Production-oriented FastAPI backend scaffold for an AI-powered financial copilot with async PostgreSQL, pgvector, and Alembic migrations.

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.x (async)
- PostgreSQL + pgvector
- Alembic
- Docker + Docker Compose

## Project Structure

```text
app/
  api/
    routes/
  services/
  parsers/
  ai/
  models/
  db/
  core/
alembic/
  versions/
```

## Quick Start

1. Copy environment template:

```bash
cp .env.example .env
```

2. Run with Docker Compose:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## API Endpoints

- `GET /api/v1/health` - health status
- `POST /api/v1/documents/upload` - upload file and persist document metadata

## Database

- `document_metadata` table stores file metadata and optional embeddings.
- pgvector extension is enabled during migration.

Run migrations manually:

```bash
alembic upgrade head
```

## Local Development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Notes

- Logging is configured centrally in `app/core/logging.py`.
- Environment config uses `pydantic-settings` in `app/core/settings.py`.
- Architecture is modular with clear boundaries for API, services, parsers, AI, and persistence.
