import traceback
from collections import deque
from datetime import datetime, timedelta, UTC

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config import get_settings
from indexes.enums import IndexStrategy, PerformanceCalculation
from indexes.schema import StockIndexCreate
from indexes.services import IndexService
from logger import get_logger
from tasks.dispatcher import execute_task_by_type
from tasks.enums import TaskStatus, TaskType
from tasks.models import Tasks

settings = get_settings()

logger = get_logger(__name__)


async def execute_scheduled_tasks(db: AsyncSession):
    """
    Execute tasks with dependencies.
    """
    task_queue = deque([])
    query = select(Tasks).where(
        Tasks.status.in_([TaskStatus.INITIATED, TaskStatus.FAILED])
    )
    result = await db.execute(query)
    tasks: list[Tasks] = result.scalars().all()

    for task in tasks:
        task_queue.append(task)
    while task_queue:
        task = task_queue.popleft()
        try:
            if task.depends_on:
                dep_result = await db.execute(
                    select(Tasks).where(Tasks.id == task.depends_on)
                )
                dependency_task = dep_result.scalar_one_or_none()

                if (
                    not dependency_task
                    or dependency_task.status != TaskStatus.COMPLETED
                ):
                    logger.debug(
                        f"Task {task.id} cannot be executed; dependency not completed."
                    )
                    task_queue.append(task)
                    continue

            result = await execute_task_by_type(
                db=db,
                task=task,
                stock_index_name=settings.STOCK_INDEX_NAME,
                target_date=task.run_date,
            )
            task.status = TaskStatus.COMPLETED
            await db.commit()
            logger.debug(f"Task {task.id} is now complete.")
        except Exception as e:
            traceback.print_exc()
            task.status = TaskStatus.FAILED
            await db.commit()
            logger.debug(f"Failed to execute task {task.id}: {e}")


async def create_startup_tasks(db: AsyncSession):
    """
    Create tasks that need to be run at the startup of the FastAPI app.
    Ensures:
      - TICKER_CREATOR task is created.
      - TICKER_PRICE_FETCHER task is created, dependent on TICKER_CREATOR.
      - INDEX_CREATOR task is created, dependent on TICKER_PRICE_FETCHER.
    """
    await IndexService.create_stock_index(
        db=db,
        stock_index_data=StockIndexCreate(
            name=settings.STOCK_INDEX_NAME,
            strategy=IndexStrategy.MARKET_CAP,
            performance_calculation=PerformanceCalculation.EQUAL_WEIGHTED,
            ticker_count=5,
        ),
    )
    end_date = datetime.now(tz=UTC).date() - timedelta(days=1)
    run_date = end_date - timedelta(days=30)
    existing_tasks = await db.execute(select(Tasks).where(Tasks.run_date == run_date))
    existing_tasks = existing_tasks.scalars().all()
    existing_task_types = {task.task_type for task in existing_tasks}

    if TaskType.TICKER_CREATOR not in existing_task_types:
        ticker_creation_task = Tasks(
            status=TaskStatus.INITIATED,
            task_type=TaskType.TICKER_CREATOR,
            run_date=run_date,
        )
        db.add(ticker_creation_task)
        await db.commit()
        await db.refresh(ticker_creation_task)
    else:
        ticker_creation_task = next(
            (
                task
                for task in existing_tasks
                if task.task_type == TaskType.TICKER_CREATOR
            ),
            None,
        )

    if (
        TaskType.TICKER_PRICE_FETCHER not in existing_task_types
        and ticker_creation_task
    ):
        ticker_price_fetcher_task = Tasks(
            status=TaskStatus.INITIATED,
            task_type=TaskType.TICKER_PRICE_FETCHER,
            run_date=run_date,
            depends_on=ticker_creation_task.id,
        )
        db.add(ticker_price_fetcher_task)
        await db.commit()
        await db.refresh(ticker_price_fetcher_task)
    else:
        ticker_price_fetcher_task = next(
            (
                task
                for task in existing_tasks
                if task.task_type == TaskType.TICKER_PRICE_FETCHER
            ),
            None,
        )
    while run_date < end_date:
        if (
            TaskType.INDEX_CREATOR not in existing_task_types
            and ticker_price_fetcher_task
        ):
            index_creation_task = Tasks(
                status=TaskStatus.INITIATED,
                task_type=TaskType.INDEX_CREATOR,
                run_date=run_date,
                depends_on=ticker_price_fetcher_task.id,
            )
            db.add(index_creation_task)
            await db.commit()
            await db.refresh(index_creation_task)

        run_date = run_date + timedelta(days=1)
