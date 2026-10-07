# ApexStore - Phased Implementation Roadmap

This document outlines the sequential engineering phases for building the full-stack ApexStore platform and DevOps automation pipeline.

---

## Phase Matrix

| Phase | Title | Focus Area | Status |
|---|---|---|---|
| **Phase 0** | Workspace Scaffolding & Git Foundation | Repository layout, `.gitignore`, `.env.example`, docs | **Completed** |
| **Phase 1** | Database Architecture & Core Data Models | PostgreSQL schema, SQLAlchemy models, Alembic, seed data | *Pending* |
| **Phase 2** | Backend Services, Redis Caching & REST APIs | FastAPI endpoints, JWT auth, stock locking, Redis cache | *Pending* |
| **Phase 3** | Frontend Foundation & Design System | Next.js setup, Tailwind styling, UI primitives, Zustand store | *Pending* |
| **Phase 4** | Customer Storefront Implementation | Home, Catalog, Product Details, Cart, Checkout, Tracking | *Pending* |
| **Phase 5** | Administrative Dashboard Implementation | Admin metrics, Product CRUD, Stock Restock Hub, Orders | *Pending* |
| **Phase 6** | Containerization & Local Orchestration | Multi-stage Dockerfiles, Docker Compose integration | *Pending* |
| **Phase 7** | Jenkins CI/CD Pipeline & Verification | Groovy Jenkinsfile, Trivy scan, Docker Hub, Smoke tests | *Pending* |

---

## Phase 0: Workspace Scaffolding & Git Foundation
* **Goal**: Establish the repository layout, configuration templates, and documentation baseline.
* **Deliverables**:
  * [x] Top-level directories: `frontend/`, `backend/`, `devops/`, `scripts/`, `docs/`.
  * [x] `.gitignore` configured for Node, Python, virtual environments, Docker, and IDEs.
  * [x] `.env.example` with safe placeholder variables (no real secrets).
  * [x] `README.md` containing project purpose, tech stack, and architectural flow.
  * [x] `docker-compose.yml` multi-container specification.
  * [x] `docs/architecture.md` high-level architecture documentation.
  * [x] `docs/development-roadmap.md` implementation plan.

---

## Phase 1: Database Architecture & Core Data Models
* **Goal**: Configure database access, write declarative SQLAlchemy models, and establish database migrations.
* **Deliverables**:
  * Setup `backend/` dependencies (`fastapi`, `sqlalchemy[asyncio]`, `asyncpg`, `pydantic`, `alembic`, `redis`).
  * Implement async database connection manager (`backend/app/core/database.py`).
  * Create SQLAlchemy 2.0 models:
    * `User` & `Address`
    * `Category`
    * `Product` & `ProductImage`
    * `Inventory` & `InventoryLog`
    * `Order` & `OrderItem`
  * Initialize Alembic migration scripts and run initial migration.
  * Author seed script (`backend/app/db/init_db.py`) creating admin user, product categories, and demo merchandise.

---

## Phase 2: Backend Business Logic, Redis Caching & REST APIs
* **Goal**: Implement business rules, transactional stock management, Redis caching, and REST endpoints.
* **Deliverables**:
  * JWT authentication and password hashing utilities (`backend/app/core/security.py`).
  * Pydantic v2 schemas for all requests and responses (`backend/app/schemas/`).
  * Service layer:
    * `AuthService`: Registration, authentication, token refresh.
    * `ProductService`: Catalog queries with Redis cache-aside caching.
    * `InventoryService`: Row-level locking (`SELECT ... FOR UPDATE`) and stock reservation.
    * `OrderService`: Transactional checkout and status progression.
    * `CacheService`: Redis connection management and key eviction hooks.
  * REST API router endpoints under `/api/v1`:
    * `/auth`
    * `/categories`
    * `/products`
    * `/inventory`
    * `/orders`
    * `/admin`
    * `/health`
  * Pytest test suite covering unit calculations and API integration flows.

---

## Phase 3: Frontend Foundation & Design System
* **Goal**: Scaffold Next.js App Router application with TypeScript and design system primitives.
* **Deliverables**:
  * Next.js project initialization with TypeScript, ESLint, and Tailwind CSS.
  * Design tokens: consistent typography, color palette (Slate + Indigo), spacing, and elevation.
  * Core UI components (`Button`, `Input`, `Dialog`, `Sheet`, `Badge`, `Card`, `Table`).
  * Feedback components: Skeleton loaders for catalogs and tables, empty states, and toast notifications.
  * Client state management: Zustand stores for persistent cart (`cart-store.ts`) and authentication (`auth-store.ts`).
  * Typed API client (`frontend/src/lib/api-client.ts`) interfacing with FastAPI backend.

---

## Phase 4: Customer Storefront Implementation
* **Goal**: Deliver a polished, responsive customer shopping experience.
* **Deliverables**:
  * Storefront layout with sticky header, live search, and slide-out cart drawer.
  * **Home Page (`/`)**: Hero promotion, featured categories, and trending products.
  * **Product Catalog (`/products`)**: Debounced search, category filters, price range slider, and pagination.
  * **Product Details (`/products/[slug]`)**: Image gallery, stock indicator badges, and quantity picker.
  * **Cart & Checkout (`/cart`, `/checkout`)**: Line-item management, shipping form, payment simulation, and order placement.
  * **Order Confirmation (`/checkout/success/[orderNumber]`)**: Summary and tracking details.
  * **Order History & Tracking (`/orders`, `/orders/[id]`)**: Visual progress stepper and order cancellation.
  * **Customer Authentication (`/login`, `/register`, `/profile`)**: Form validation and account profile.

---

## Phase 5: Administrative Dashboard Implementation
* **Goal**: Deliver back-office operational dashboard for inventory and order management.
* **Deliverables**:
  * Admin layout with collapsible sidebar and breadcrumbs header.
  * **Dashboard (`/admin`)**: Revenue KPIs, order count, low-stock warnings, and recent sales charts.
  * **Product Management (`/admin/products`)**: Catalog data table, create/edit modal, price updates.
  * **Inventory Hub (`/admin/inventory`)**: Stock level monitoring, threshold alerts, restock modal, and stock movement audit log.
  * **Order Fulfillment (`/admin/orders`)**: Filterable order directory, status transition stepper (`CONFIRMED` -> `SHIPPED` -> `DELIVERED`).
  * **Customer Directory (`/admin/customers`)**: Lifetime spend and order count table.

---

## Phase 6: Containerization & Local Orchestration
* **Goal**: Package frontend and backend into production-grade Docker containers and verify with Docker Compose.
* **Deliverables**:
  * Backend multi-stage `Dockerfile` with non-root user execution (`appuser`).
  * Frontend multi-stage `Dockerfile` leveraging Next.js standalone output.
  * Verified local `docker-compose.yml` running all 4 services (`postgres`, `redis`, `backend`, `frontend`).
  * Verify inter-container networking, environment injection, and health checks.

---

## Phase 7: Jenkins CI/CD Pipeline & End-to-End Verification
* **Goal**: Implement declarative Jenkins pipeline executing full CI/CD delivery lifecycle.
* **Deliverables**:
  * Declarative `Jenkinsfile` in Groovy with stages:
    1. Checkout SCM
    2. Parallel Code Quality & Linting (Ruff + ESLint + tsc)
    3. Parallel Automated Tests (Pytest + Frontend tests)
    4. Multi-stage Docker build
    5. Trivy container vulnerability scan
    6. Push images to Docker Hub
    7. Deploy application stack via Docker Compose
    8. Post-deploy automated HTTP smoke tests
  * Verification script checking `/health`, API catalog response, and frontend page rendering.
