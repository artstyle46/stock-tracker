from datetime import date
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from indexes.enums import IndexStrategy
from prices.models import DailyPrices


class IndexStrategyFactory:
    """
    Factory for handling index strategies.
    """

    @staticmethod
    def get_strategy(strategy_type: IndexStrategy) -> Callable:
        """
        Returns the appropriate strategy function based on the type.
        """
        strategies = {
            IndexStrategy.MARKET_CAP: IndexStrategyFactory._market_cap_strategy,
        }

        if strategy_type not in strategies:
            raise ValueError(f"Unsupported index strategy type: {strategy_type}")

        return strategies[strategy_type]

    @staticmethod
    async def _market_cap_strategy(
        db: AsyncSession, top_n: int, target_date: date
    ) -> list[int]:
        """
        Strategy to select top `m` stocks by market capitalization.
        """
        query = await db.execute(
            select(DailyPrices.stock_ticker_id)
            .where(DailyPrices.date == target_date)
            .order_by(DailyPrices.market_cap.desc())
            .limit(top_n)
        )
        return query.scalars().all()
