from datetime import date, datetime, timedelta, UTC

import yfinance as yf
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from logger import get_logger
from prices.models import DailyPrices
from prices.schema import DailyPriceResponse
from stocks.models import StockTicker
from stocks.services import fetch_all_tickers

logger = get_logger(__name__)


async def fetch_and_store_target_date_data(
    db: AsyncSession = Depends(get_db),
    start_date: date | None = None,
    end_date: date | None = None,
):
    end_date = (
        datetime.now(tz=UTC).date() - timedelta(days=1)
        if end_date is None
        else end_date
    )
    start_date = end_date - timedelta(days=30) if start_date is None else start_date
    tickers = await fetch_all_tickers(db=db)
    for ticker in tickers:
        stock = yf.Ticker(ticker.ticker)
        try:
            market_cap = stock.info.get("marketCap", 0.0)
            history = stock.history(start=start_date, end=end_date)
            for date, row in history.iterrows():
                daily_price = DailyPrices(
                    stock_ticker_id=ticker.id,
                    date=date,
                    close_price=row["Close"],
                    market_cap=market_cap,
                )
                db.add(daily_price)

            await db.commit()
        except Exception as e:
            logger.debug(f"Failed to fetch or store data for ticker {ticker}: {e}")
            await db.rollback()


async def check_if_history_data_is_present(
    db: AsyncSession = Depends(get_db), target_date: date | None = None
) -> bool:
    target_date = (
        datetime.now(tz=UTC).date() - timedelta(days=1)
        if target_date is None
        else target_date
    )
    tickers = await fetch_all_tickers(db=db)
    ticker_ids = [ticker.id for ticker in tickers]
    result = await db.execute(
        select(DailyPrices).where(
            DailyPrices.stock_ticker_id.in_(ticker_ids), DailyPrices.date == target_date
        )
    )
    existing_data = result.scalars().all()
    return len(existing_data) == len(tickers)


async def execute_ticker_price_fetcher(
    db: AsyncSession = Depends(get_db), target_date: date | None = None
):
    end_date = (
        datetime.now(tz=UTC).date() - timedelta(days=1)
        if target_date is None
        else target_date
    )
    start_date = end_date - timedelta(days=30)

    if start_date > end_date:
        raise ValueError("Start date should be less than end date.")
    if end_date - start_date > timedelta(days=30):
        raise ValueError("30 days is the limit of fetching history.")
    if not (await check_if_history_data_is_present(db=db, target_date=end_date)):
        await fetch_and_store_target_date_data(
            db=db, start_date=start_date, end_date=end_date
        )


async def fetch_all_daily_prices(db: AsyncSession) -> list[DailyPriceResponse]:
    query = select(DailyPrices, StockTicker.ticker).join(
        StockTicker, StockTicker.id == DailyPrices.stock_ticker_id
    )
    res = await db.execute(query)
    result = res.all()
    response_list = [
        DailyPriceResponse(
            id=row[0].id,
            ticker=row[1],
            close_price=row[0].close_price,
            market_cap=row[0].market_cap,
            date=row[0].date,
        )
        for row in result
    ]

    return response_list
