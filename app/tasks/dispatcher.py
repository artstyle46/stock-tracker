from sqlalchemy.ext.asyncio import AsyncSession

from indexes.services import execute_index_creator
from logger import get_logger
from prices.services import execute_ticker_price_fetcher
from stocks.services import execute_ticker_creator
from tasks.enums import TaskType
from tasks.models import Tasks

logger = get_logger(__name__)

TASK_EXECUTORS = {
    TaskType.TICKER_CREATOR: {
        "executor": execute_ticker_creator,
        "params": ["db"],
    },
    TaskType.TICKER_PRICE_FETCHER: {
        "executor": execute_ticker_price_fetcher,
        "params": ["db", "target_date"],
    },
    TaskType.INDEX_CREATOR: {
        "executor": execute_index_creator,
        "params": ["db", "stock_index_name", "target_date"],
    },
}


async def execute_task_by_type(db: AsyncSession, task: Tasks, **kwargs):
    """
    Dispatch execution based on the task type.
    """
    task_type = task.task_type
    task_entry = TASK_EXECUTORS.get(task_type)

    if not task_entry:
        raise ValueError(f"No executor defined for task type: {task_type}")

    executor = task_entry["executor"]
    required_params = task_entry.get("params", [])
    required_params = task_entry.get("params", [])
    executor_args = {
        param: kwargs.get(param) for param in required_params if param in kwargs
    }
    executor_args["db"] = db

    return await executor(**executor_args)
