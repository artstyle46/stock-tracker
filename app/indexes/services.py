from collections import defaultdict
from datetime import date, datetime, timedelta, UTC

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config import get_settings
from database import get_db
from index_strategy.factory import IndexStrategyFactory
from indexes.models import IndexPerformance, StockIndex, StockIndexTicker
from indexes.schema import (
    CompositionResponse,
    IndexPerformanceResponse,
    StockIndexCreate,
    StockIndexResponse,
    SummaryMetricsResponse,
    TickerResponse,
)
from performance_calculation.factory import PerformanceCalculatorFactory
from prices.models import DailyPrices
from stocks.models import StockTicker

settings = get_settings()


class IndexService:
    @staticmethod
    async def create_stock_index(
        db: AsyncSession, stock_index_data: StockIndexCreate
    ) -> StockIndex:
        """
        Create a new stock index in the database.
        """
        result = await db.execute(
            select(StockIndex).filter(StockIndex.name == stock_index_data.name)
        )
        existing_index = result.scalars().first()

        if existing_index:
            return existing_index

        stock_index = StockIndex(
            name=stock_index_data.name,
            strategy=stock_index_data.strategy,
            performance_calculation=stock_index_data.performance_calculation,
            ticker_count=stock_index_data.ticker_count,
        )
        db.add(stock_index)
        await db.commit()
        await db.refresh(stock_index)
        return stock_index

    @staticmethod
    async def get_index_performance(
        db: AsyncSession, start_date: date, end_date: date
    ) -> list[IndexPerformanceResponse]:
        result = await db.execute(
            select(IndexPerformance)
            .join(StockIndex, StockIndex.id == IndexPerformance.stock_index_id)
            .where(StockIndex.name == settings.STOCK_INDEX_NAME)
            .where(IndexPerformance.date <= end_date)
            .where(IndexPerformance.date >= start_date)
        )
        out: list[IndexPerformanceResponse] = []
        for item in result.scalars().all():
            out.append(IndexPerformanceResponse(date=item.date, index_value=item.value))
        return out

    @staticmethod
    async def get_composition_for_day(
        db: AsyncSession, target_date: date
    ) -> CompositionResponse:
        result = await db.execute(
            select(StockTicker.ticker, DailyPrices.market_cap, DailyPrices.close_price)
            .select_from(StockIndexTicker)
            .join(StockIndex, StockIndex.id == StockIndexTicker.stock_index_id)
            .join(
                DailyPrices,
                DailyPrices.stock_ticker_id == StockIndexTicker.stock_ticker_id,
            )
            .join(StockTicker, StockTicker.id == StockIndexTicker.stock_ticker_id)
            .where(StockIndex.name == settings.STOCK_INDEX_NAME)
            .where(StockIndexTicker.date == target_date)
            .where(DailyPrices.date == target_date)
        )
        ticker_data: list[TickerResponse] = []

        for ticker, market_cap, close_price in result.all():
            ticker_data.append(
                TickerResponse(
                    ticker=ticker, market_cap=market_cap, close_price=close_price
                )
            )
        return CompositionResponse(
            data=ticker_data,
            target_date=target_date,
        )

    @staticmethod
    async def get_summary_metrics(
        db: AsyncSession, start_date: date, end_date: date
    ) -> SummaryMetricsResponse:
        result = await db.execute(
            select(IndexPerformance)
            .join(StockIndex, StockIndex.id == IndexPerformance.stock_index_id)
            .where(StockIndex.name == settings.STOCK_INDEX_NAME)
            .where(IndexPerformance.date <= end_date)
            .where(IndexPerformance.date >= start_date)
            .order_by(IndexPerformance.date.desc())
        )
        result = result.scalars().all()
        daily_changes: list[float] = []
        prev_performance_value: float = 0.0
        start_value = 0.0
        end_value = 0.0
        for idx_performance in result:
            if idx_performance.date == start_date:
                start_value = idx_performance.value
            if idx_performance.date == end_date:
                end_value = idx_performance.value
            if prev_performance_value > 0:
                daily_changes.append(idx_performance.value - prev_performance_value)
            prev_performance_value = idx_performance.value

        average_daily_change: float = sum(daily_changes) / len(daily_changes)
        cumulative_return: float = (
            ((end_value - start_value) / start_value) * 100 if start_value else 0.0
        )
        composition_changes: list[int] = []
        compostition_date_ticker_id_map: dict[date, set[int]] = defaultdict(set)
        result = await db.execute(
            select(StockIndexTicker)
            .join(StockIndex, StockIndex.id == StockIndexTicker.stock_index_id)
            .where(StockIndex.name == settings.STOCK_INDEX_NAME)
            .where(StockIndexTicker.date <= end_date)
            .where(StockIndexTicker.date >= start_date)
            .order_by(StockIndexTicker.date.desc())
        )
        for stock_idx_ticker in result.scalars().all():
            compostition_date_ticker_id_map[stock_idx_ticker.date].add(
                stock_idx_ticker.stock_ticker_id
            )

        prev_tickers: set[int] = set([])
        while start_date < end_date:
            if not prev_tickers:
                prev_tickers = compostition_date_ticker_id_map.get(start_date, set([]))
                start_date = start_date + timedelta(days=1)
                continue
            curr_tickers = compostition_date_ticker_id_map.get(start_date, set([]))
            composition_changes.append(len(curr_tickers.difference(prev_tickers)))
            start_date = start_date + timedelta(days=1)
            prev_tickers = curr_tickers

        return SummaryMetricsResponse(
            cumulative_return=cumulative_return,
            average_daily_change=average_daily_change,
            composition_changes=composition_changes,
            daily_changes=daily_changes,
        )

    @staticmethod
    async def get_composition_change(
        db: AsyncSession, start_date: date, end_date: date
    ) -> dict[date, bool]:
        composition_changes: dict[date, bool] = {}
        compostition_date_ticker_id_map: dict[date, set[int]] = defaultdict(set)
        result = await db.execute(
            select(StockIndexTicker)
            .join(StockIndex, StockIndex.id == StockIndexTicker.stock_index_id)
            .where(StockIndex.name == settings.STOCK_INDEX_NAME)
            .where(StockIndexTicker.date <= end_date)
            .where(StockIndexTicker.date >= start_date)
            .order_by(StockIndexTicker.date.desc())
        )
        for stock_idx_ticker in result.scalars().all():
            compostition_date_ticker_id_map[stock_idx_ticker.date].add(
                stock_idx_ticker.stock_ticker_id
            )

        prev_tickers: set[int] = set([])
        while start_date < end_date:
            if not prev_tickers:
                prev_tickers = compostition_date_ticker_id_map.get(start_date, set([]))
                start_date = start_date + timedelta(days=1)
                continue
            curr_tickers = compostition_date_ticker_id_map.get(start_date, set([]))
            composition_changes[start_date] = (
                len(curr_tickers.difference(prev_tickers)) > 0
            )
            start_date = start_date + timedelta(days=1)
            prev_tickers = curr_tickers
        return composition_changes

    @staticmethod
    async def get_stock_index(db: AsyncSession, stock_index_name: str):
        index_query = await db.execute(
            select(StockIndex).where(StockIndex.name == stock_index_name)
        )
        stock_index = index_query.scalar_one_or_none()
        if stock_index is None:
            raise ValueError("No stock index found for name")
        return stock_index

    @staticmethod
    async def build_index(db: AsyncSession, target_date: date, stock_index_name: str):
        """
        Build an index for the specified stock index and date.
        """
        stock_index = await IndexService.get_stock_index(
            db=db, stock_index_name=stock_index_name
        )

        index_strategy_factory = IndexStrategyFactory().get_strategy(
            stock_index.strategy
        )
        selected_stock_ids = await index_strategy_factory(
            db=db, top_n=stock_index.ticker_count, target_date=target_date
        )

        await IndexService._store_index_tickers(
            db=db,
            stock_index_id=stock_index.id,
            selected_stock_ids=selected_stock_ids,
            target_date=target_date,
        )

        performance_calculator_factory = PerformanceCalculatorFactory().get_calculator(
            stock_index.performance_calculation
        )
        index_performance_value = await performance_calculator_factory(
            db=db, ticker_count=stock_index.ticker_count, target_date=target_date
        )

        await IndexService._store_index_performance(
            db=db,
            stock_index_id=stock_index.id,
            value=index_performance_value,
            target_date=target_date,
        )

    @staticmethod
    async def _store_index_tickers(
        db: AsyncSession,
        stock_index_id: int,
        selected_stock_ids: list[int],
        target_date: date,
    ):
        """
        Store selected stocks in StockIndexTicker for the given index and date.
        """
        stock_index_tickers = [
            StockIndexTicker(
                date=target_date,
                stock_ticker_id=stock_ticker_id,
                stock_index_id=stock_index_id,
            )
            for stock_ticker_id in selected_stock_ids
        ]
        db.add_all(stock_index_tickers)
        await db.commit()

    @staticmethod
    async def _store_index_performance(
        db: AsyncSession, stock_index_id: int, value: float, target_date: date
    ):
        """
        Store selected stocks in Store Index performance for the given index and date.
        """
        index_performance = IndexPerformance(
            stock_index_id=stock_index_id,
            date=target_date,
            value=value,
        )
        db.add(index_performance)
        await db.commit()

    @staticmethod
    async def is_index_calculated_and_tickers_present(
        db: AsyncSession, stock_index_name: str, target_date: date
    ) -> bool:
        """
        Check if index calculation and tickers are already added for a specific stock index and date.
        """
        stock_index = await IndexService.get_stock_index(
            db=db, stock_index_name=stock_index_name
        )

        performance_result = await db.execute(
            select(IndexPerformance).where(
                IndexPerformance.stock_index_id == stock_index.id,
                IndexPerformance.date == target_date,
            )
        )
        is_performance_calculated = performance_result.scalars().first() is not None

        tickers_result = await db.execute(
            select(StockIndexTicker).where(
                StockIndexTicker.stock_index_id == stock_index.id,
                StockIndexTicker.date == target_date,
            )
        )
        are_tickers_present = tickers_result.scalars().first() is not None

        return are_tickers_present and is_performance_calculated


async def execute_index_creator(
    db: AsyncSession = Depends(get_db),
    stock_index_name: str | None = None,
    target_date: date | None = None,
):
    target_date = (
        datetime.now(tz=UTC).date()
        if target_date is None
        else target_date
    )
    stock_index_name = (
        settings.STOCK_INDEX_NAME if stock_index_name is None else stock_index_name
    )

    if not (
        await IndexService.is_index_calculated_and_tickers_present(
            db=db, stock_index_name=stock_index_name, target_date=target_date
        )
    ):
        await IndexService.build_index(
            db=db, target_date=target_date, stock_index_name=stock_index_name
        )


async def fetch_all_stock_index_ticker(db: AsyncSession) -> list[StockIndexResponse]:
    query = select(StockIndexTicker)
    res = await db.execute(query)
    return res.scalars().all()
