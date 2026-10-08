"""Real integration test suite verifying TaskFlow against live services."""

import os
import uuid

import pytest
from httpx import AsyncClient

INTEGRATION_BASE_URL = os.getenv("INTEGRATION_BASE_URL", "http://localhost:8001")


@pytest.fixture
async def live_client():
    """Client pointing to live running integration service."""
    async with AsyncClient(base_url=INTEGRATION_BASE_URL, timeout=15.0) as client:
        yield client


@pytest.mark.asyncio
async def test_integration_01_health(live_client: AsyncClient):
    """1. Health integration verification."""
    try:
        response = await live_client.get("/health")
    except Exception as e:
        pytest.skip(f"Integration environment not available at {INTEGRATION_BASE_URL}: {e}")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_integration_02_to_08_full_crud_lifecycle(live_client: AsyncClient):
    """Tests 2 through 8 in sequential real integration flow."""
    try:
        ping = await live_client.get("/health")
        if ping.status_code != 200:
            pytest.skip("Integration service unhealthy")
    except Exception as e:
        pytest.skip(f"Integration environment not available at {INTEGRATION_BASE_URL}: {e}")

    unique_suffix = str(uuid.uuid4())[:8]

    # 2. Create Task
    create_payload = {
        "title": f"Integration Task {unique_suffix}",
        "description": "Integration verification against real PostgreSQL",
        "status": "TODO",
        "priority": "HIGH",
    }
    create_res = await live_client.post("/api/tasks", json=create_payload)
    assert create_res.status_code == 201
    created_task = create_res.json()
    task_id = created_task["id"]
    assert created_task["title"] == create_payload["title"]
    assert created_task["status"] == "TODO"
    assert created_task["priority"] == "HIGH"
    assert created_task["completed_at"] is None

    # 3. Retrieve Task
    get_res = await live_client.get(f"/api/tasks/{task_id}")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["id"] == task_id
    assert retrieved["title"] == create_payload["title"]

    # 4. Update Task
    update_payload = {
        "title": f"Integration Task {unique_suffix} [Updated]",
        "status": "DONE",
    }
    patch_res = await live_client.patch(f"/api/tasks/{task_id}", json=update_payload)
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["title"] == update_payload["title"]
    assert updated["status"] == "DONE"
    assert updated["completed_at"] is not None

    # 5. Search
    search_res = await live_client.get(f"/api/tasks?search={unique_suffix}")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total"] >= 1
    assert any(item["id"] == task_id for item in search_data["items"])

    # 6. Status Filtering
    status_res = await live_client.get("/api/tasks?status=DONE")
    assert status_res.status_code == 200
    for item in status_res.json()["items"]:
        assert item["status"] == "DONE"

    # 7. Priority Filtering
    priority_res = await live_client.get("/api/tasks?priority=HIGH")
    assert priority_res.status_code == 200
    for item in priority_res.json()["items"]:
        assert item["priority"] == "HIGH"

    # 8. Delete Task
    del_res = await live_client.delete(f"/api/tasks/{task_id}")
    assert del_res.status_code == 204

    # Confirm deletion
    not_found_res = await live_client.get(f"/api/tasks/{task_id}")
    assert not_found_res.status_code == 404
