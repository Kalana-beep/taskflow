# ApexStore

> **Enterprise-Grade Full-Stack E-Commerce & DevOps Showcase**  
> A high-performance order and inventory management platform featuring a modern customer storefront, administrative operations dashboard, transactional FastAPI backend, Redis caching, and an automated Jenkins CI/CD pipeline.

---

## 1. Project Overview

**ApexStore** is built to demonstrate modern full-stack web engineering and enterprise DevOps best practices. It bridges customer-facing commerce experiences with warehouse inventory control and continuous delivery automation.

### Key Objectives
* **Modern Customer Storefront**: Responsive product browsing, instant search, faceted filtering, multi-image product showcases, shopping cart persistence, and end-to-end checkout.
* **Administrative Operations**: Real-time inventory monitoring, low-stock alerts, atomic stock restock workflows, order fulfillment transitions, customer CRM, and sales analytics.
* **Data Integrity & Concurrency**: Row-level locking on database transactions to guarantee stock consistency during simultaneous checkout spikes.
* **Performance Caching**: Redis cache-aside caching for catalog queries, paired with automated cache invalidation upon inventory or product updates.
* **DevOps Excellence**: Automated CI/CD with Jenkins, container security scanning (Trivy), Docker Hub registry publishing, and automated smoke testing.

---

## 2. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | [Next.js](https://nextjs.org/) (App Router), [TypeScript](https://www.typescriptlang.org/), [React](https://react.dev/), [Tailwind CSS](https://tailwindcss.com/), [Zustand](https://github.com/pmndrs/zustand), [Lucide Icons](https://lucide.dev/) |
| **Backend** | [Python 3.11](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org/), [Pydantic v2](https://docs.pydantic.dev/), [Alembic](https://alembic.sqlalchemy.org/) |
| **Data & Cache** | [PostgreSQL 16](https://www.postgresql.org/), [Redis 7](https://redis.io/) |
| **Containers** | [Docker](https://www.docker.com/) (Multi-stage builds), [Docker Compose v2](https://docs.docker.com/compose/) |
| **CI / CD** | [Jenkins](https://www.jenkins.io/) (Declarative Groovy Pipeline), [Docker Hub](https://hub.docker.com/), [GitHub](https://github.com/) |
| **Testing & Quality** | Pytest, Vitest / React Testing Library, ESLint, TypeScript (`tsc`), Ruff |

---

## 3. Planned Architecture

The platform uses a modular monolith topology for maximum developer velocity, reliability, and maintainability without distributed microservice complexity.

```
+-----------------------------------------------------------------------+
|                         Client Layer (Browser)                        |
|             Customer Storefront    |    Admin Dashboard               |
+----------------------------------+------------------------------------+
                                   | HTTP / JSON (REST)
                                   v
+-----------------------------------------------------------------------+
|                      Next.js Frontend Tier (:3000)                    |
|      - App Router (SSR & Client Components)                           |
|      - Zustand State (Cart & Auth)                                    |
|      - Tailwind CSS Design System                                     |
+----------------------------------+------------------------------------+
                                   | REST Requests
                                   v
+-----------------------------------------------------------------------+
|                      FastAPI Backend Tier (:8000)                     |
|      - JWT Authentication & RBAC (Customer / Admin)                   |
|      - Product Catalog & Category Services                            |
|      - Atomic Inventory Engine (Row-Level Locking)                    |
|      - Order Fulfillment & Checkout Processing                        |
+-------------------+-------------------------------+-------------------+
                    |                               |
                    v                               v
+---------------------------------------+   +---------------------------+
|             PostgreSQL 16             |   |          Redis 7          |
|    - ACID Relational Database         |   |    - Catalog Cache        |
|    - Users, Orders, Inventory, Logs   |   |    - Invalidation Hooks   |
+---------------------------------------+   +---------------------------+
```

*For complete architectural specifications, see [docs/architecture.md](docs/architecture.md).*

---

## 4. Planned CI/CD Flow

The delivery lifecycle is automated using a declarative `Jenkinsfile` in Groovy:

```
[GitHub Push]
     │
     ▼
[Stage 1: Checkout SCM]
     │
     ▼
[Stage 2: Code Quality & Linting] ─── Parallel: Ruff (Python) + ESLint / tsc (Next.js)
     │
     ▼
[Stage 3: Automated Testing]     ─── Parallel: Pytest (Backend) + Component Tests (Frontend)
     │
     ▼
[Stage 4: Multi-Stage Docker Build]
     │
     ▼
[Stage 5: Security Vulnerability Scan] ─── Trivy Container Scanner
     │
     ▼
[Stage 6: Docker Hub Publication]  ─── Tag with Build Number, Git SHA, and latest
     │
     ▼
[Stage 7: Stack Deployment]        ─── Docker Compose (Postgres + Redis + Backend + Frontend)
     │
     ▼
[Stage 8: Automated Smoke Tests]   ─── Verify /health probes, API catalog, and Storefront UI
```

---

## 5. Repository Structure

```
apexstore/
├── frontend/             # Next.js App Router application
├── backend/              # FastAPI application, SQLAlchemy models, API routers
├── devops/               # Jenkinsfile, CI/CD scripts, and deployment configs
├── scripts/              # Utility scripts for local setup, seeding, and smoke tests
├── docs/                 # System architecture, schemas, and roadmaps
│   ├── architecture.md
│   └── development-roadmap.md
├── .env.example          # Environment variable template (placeholders only)
├── .gitignore            # Git exclusion rules for Node, Python, Docker, OS
├── README.md             # Project documentation and guide
└── docker-compose.yml    # Local multi-container orchestration configuration
```

---

## 6. Current Development Status

* **Current Phase**: `Phase 0: Workspace Scaffolding & Git Foundation` (COMPLETED)
* **Next Phase**: `Phase 1: Database Architecture & Core Data Models`

*For the complete 8-phase implementation roadmap, consult [docs/development-roadmap.md](docs/development-roadmap.md).*

---

## 7. Getting Started (Phase 0)

1. Review configuration parameters in `.env.example`.
2. Inspect architectural blueprints in `docs/architecture.md`.
3. Track phase deliverables in `docs/development-roadmap.md`.
