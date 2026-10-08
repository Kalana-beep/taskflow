"""Task API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.task import TaskPriority, TaskStatus
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskStatsResponse,
    TaskUpdate,
)
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List tasks",
    description="Retrieve paginated tasks with optional search, status, and priority filtering.",
)
async def list_tasks(
    page: int = Query(default=1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(default=None, description="Search keyword in title or description"),
    status_filter: TaskStatus | None = Query(
        default=None, alias="status", description="Filter by status"
    ),
    priority_filter: TaskPriority | None = Query(
        default=None, alias="priority", description="Filter by priority"
    ),
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    """List tasks matching query filters."""
    return await TaskService.list_tasks(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        status=status_filter,
        priority=priority_filter,
    )


@router.get(
    "/stats",
    response_model=TaskStatsResponse,
    summary="Task dashboard statistics",
    description="Get count aggregates for tasks by status and priority.",
)
async def get_task_stats(db: AsyncSession = Depends(get_db)) -> TaskStatsResponse:
    """Retrieve statistical counters for the task dashboard."""
    return await TaskService.get_task_stats(db=db)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task entity. Timestamps and ID are managed by the server.",
)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Create a new task with given properties."""
    task = await TaskService.create_task(db=db, task_in=task_in)
    return TaskResponse.model_validate(task)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
    description="Retrieve detailed task information by unique UUID.",
)
async def get_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Retrieve a single task or raise 404."""
    task = await TaskService.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID '{task_id}' not found",
        )
    return TaskResponse.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description="Partially update a task's title, description, status, or priority.",
)
async def update_task(
    task_id: uuid.UUID,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Update existing task fields and maintain status timestamps."""
    task = await TaskService.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID '{task_id}' not found",
        )
    updated = await TaskService.update_task(db=db, task=task, task_in=task_in)
    return TaskResponse.model_validate(updated)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete a task by its unique ID.",
)
async def delete_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete task or raise 404."""
    task = await TaskService.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID '{task_id}' not found",
        )
    await TaskService.delete_task(db=db, task=task)
