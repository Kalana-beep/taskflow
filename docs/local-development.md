# Local Development Guide

This guide walks you through running TaskFlow locally, both via Docker Compose and native developer environments.

---

## 1. Prerequisites

- **Python:** 3.11+
- **Node.js:** 18+ or 20+
- **Docker & Docker Compose:** Docker Engine 24+ / Compose v2.20+
- **Git**

---

## 2. Docker Compose Quickstart (Recommended)

To run the entire system (Database, Backend, Frontend) with a single command:

```bash
docker compose up -d --build
```

### Access Endpoints
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
- **Backend API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Probe:** [http://localhost:8000/health](http://localhost:8000/health)

### Stopping Services
```bash
docker compose down
```

To also remove database data:
```bash
docker compose down -v
```

---

## 3. Direct Native Development

### 3.1 Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on Linux/macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3.2 Frontend Setup

```bash
cd frontend

# Install packages
npm install

# Run development server
npm run dev
```

---

## 4. Running Quality Checks Locally

### Backend
```bash
# Code formatting and linting
ruff check backend
ruff format --check backend

# Automated tests with coverage
pytest backend/tests --cov=app --cov-report=term-missing
```

### Frontend
```bash
cd frontend

# ESLint
npm run lint

# TypeScript Typecheck
npm run typecheck

# Vitest Component Tests
npm test
```
