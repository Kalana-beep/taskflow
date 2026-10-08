"""Pydantic schemas for Task validation and serialization."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    """Shared task properties."""

    title: str = Field(..., min_length=1, max_length=255, description="Title of the task")
    description: str | None = Field(default=None, max_length=5000, description="Optional details")


class TaskCreate(BaseModel):
    """Payload for creating a new task."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=255, description="Title of the task")
    description: str | None = Field(default=None, max_length=5000, description="Optional details")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Initial task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task urgency")


class TaskUpdate(BaseModel):
    """Payload for updating an existing task."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    status: TaskStatus | None = Field(default=None)
    priority: TaskPriority | None = Field(default=None)


class TaskResponse(BaseModel):
    """Standard serialized task response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class TaskListResponse(BaseModel):
    """Paginated collection of tasks."""

    items: list[TaskResponse]
    page: int
    page_size: int
    total: int
    pages: int


class TaskStatsResponse(BaseModel):
    """Aggregated statistics across all tasks."""

    total: int
    todo: int
    in_progress: int
    done: int
    high_priority: int
