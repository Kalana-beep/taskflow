"""Task business logic and database persistence service."""

import math
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskListResponse, TaskStatsResponse, TaskUpdate


class TaskService:
    """Service handling business rules and persistence operations for Tasks."""

    @staticmethod
    async def create_task(db: AsyncSession, task_in: TaskCreate) -> Task:
        """Create a new task instance according to business rules."""
        now = datetime.now(UTC)
        completed_at = now if task_in.status == TaskStatus.DONE else None

        task = Task(
            id=uuid.uuid4(),
            title=task_in.title,
            description=task_in.description,
            status=task_in.status,
            priority=task_in.priority,
            created_at=now,
            updated_at=now,
            completed_at=completed_at,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def get_task_by_id(db: AsyncSession, task_id: uuid.UUID) -> Task | None:
        """Retrieve a task by its unique identifier."""
        query = select(Task).where(Task.id == task_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_tasks(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
    ) -> TaskListResponse:
        """List tasks with pagination, search, and filtering."""
        base_query = select(Task)
        count_query = select(func.count(Task.id))

        filters = []
        if status is not None:
            filters.append(Task.status == status)
        if priority is not None:
            filters.append(Task.priority == priority)
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            filters.append(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term),
                )
            )

        if filters:
            base_query = base_query.where(*filters)
            count_query = count_query.where(*filters)

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Pagination calculations
        pages = math.ceil(total / page_size) if total > 0 else 0
        offset = (page - 1) * page_size

        # Retrieve items ordered by creation date descending
        items_query = base_query.order_by(Task.created_at.desc()).offset(offset).limit(page_size)
        items_result = await db.execute(items_query)
        tasks = list(items_result.scalars().all())

        return TaskListResponse(
            items=tasks,
            page=page,
            page_size=page_size,
            total=total,
            pages=pages,
        )

    @staticmethod
    async def update_task(db: AsyncSession, task: Task, task_in: TaskUpdate) -> Task:
        """Update an existing task and maintain timestamp invariants."""
        now = datetime.now(UTC)
        update_data = task_in.model_dump(exclude_unset=True)

        if "title" in update_data and update_data["title"] is not None:
            task.title = update_data["title"]
        if "description" in update_data:
            task.description = update_data["description"]
        if "priority" in update_data and update_data["priority"] is not None:
            task.priority = update_data["priority"]

        if "status" in update_data and update_data["status"] is not None:
            new_status = update_data["status"]
            if new_status == TaskStatus.DONE and task.status != TaskStatus.DONE:
                task.completed_at = now
            elif new_status != TaskStatus.DONE and task.status == TaskStatus.DONE:
                task.completed_at = None
            task.status = new_status

        task.updated_at = now
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def delete_task(db: AsyncSession, task: Task) -> None:
        """Delete a task from storage."""
        await db.delete(task)
        await db.commit()

    @staticmethod
    async def get_task_stats(db: AsyncSession) -> TaskStatsResponse:
        """Compute aggregated dashboard statistics."""
        # Query total count
        total_query = select(func.count(Task.id))
        total = (await db.execute(total_query)).scalar_one()

        # Query TODO count
        todo_query = select(func.count(Task.id)).where(Task.status == TaskStatus.TODO)
        todo = (await db.execute(todo_query)).scalar_one()

        # Query IN_PROGRESS count
        in_progress_query = select(func.count(Task.id)).where(Task.status == TaskStatus.IN_PROGRESS)
        in_progress = (await db.execute(in_progress_query)).scalar_one()

        # Query DONE count
        done_query = select(func.count(Task.id)).where(Task.status == TaskStatus.DONE)
        done = (await db.execute(done_query)).scalar_one()

        # Query HIGH priority count
        high_query = select(func.count(Task.id)).where(Task.priority == TaskPriority.HIGH)
        high = (await db.execute(high_query)).scalar_one()

        return TaskStatsResponse(
            total=total,
            todo=todo,
            in_progress=in_progress,
            done=done,
            high_priority=high,
        )
