"""Direct unit tests for TaskService methods."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService


@pytest.mark.asyncio
async def test_service_create_and_get_task(db_session: AsyncSession) -> None:
    """Test creating and retrieving task via TaskService."""
    create_dto = TaskCreate(
        title="Direct Service Test",
        description="Testing service logic directly",
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
    )
    task = await TaskService.create_task(db_session, create_dto)
    assert task.id is not None
    assert task.title == "Direct Service Test"
    assert task.completed_at is None

    fetched = await TaskService.get_task_by_id(db_session, task.id)
    assert fetched is not None
    assert fetched.id == task.id

    # Non-existent task returns None
    missing = await TaskService.get_task_by_id(db_session, uuid.uuid4())
    assert missing is None


@pytest.mark.asyncio
async def test_service_update_task_status_transition(db_session: AsyncSession) -> None:
    """Test update status transitions and completed_at handling."""
    task = await TaskService.create_task(
        db_session,
        TaskCreate(title="Transition Task", status=TaskStatus.TODO),
    )
    assert task.completed_at is None

    # Transition to DONE
    updated_done = await TaskService.update_task(
        db_session,
        task,
        TaskUpdate(status=TaskStatus.DONE),
    )
    assert updated_done.status == TaskStatus.DONE
    assert updated_done.completed_at is not None

    # Transition back to TODO
    updated_todo = await TaskService.update_task(
        db_session,
        updated_done,
        TaskUpdate(status=TaskStatus.TODO),
    )
    assert updated_todo.status == TaskStatus.TODO
    assert updated_todo.completed_at is None


@pytest.mark.asyncio
async def test_service_list_tasks_and_search(db_session: AsyncSession) -> None:
    """Test listing tasks with search filters and pagination."""
    await TaskService.create_task(
        db_session,
        TaskCreate(title="Alpha Unique Task", description="Special description"),
    )
    await TaskService.create_task(
        db_session,
        TaskCreate(title="Beta Common Task", description="Alpha in description"),
    )

    # Search for "Alpha" -> matches 2 tasks (one title, one description)
    result = await TaskService.list_tasks(db_session, search="Alpha")
    assert result.total == 2
    assert len(result.items) == 2

    # Search for non-existent keyword
    empty_result = await TaskService.list_tasks(db_session, search="NonExistent12345")
    assert empty_result.total == 0
    assert len(empty_result.items) == 0


@pytest.mark.asyncio
async def test_service_delete_task(db_session: AsyncSession) -> None:
    """Test deleting task via TaskService."""
    task = await TaskService.create_task(
        db_session,
        TaskCreate(title="Task to Delete"),
    )
    task_id = task.id

    await TaskService.delete_task(db_session, task)
    fetched = await TaskService.get_task_by_id(db_session, task_id)
    assert fetched is None


@pytest.mark.asyncio
async def test_service_get_stats(db_session: AsyncSession) -> None:
    """Test stats computation directly via TaskService."""
    await TaskService.create_task(
        db_session,
        TaskCreate(title="T1", status=TaskStatus.TODO, priority=TaskPriority.HIGH),
    )
    await TaskService.create_task(
        db_session,
        TaskCreate(title="T2", status=TaskStatus.IN_PROGRESS, priority=TaskPriority.MEDIUM),
    )
    await TaskService.create_task(
        db_session,
        TaskCreate(title="T3", status=TaskStatus.DONE, priority=TaskPriority.HIGH),
    )

    stats = await TaskService.get_task_stats(db_session)
    assert stats.total == 3
    assert stats.todo == 1
    assert stats.in_progress == 1
    assert stats.done == 1
    assert stats.high_priority == 2
