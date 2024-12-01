from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from tasks.enums import TaskStatus, TaskType
from tasks.models import Tasks


class TaskService:
    @staticmethod
    async def create_task(
        db: AsyncSession,
        status: TaskStatus,
        task_type: TaskType,
        start_date: str | None = None,
        end_date: str | None = None,
        depends_on: int | None = None,
    ) -> Tasks:
        """
        Create a new task.
        """
        new_task = Tasks(
            status=status,
            task_type=task_type,
            start_date=start_date,
            end_date=end_date,
            depends_on=depends_on,
        )
        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)
        return new_task

    @staticmethod
    async def patch_task_status(
        db: AsyncSession,
        task_id: int,
        status: TaskStatus | None = None,
    ) -> Tasks | None:
        """
        Update task properties.
        """
        result = await db.execute(select(Tasks).where(Tasks.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            return None

        if status:
            task.status = status

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def read_tasks(
        db: AsyncSession,
        status: TaskStatus | None = None,
    ) -> list[Tasks]:
        """
        Retrieve tasks with optional filters.
        """
        query = select(Tasks)
        if status:
            query = query.where(Tasks.status == status)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def execute_task(db: AsyncSession, task_id: int) -> Tasks | None:
        """
        Execute a task after ensuring dependencies are complete.
        """
        result = await db.execute(select(Tasks).where(Tasks.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            return None

        if task.depends_on:
            dep_result = await db.execute(
                select(Tasks).where(Tasks.id == task.depends_on)
            )
            dependency_task = dep_result.scalar_one_or_none()

            if not dependency_task or dependency_task.status != TaskStatus.COMPLETED:
                raise Exception("Cannot execute task; dependency is not completed.")

        task.status = TaskStatus.IN_PROGRESS
        await db.commit()
        await db.refresh(task)

        return task
