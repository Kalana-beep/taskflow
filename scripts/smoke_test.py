#!/usr/bin/env python3
"""TaskFlow API Smoke Test Suite.

Executes end-to-end verification of critical service capabilities:
1. Health check (/health)
2. List tasks (/api/tasks)
3. Create task (POST /api/tasks)
4. Retrieve task (GET /api/tasks/{id})
5. Update task (PATCH /api/tasks/{id} - status to DONE)
6. Delete task (DELETE /api/tasks/{id})

Exits with code 0 on complete success, 1 on failure.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

# Configure utf-8 encoding for stdout on Windows if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def make_request(
    url: str,
    method: str = "GET",
    data: dict[str, Any] | None = None,
    expected_status: tuple[int, ...] = (200,),
) -> tuple[int, Any]:
    """Perform HTTP request and return (status_code, response_data)."""
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    body = json.dumps(data).encode("utf-8") if data is not None else None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            status_code = response.status
            raw_body = response.read().decode("utf-8")
            parsed_data = json.loads(raw_body) if raw_body else None

            if status_code not in expected_status:
                print(f"[FAIL] Unexpected status code {status_code} (expected {expected_status})")
                return status_code, parsed_data
            return status_code, parsed_data

    except urllib.error.HTTPError as e:
        raw_body = e.read().decode("utf-8")
        try:
            parsed_data = json.loads(raw_body)
        except Exception:
            parsed_data = raw_body

        if e.code in expected_status:
            return e.code, parsed_data

        print(f"[ERROR] HTTP {e.code} {e.reason}: {parsed_data}")
        return e.code, parsed_data

    except urllib.error.URLError as e:
        print(f"[ERROR] Connection failure for {url}: {e.reason}")
        return 0, None
    except Exception as e:
        print(f"[ERROR] Unexpected exception: {e}")
        return 0, None


def run_smoke_test(base_url: str) -> bool:
    """Execute smoke test sequence against the target base URL."""
    base_url = base_url.rstrip("/")
    print("=" * 60)
    print("TASKFLOW SMOKE TEST EXECUTION")
    print(f"Target URL: {base_url}")
    print("=" * 60)

    # 1. Health Probe
    print("\n[STEP 1/6] Probing /health endpoint...")
    status, body = make_request(f"{base_url}/health", method="GET", expected_status=(200,))
    if status != 200 or not isinstance(body, dict) or body.get("status") != "healthy":
        print(f"[FAIL] Health check returned invalid response: status={status}, body={body}")
        return False
    print("[PASS] Health check reported healthy.")

    # 2. List Tasks
    print("\n[STEP 2/6] Querying /api/tasks...")
    status, body = make_request(f"{base_url}/api/tasks?page=1&page_size=5", method="GET", expected_status=(200,))
    if status != 200 or not isinstance(body, dict) or "items" not in body:
        print(f"[FAIL] Task list returned invalid format: status={status}")
        return False
    print(f"[PASS] Task listing operational (current count in page: {len(body['items'])}).")

    # 3. Create Task
    print("\n[STEP 3/6] Creating verification task...")
    test_title = f"Smoke Test Task - {int(time.time())}"
    create_payload = {
        "title": test_title,
        "description": "Automated pipeline smoke test verification",
        "status": "TODO",
        "priority": "HIGH",
    }
    status, created = make_request(f"{base_url}/api/tasks", method="POST", data=create_payload, expected_status=(201,))
    if status != 201 or not isinstance(created, dict) or "id" not in created:
        print(f"[FAIL] Failed to create task: status={status}, response={created}")
        return False
    task_id = created["id"]
    print(f"[PASS] Created task successfully. ID: {task_id}")

    # 4. Retrieve Created Task
    print(f"\n[STEP 4/6] Retrieving task {task_id}...")
    status, retrieved = make_request(f"{base_url}/api/tasks/{task_id}", method="GET", expected_status=(200,))
    if status != 200 or not isinstance(retrieved, dict) or retrieved.get("title") != test_title:
        print(f"[FAIL] Failed to retrieve task correctly: status={status}, body={retrieved}")
        return False
    print("[PASS] Retrieved task matches created title.")

    # 5. Update Task
    print(f"\n[STEP 5/6] Updating task status to DONE...")
    update_payload = {
        "title": f"{test_title} [VERIFIED]",
        "status": "DONE",
    }
    status, updated = make_request(f"{base_url}/api/tasks/{task_id}", method="PATCH", data=update_payload, expected_status=(200,))
    if (
        status != 200
        or not isinstance(updated, dict)
        or updated.get("status") != "DONE"
        or updated.get("completed_at") is None
    ):
        print(f"[FAIL] Failed to update task or completed_at invariant not satisfied: {updated}")
        return False
    print(f"[PASS] Task updated to DONE. Completed at: {updated.get('completed_at')}")

    # 6. Delete Task
    print(f"\n[STEP 6/6] Deleting task {task_id}...")
    status, _ = make_request(f"{base_url}/api/tasks/{task_id}", method="DELETE", expected_status=(204,))
    if status != 204:
        print(f"[FAIL] Delete request did not return 204: status={status}")
        return False

    # Verify 404 on subsequent get
    status, _ = make_request(f"{base_url}/api/tasks/{task_id}", method="GET", expected_status=(404,))
    if status != 404:
        print(f"[FAIL] Expected 404 after deletion, got {status}")
        return False
    print("[PASS] Task deleted and verified non-existent (HTTP 404 confirmed).")

    print("\n" + "=" * 60)
    print("ALL SMOKE TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="TaskFlow Smoke Test Runner")
    parser.add_argument(
        "--base-url",
        default=os.getenv("TASKFLOW_BASE_URL", os.getenv("API_URL", "http://localhost:8000")),
        help="Base URL of the TaskFlow API service (e.g. http://localhost:8000)",
    )
    args = parser.parse_args()

    success = run_smoke_test(args.base_url)
    if not success:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
