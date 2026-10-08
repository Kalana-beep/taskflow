# Testing Strategy & Quality Assurance

TaskFlow enforces testing across three tiers: Unit Tests, Integration Tests, and Smoke Tests.

---

## 1. The Testing Pyramid

```
                / \
               /   \
              / Smoke\       (End-to-End API Workflow Verification)
             /---------\
            /Integrat-  \    (Real PostgreSQL & Container Endpoints)
           /    ion      \
          /---------------\
         /   Unit Tests    \  (Fast Pytest Async & Vitest Components)
        /-------------------\
```

---

## 2. Backend Unit Testing

Backend tests are written using `pytest` and `pytest-asyncio` utilizing an in-memory SQLite database via `aiosqlite` for millisecond-fast test isolation.

### Execution
```bash
pytest backend/tests/test_health.py backend/tests/test_tasks.py backend/tests/test_task_service.py \
  --cov=app \
  --cov-report=term-missing \
  --cov-report=xml:reports/coverage.xml \
  --cov-fail-under=80
```

### Coverage Requirement
- **Target:** >= 80% coverage on core application code.
- Current coverage achieves **90%** across `app/api`, `app/models`, `app/schemas`, and `app/services`.

---

## 3. Integration Testing

Integration tests verify data consistency and HTTP behaviors against live PostgreSQL containers without mocking.

### Running with CI Compose
```bash
# 1. Start ephemeral CI environment
docker compose -f docker-compose.ci.yml up -d

# 2. Run integration suite
INTEGRATION_BASE_URL="http://localhost:8001" pytest backend/tests/test_integration.py -v

# 3. Teardown CI environment
docker compose -f docker-compose.ci.yml down -v
```

### Verified Behaviors
1. `/health` operational readiness.
2. Task creation with persistent UUID and timestamps.
3. Task retrieval by ID.
4. Task updating and `completed_at` invariant logic.
5. Full text substring search across titles and descriptions.
6. Status filtering (`TODO`, `IN_PROGRESS`, `DONE`).
7. Priority filtering (`LOW`, `MEDIUM`, `HIGH`).
8. Task deletion and 404 confirmation.

---

## 4. End-to-End Smoke Testing

Executed via `scripts/smoke_test.py` as post-deployment gatekeeping:

```bash
python scripts/smoke_test.py --base-url http://localhost:8000
```

Validates complete lifecycle against production deployment before approving release.

---

## 5. Frontend Testing

Frontend tests use **Vitest** and **React Testing Library** with a mock DOM (`jsdom`):

```bash
cd frontend
npm test
```

Verifies:
- Dashboard KPI cards rendering and count accuracy.
- Empty states and user feedback banners.
- Error alerts on connectivity loss.
- Modal interactions and form submission.
- Real-time search query dispatch.
