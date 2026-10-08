# TaskFlow

> **Simple Task Management Application & Advanced DevOps CI/CD Pipeline**
> A full-stack task management platform built to showcase enterprise-grade continuous delivery automation: Python, FastAPI, PostgreSQL 16, SQLAlchemy 2.x, Alembic, Next.js, React, TypeScript, Docker, Docker Compose, Jenkins, Trivy, Gitleaks, and Docker Hub.

---

## 1. Project Overview

TaskFlow is designed to keep domain logic simple, intuitive, and robust, while applying industry-standard DevOps engineering and CI/CD automation around the full software development lifecycle.

### Key Capabilities
- **Simple & Intuitive Application:** Manage tasks through their lifecycle (`TODO` ➔ `IN_PROGRESS` ➔ `DONE`) with priority ratings (`LOW`, `MEDIUM`, `HIGH`).
- **Interactive SaaS Dashboard:** Real-time metrics tracking total, in-progress, completed, and high-priority workloads.
- **Enterprise Testing Pyramid:** Unit tests with SQLite in-memory, live PostgreSQL integration testing in ephemeral CI containers, and automated post-deployment smoke tests.
- **Automated Security Gates:** Secret scanning with Gitleaks, dependency vulnerability audits with pip-audit and npm audit, and container CVE analysis with Trivy.
- **Declarative CI/CD Pipeline:** Fully automated 17-stage Jenkins Declarative Pipeline featuring parallel quality gates, branch-aware deployment, and immutable image tagging via Git commit SHA.

---

