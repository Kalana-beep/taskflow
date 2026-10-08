# TaskFlow Backend

A clean, production-ready RESTful API service for the TaskFlow task management platform, built using FastAPI, SQLAlchemy 2.x, Pydantic v2, and PostgreSQL.

## Features

- **Asynchronous Architecture:** High-performance async I/O powered by FastAPI and asyncpg/SQLAlchemy.
- **Strict Data Validation:** Pydantic v2 data models with forbidden extra fields preventing parameter injection.
- **Relational Integrity:** PostgreSQL 16 schema with UUID primary keys and indexing on status, priority, and creation dates.
- **Automatic Lifecycle Rules:** Automatically updates timestamps and manages `completed_at` when status transitions to/from `DONE`.
- **Database Migrations:** Version-controlled database schema management with Alembic.
- **Production Containerization:** Slim multi-stage Docker build running under a non-root user.

## Getting Started

### Local Virtual Environment

```bash
cd backend
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
pytest --cov=app --cov-report=xml --cov-report=term-missing
```

### Running Code Quality Checks

```bash
ruff check .
ruff format --check .
```

### Running Locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI Schema: `http://localhost:8000/openapi.json`
- Liveness Probe: `http://localhost:8000/health`
