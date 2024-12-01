from datetime import date
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from indexes.enums import PerformanceCalculation
from prices.models import DailyPrices


class PerformanceCalculatorFactory:
    @staticmethod
    def get_calculator(calculation_type: PerformanceCalculation) -> Callable:
        """
        Returns the appropriate performance calculation function.
        """
        calculators = {
            PerformanceCalculation.EQUAL_WEIGHTED: PerformanceCalculatorFactory._equal_weighted,
        }

        if calculation_type not in calculators:
            raise ValueError(
                f"Unsupported performance calculation type: {calculation_type}"
            )

        return calculators[calculation_type]

    @staticmethod
    async def _equal_weighted(
        db: AsyncSession, ticker_count: int, target_date: date
    ) -> float:
        """
        Equal-weighted performance calculation.
        """
        query = await db.execute(
            select(DailyPrices.close_price)
            .where(DailyPrices.date == target_date)
            .order_by(DailyPrices.market_cap.desc())
            .limit(ticker_count)
        )
        close_prices = query.scalars().all()

        return sum(close_prices) / len(close_prices) if close_prices else 0.0
