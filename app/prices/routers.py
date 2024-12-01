from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config import get_settings
from database import get_db
from logger import get_logger
from prices import paths
from prices.schema import DailyPriceResponse
from prices.services import fetch_all_daily_prices

logger = get_logger(__name__)
settings = get_settings()
tags = ["daily_price"]
router = APIRouter(prefix=paths.base)


@router.get(
    f"",
    status_code=status.HTTP_200_OK,
)
async def get_all_stocks(
    db: AsyncSession = Depends(get_db),
) -> list[DailyPriceResponse]:
    return await fetch_all_daily_prices(db=db)