## 2. Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | [Next.js 14](https://nextjs.org/) (App Router), [React 18](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS](https://tailwindcss.com/), [Lucide React](https://lucide.dev/) |
| **Backend** | [Python 3.11+](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org/), [Pydantic v2](https://docs.pydantic.dev/), [Alembic](https://alembic.sqlalchemy.org/) |
| **Database** | [PostgreSQL 16](https://www.postgresql.org/) with UUID primary keys, indexes, and connection pooling |
| **Containers** | [Docker](https://www.docker.com/) (Multi-stage builds, non-root users), [Docker Compose v2](https://docs.docker.com/compose/) |
| **CI / CD** | [Jenkins LTS](https://www.jenkins.io/) (Declarative Pipeline), [Docker Hub](https://hub.docker.com/) |
| **Code Quality** | [Ruff](https://astral.sh/ruff), [ESLint](https://eslint.org/), TypeScript Strict Mode |
| **Security Scanning** | [Gitleaks](https://github.com/gitleaks/gitleaks), [Trivy](https://github.com/aquasecurity/trivy), [pip-audit](https://github.com/pypa/pip-audit), `npm audit` |
| **Testing** | [Pytest](https://pytest.org/), `pytest-asyncio`, `pytest-cov`, [Vitest](https://vitest.dev/), React Testing Library |

---

## 3. Directory Structure

```
TaskFlow/
│
├── backend/                  # FastAPI backend service
│   ├── app/
│   │   ├── api/routes/       # Thin API route handlers (/health, /api/tasks)
│   │   ├── core/             # Configuration & environment settings
│   │   ├── db/               # Database engine, session, and metadata
│   │   ├── models/           # SQLAlchemy 2.x ORM models (Task)
│   │   ├── schemas/          # Pydantic v2 validation models
│   │   ├── services/         # Encapsulated task business logic
│   │   └── main.py           # FastAPI application entry point
│   ├── tests/                # Pytest unit & integration test suites
│   ├── alembic/              # Database migration versions
│   ├── Dockerfile            # Multi-stage production container
│   ├── requirements.txt      # Production runtime dependencies
│   ├── requirements-dev.txt  # Testing, linting, & security packages
│   └── pyproject.toml        # Ruff, Pytest, and Coverage configurations
│
├── frontend/                 # Next.js 14 modern React dashboard
│   ├── app/                  # App router pages and global styles
│   ├── components/           # Reusable UI components (Cards, Modals, Filters)
│   ├── lib/                  # Reusable typed API client
│   ├── types/                # TypeScript interface definitions
│   ├── tests/                # Vitest & React Testing Library suites
│   ├── Dockerfile            # Multi-stage production container
│   ├── package.json          # Node dependencies & test scripts
│   └── tsconfig.json         # Strict TypeScript compiler options
│
├── scripts/
│   └── smoke_test.py         # End-to-end post-deployment smoke test runner
│
├── ci/
│   └── jenkins/              # Local Jenkins master/agent container setup
│       ├── Dockerfile        # Jenkins LTS with Docker CLI, Compose, Trivy, Gitleaks
│       ├── docker-compose.yml# Jenkins orchestration and host socket mount
│       └── README.md         # Jenkins setup and credentials instructions
│
├── docs/                     # Technical specifications and guides
│   ├── architecture.md       # System design and component interactions
│   ├── local-development.md  # Local setup commands and workflows
│   ├── testing.md            # Testing pyramid and coverage standards
│   ├── pipeline.md           # CI/CD pipeline stage explanations
│   └── jenkins.md            # Jenkins execution and troubleshooting
│
├── docker-compose.yml        # Production / local multi-container stack
├── docker-compose.ci.yml     # Isolated ephemeral CI integration environment
├── Jenkinsfile               # Declarative CI/CD pipeline script
├── .env.example              # Environment variables template
├── .gitignore                # Exclusion rules for secrets, venvs, artifacts
└── README.md                 # Primary project documentation
```

---

## 4. Quickstart Guide

### 4.1 Running with Docker Compose

Start the full stack with a single command:

```bash
docker compose up -d --build
```

#### Application Endpoints
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
- **Backend Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Probe:** [http://localhost:8000/health](http://localhost:8000/health)

#### Stopping Services
```bash
docker compose down
```

### 4.2 Running Smoke Tests Locally

```bash
python scripts/smoke_test.py --base-url http://localhost:8000
```

---

## 5. CI/CD Pipeline Workflow

```
GitHub Push
   │
   ▼
Jenkins Agent
   │
   ├─► 1. Checkout & Git SHA Extraction
   ├─► 2. Tool Validation (Python, Node, Docker, Compose)
   ├─► 3. Install Dependencies (Backend requirements, frontend npm ci)
   │
   ├─► 4. Parallel Quality Checks
   │      ├── Backend Ruff Linter
   │      ├── Backend Unit Tests (Pytest)
   │      ├── Frontend ESLint
   │      ├── Frontend TypeScript Check (tsc --noEmit)
   │      └── Frontend Component Tests (Vitest)
   │
   ├─► 5. Coverage Gate (Pytest --cov >= 80%)
   ├─► 6. Dependency Security (pip-audit & npm audit)
   ├─► 7. Secret Scan (Gitleaks)
   │
   ├─► 8. Integration Environment (docker compose -f docker-compose.ci.yml up -d)
   ├─► 9. Integration Tests (Real PostgreSQL CRUD verification)
   │
   ├─► 10. Application Build (Next.js bundle & backend import check)
   ├─► 11. Docker Build (taskflow-backend:<git-sha>, taskflow-frontend:<git-sha>)
   ├─► 12. Trivy Scan (Container CVE gate)
   │
   ├─► 13. Docker Hub Push (Branch: main only, uses DOCKERHUB_CREDENTIALS)
   ├─► 14. Deployment (Docker Compose with SHA image)
   ├─► 15. Health Checks (/health & Frontend HTTP)
   ├─► 16. Smoke Tests (scripts/smoke_test.py)
   │
   └─► 17. Post Cleanup & Report Archiving (JUnit XML, coverage.xml)
```

---

## 6. Branch Strategy

- **Feature Branches (`feat/*`, `fix/*`):**
  - Triggers complete validation: dependencies, linting, unit tests, coverage, security scans, integration tests, and Docker builds.
  - Releases and production deployments are **not triggered**.
- **Main Branch (`main`):**
  - Runs full validation pipeline.
  - Pushes immutable `<git-sha>` and `latest` tags to Docker Hub.
  - Automatically deploys the stack, verifies health endpoints, and executes smoke tests.

---

## 7. Security Best Practices

1. **No Hardcoded Secrets:** Passwords, tokens, and database credentials are strictly injected via environment variables.
2. **Pre-commit & CI Secret Gates:** Gitleaks scans the entire commit history for leaked API keys and passwords.
3. **Multi-Stage Container Hardening:** Containers run as non-privileged users (`appuser`, `nextjs`) without build compilers or secrets.
4. **Automated Vulnerability Management:** Dependency trees (pip-audit, npm audit) and base images (Trivy) are scanned on every build.
