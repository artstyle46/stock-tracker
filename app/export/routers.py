import os

import pandas as pd
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from export import paths
from export.factory import ExporterFactory
from indexes.models import IndexPerformance
from indexes.services import IndexService
from logger import get_logger

logger = get_logger(__name__)
tags = ["export"]
router = APIRouter(prefix=paths.base)


@router.get(
    f"{paths.index_performance}",
    status_code=status.HTTP_200_OK,
)
async def export_index_performance(
    file_type: str = Query(..., description="File type: 'xls' or 'pdf'"),
    db: AsyncSession = Depends(get_db),
):
    """
    Export index performance data to the specified file type (xls or PDF).
    """
    query = select(IndexPerformance).order_by(IndexPerformance.date)
    result = await db.execute(query)
    index_data = result.scalars().all()

    if not index_data:
        return {"error": "No data available for export"}

    df = pd.DataFrame(
        [{"date": str(row.date), "index_value": row.value} for row in index_data]
    )

    file_name = f"index_performance.{file_type}"
    exporter = ExporterFactory.get_exporter(file_type)
    file_path = os.path.join("/tmp", file_name)
    exporter.export(df, file_path)

    return FileResponse(file_path, filename=file_name)


@router.get(
    f"{paths.composition}",
    status_code=status.HTTP_200_OK,
)
async def export_composition(
    date: str = Query(..., description="Date for composition (YYYY-MM-DD)"),
    file_type: str = Query(..., description="File type: 'xls' or 'pdf'"),
    db: AsyncSession = Depends(get_db),
):
    """
    Export composition data for a specific date to the specified file type (xls or PDF).
    """
    composition_data = await IndexService().get_composition_for_day(
        db=db, target_date=date
    )

    df = pd.DataFrame(
        [
            {
                "ticker": row.ticker,
                "close_price": row.close_price,
                "market_cap": row.market_cap,
            }
            for row in composition_data.data
        ]
    )

    file_name = f"composition_{date}.{file_type}"
    exporter = ExporterFactory.get_exporter(file_type)
    file_path = os.path.join("/tmp", file_name)
    exporter.export(df, file_path)

    return FileResponse(file_path, filename=file_name)
