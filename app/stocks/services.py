import csv

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from logger import get_logger
from stocks.enums import StockExchanges
from stocks.models import StockTicker

logger = get_logger(__name__)


async def ticker_data_from_csv(
    csv_file: str = "stocks/data/10_companies.csv",
) -> dict[str, str]:
    ticker_name_map = {}

    with open(csv_file, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            ticker_name_map[row["Symbol"]] = row["Shortname"]
    return ticker_name_map


async def fetch_all_tickers(db: AsyncSession) -> list[StockTicker]:
    query = select(StockTicker)
    tickers = await db.execute(query)
    return tickers.scalars().all()


async def execute_ticker_creator(db: AsyncSession):
    tickers = await fetch_all_tickers(db)
    ticker_set = {ticker.ticker for ticker in tickers}
    ticker_name_map = await ticker_data_from_csv()

    tickers_to_create = []
    for ticker, name in ticker_name_map.items():
        if ticker not in ticker_set:
            tickers_to_create.append(
                StockTicker(ticker=ticker, name=name, exchange=StockExchanges.NASDAQ)
            )

    db.add_all(tickers_to_create)
    await db.commit()
