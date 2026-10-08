"""Base metadata collector for Alembic migrations.

Imports all SQLAlchemy models to ensure they are registered with Base.metadata.
"""

from app.db.database import Base
from app.models.task import Task, TaskPriority, TaskStatus

__all__ = ["Base", "Task", "TaskStatus", "TaskPriority"]
