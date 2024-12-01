from datetime import date, datetime, timedelta, UTC

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database import get_db
from indexes import paths
from indexes.schema import (
    CompositionResponse,
    IndexPerformanceResponse,
    StockIndexResponse,
    SummaryMetricsResponse,
)
from indexes.services import fetch_all_stock_index_ticker, IndexService
from logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
tags = ["indexes"]
router = APIRouter(prefix=paths.base)


@router.get(
    f"{paths.performance}",
    status_code=status.HTTP_200_OK,
)
async def get_performance(
    start_date: date | None = None,
    end_date: date | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[IndexPerformanceResponse]:
    end_date = datetime.now(tz=UTC).date() if end_date is None else end_date
    start_date = end_date - timedelta(days=30) if start_date is None else start_date
    return await IndexService().get_index_performance(
        db=db, start_date=start_date, end_date=end_date
    )


@router.get(
    f"{paths.summary}",
    status_code=status.HTTP_200_OK,
)
async def get_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    db: AsyncSession = Depends(get_db),
) -> SummaryMetricsResponse:
    end_date = datetime.now(tz=UTC).date() if end_date is None else end_date
    start_date = end_date - timedelta(days=30) if start_date is None else start_date
    return await IndexService().get_summary_metrics(
        db=db, start_date=start_date, end_date=end_date
    )


@router.get(
    f"{paths.composition}",
    status_code=status.HTTP_200_OK,
)
async def get_compostion(
    target_date: date | None = None, db: AsyncSession = Depends(get_db)
) -> CompositionResponse:
    target_date = datetime.now(tz=UTC).date() if target_date is None else target_date
    return await IndexService().get_composition_for_day(db=db, target_date=target_date)


@router.get(
    f"{paths.composition_change}",
    status_code=status.HTTP_200_OK,
)
async def get_compostion_change(
    start_date: date, end_date: date, db: AsyncSession = Depends(get_db)
) -> dict[date, bool]:
    return await IndexService().get_composition_change(
        db=db, start_date=start_date, end_date=end_date
    )


@router.get(
    f"{paths.stock_ticker_idx}",
    status_code=status.HTTP_200_OK,
)
async def get_stock_ticker_idx(
    db: AsyncSession = Depends(get_db),
) -> list[StockIndexResponse]:
    return await fetch_all_stock_index_ticker(db=db)
