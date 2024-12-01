from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config import get_settings
from database import get_db
from logger import get_logger
from tasks import paths
from tasks.models import Tasks
from tasks.scheduler import execute_scheduled_tasks
from tasks.schema import TaskResponse

logger = get_logger(__name__)
settings = get_settings()
tags = ["tasks"]
router = APIRouter(prefix=paths.base)


@router.get(
    f"",
    status_code=status.HTTP_200_OK,
)
async def get_tasks(db: AsyncSession = Depends(get_db)) -> list[TaskResponse]:
    result = await db.execute(select(Tasks))
    return result.scalars().all()


@router.get(f"{paths.manual_execution}")
async def execute_tasks():
    await execute_scheduled_tasks()
