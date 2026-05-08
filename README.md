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


## Financial Document Extraction Engine

`POST /api/v1/documents/upload-and-extract` now returns a strict, validated extraction payload under `extracted.structured_financial_extraction`.

Structured fields extracted:
- insurer
- policy type
- sum insured
- waiting periods
- exclusions
- mutual fund names
- folios
- portfolio value

Validation/retries:
- extraction output is validated against strict Pydantic schemas (`extra=forbid`)
- engine retries up to 3 times when model output fails schema validation
- if validation still fails, API returns a safe default schema with `validated=false` and an error message

### Frontend testing flow

1. Start backend:

```bash
docker compose up --build
```

2. Start frontend:

```bash
cd frontend
npm install
npm run dev
```

3. Open `http://localhost:3000/upload` and upload a PDF.

4. In parallel, verify backend extraction response from API directly:

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload-and-extract \
  -F "file=@/absolute/path/to/sample.pdf"
```

5. Confirm response includes:
- `extracted.raw_text`
- `extracted.structured_sections`
- `extracted.structured_financial_extraction.validated`
- `extracted.structured_financial_extraction.data.insurance`
- `extracted.structured_financial_extraction.data.mutual_funds`
