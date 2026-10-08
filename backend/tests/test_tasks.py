"""Comprehensive API route test suite for tasks."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task_success(async_client: AsyncClient) -> None:
    """Test creating a task with defaults."""
    payload = {
        "title": "Complete DevOps Pipeline",
        "description": "Implement Jenkins and Docker automation",
    }
    response = await async_client.post("/api/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["status"] == "TODO"
    assert data["priority"] == "MEDIUM"
    assert "id" in data
    assert data["created_at"] is not None
    assert data["updated_at"] is not None
    assert data["completed_at"] is None


@pytest.mark.asyncio
async def test_create_task_with_custom_status_and_priority(async_client: AsyncClient) -> None:
    """Test creating a task with specified status and priority."""
    payload = {
        "title": "Fix Production Incident",
        "description": "Database connection pool exhausted",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
    }
    response = await async_client.post("/api/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "IN_PROGRESS"
    assert data["priority"] == "HIGH"


@pytest.mark.asyncio
async def test_create_task_with_done_sets_completed_at(async_client: AsyncClient) -> None:
    """Test creating a task initialized to DONE sets completed_at."""
    payload = {
        "title": "Already Completed Task",
        "status": "DONE",
        "priority": "LOW",
    }
    response = await async_client.post("/api/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "DONE"
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_create_task_validation_errors(async_client: AsyncClient) -> None:
    """Test validation errors for invalid payloads."""
    # Missing title
    res_missing_title = await async_client.post("/api/tasks", json={"description": "no title"})
    assert res_missing_title.status_code == 422

    # Empty title
    res_empty_title = await async_client.post("/api/tasks", json={"title": ""})
    assert res_empty_title.status_code == 422

    # Title exceeding max length
    res_long_title = await async_client.post("/api/tasks", json={"title": "x" * 256})
    assert res_long_title.status_code == 422

    # Invalid status
    res_invalid_status = await async_client.post(
        "/api/tasks", json={"title": "Valid", "status": "NOT_A_STATUS"}
    )
    assert res_invalid_status.status_code == 422

    # Invalid priority
    res_invalid_priority = await async_client.post(
        "/api/tasks", json={"title": "Valid", "priority": "CRITICAL"}
    )
    assert res_invalid_priority.status_code == 422

    # Client attempting to inject forbidden fields (extra='forbid')
    res_extra_fields = await async_client.post(
        "/api/tasks",
        json={
            "title": "Hacker Task",
            "id": str(uuid.uuid4()),
        },
    )
    assert res_extra_fields.status_code == 422


@pytest.mark.asyncio
async def test_get_task_by_id(async_client: AsyncClient) -> None:
    """Test getting an existing task by ID and 404 behavior."""
    # Create task
    create_res = await async_client.post("/api/tasks", json={"title": "Read Architecture Docs"})
    task_id = create_res.json()["id"]

    # Fetch task
    get_res = await async_client.get(f"/api/tasks/{task_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == task_id
    assert get_res.json()["title"] == "Read Architecture Docs"

    # Non-existent UUID
    fake_id = uuid.uuid4()
    not_found = await async_client.get(f"/api/tasks/{fake_id}")
    assert not_found.status_code == 404

    # Malformed UUID
    invalid_uuid = await async_client.get("/api/tasks/not-a-uuid")
    assert invalid_uuid.status_code == 422


@pytest.mark.asyncio
async def test_patch_task_lifecycle(async_client: AsyncClient) -> None:
    """Test updating task fields and completed_at lifecycle invariant."""
    create_res = await async_client.post("/api/tasks", json={"title": "Original Title"})
    task_id = create_res.json()["id"]
    assert create_res.json()["completed_at"] is None

    # Update title and priority
    patch_res = await async_client.patch(
        f"/api/tasks/{task_id}",
        json={"title": "Updated Title", "priority": "HIGH"},
    )
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["title"] == "Updated Title"
    assert data["priority"] == "HIGH"
    assert data["status"] == "TODO"
    assert data["completed_at"] is None

    # Transition to DONE -> completed_at must be populated
    done_res = await async_client.patch(
        f"/api/tasks/{task_id}",
        json={"status": "DONE"},
    )
    assert done_res.status_code == 200
    assert done_res.json()["status"] == "DONE"
    assert done_res.json()["completed_at"] is not None

    # Transition away from DONE -> completed_at must be reset to null
    todo_res = await async_client.patch(
        f"/api/tasks/{task_id}",
        json={"status": "IN_PROGRESS"},
    )
    assert todo_res.status_code == 200
    assert todo_res.json()["status"] == "IN_PROGRESS"
    assert todo_res.json()["completed_at"] is None

    # Update non-existent task
    fake_id = uuid.uuid4()
    patch_404 = await async_client.patch(f"/api/tasks/{fake_id}", json={"title": "Ghost"})
    assert patch_404.status_code == 404


@pytest.mark.asyncio
async def test_delete_task(async_client: AsyncClient) -> None:
    """Test deleting task and verifying 404 behavior."""
    create_res = await async_client.post("/api/tasks", json={"title": "To be deleted"})
    task_id = create_res.json()["id"]

    # Delete task
    del_res = await async_client.delete(f"/api/tasks/{task_id}")
    assert del_res.status_code == 204

    # Verify task no longer exists
    get_res = await async_client.get(f"/api/tasks/{task_id}")
    assert get_res.status_code == 404

    # Deleting non-existent task returns 404
    del_again = await async_client.delete(f"/api/tasks/{task_id}")
    assert del_again.status_code == 404


@pytest.mark.asyncio
async def test_list_tasks_pagination_and_filtering(async_client: AsyncClient) -> None:
    """Test pagination, search, status, and priority query filters."""
    # Seed multiple tasks
    await async_client.post(
        "/api/tasks",
        json={
            "title": "Write Unit Tests",
            "description": "Backend pytest",
            "status": "TODO",
            "priority": "HIGH",
        },
    )
    await async_client.post(
        "/api/tasks",
        json={
            "title": "Configure Jenkins",
            "description": "Declarative pipeline",
            "status": "IN_PROGRESS",
            "priority": "HIGH",
        },
    )
    await async_client.post(
        "/api/tasks",
        json={
            "title": "Deploy NextJS App",
            "description": "Frontend UI",
            "status": "DONE",
            "priority": "LOW",
        },
    )
    await async_client.post(
        "/api/tasks",
        json={
            "title": "Database Migrations",
            "description": "Alembic setup",
            "status": "DONE",
            "priority": "MEDIUM",
        },
    )

    # List all
    res = await async_client.get("/api/tasks")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 4
    assert len(data["items"]) >= 4

    # Pagination: page_size=2
    res_page = await async_client.get("/api/tasks?page=1&page_size=2")
    assert res_page.status_code == 200
    data_page = res_page.json()
    assert len(data_page["items"]) == 2
    assert data_page["page"] == 1
    assert data_page["page_size"] == 2

    # Status filter: DONE
    res_status = await async_client.get("/api/tasks?status=DONE")
    assert res_status.status_code == 200
    for item in res_status.json()["items"]:
        assert item["status"] == "DONE"

    # Priority filter: HIGH
    res_priority = await async_client.get("/api/tasks?priority=HIGH")
    assert res_priority.status_code == 200
    for item in res_priority.json()["items"]:
        assert item["priority"] == "HIGH"

    # Search filter: "Jenkins"
    res_search = await async_client.get("/api/tasks?search=Jenkins")
    assert res_search.status_code == 200
    assert res_search.json()["total"] == 1
    assert res_search.json()["items"][0]["title"] == "Configure Jenkins"


@pytest.mark.asyncio
async def test_get_task_stats(async_client: AsyncClient) -> None:
    """Test dashboard stats endpoint calculation."""
    # Clear / start fresh: create known distribution
    await async_client.post(
        "/api/tasks",
        json={"title": "Task A", "status": "TODO", "priority": "HIGH"},
    )
    await async_client.post(
        "/api/tasks",
        json={"title": "Task B", "status": "IN_PROGRESS", "priority": "HIGH"},
    )
    await async_client.post(
        "/api/tasks",
        json={"title": "Task C", "status": "DONE", "priority": "LOW"},
    )

    stats_res = await async_client.get("/api/tasks/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total"] >= 3
    assert stats["todo"] >= 1
    assert stats["in_progress"] >= 1
    assert stats["done"] >= 1
    assert stats["high_priority"] >= 2
