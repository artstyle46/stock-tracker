from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config import get_settings
from database import get_db
from logger import get_logger
from stocks import paths
from stocks.models import StockTicker
from stocks.schema import StockRequest, StockResponse

logger = get_logger(__name__)
settings = get_settings()
tags = ["stock_ticker"]
router = APIRouter(prefix=paths.base)


@router.post(
    f"",
    status_code=status.HTTP_200_OK,
)
async def create_stock(
    data: StockRequest, db: AsyncSession = Depends(get_db)
) -> StockResponse:
    stock_ticker = StockTicker(**data.model_dump())
    db.add(stock_ticker)
    await db.commit()
    await db.refresh(stock_ticker)
    return stock_ticker


@router.get(
    f"",
    status_code=status.HTTP_200_OK,
)
async def get_all_stocks(db: AsyncSession = Depends(get_db)) -> list[StockResponse]:
    result = await db.execute(select(StockTicker))
    items = result.scalars().all()
    return items
