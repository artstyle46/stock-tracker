from unittest.mock import mock_open, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from stocks.models import StockTicker
from stocks.services import fetch_all_tickers, ticker_data_from_csv


@pytest.mark.asyncio
async def test_ticker_data_from_csv():
    csv_content = "Symbol,Shortname\nAAPL,Apple Inc.\nGOOG,Alphabet Inc.\n"

    with patch("builtins.open", mock_open(read_data=csv_content)):
        result = await ticker_data_from_csv("dummy_path.csv")

    expected = {
        "AAPL": "Apple Inc.",
        "GOOG": "Alphabet Inc.",
    }

    assert result == expected


@pytest.mark.asyncio
async def test_fetch_all_tickers(test_db: AsyncSession):
    test_tickers = [
        {"ticker": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
        {"ticker": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
        {"ticker": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
    ]
    for ticker_data in test_tickers:
        ticker = StockTicker(**ticker_data)
        test_db.add(ticker)
    await test_db.commit()

    tickers = await fetch_all_tickers(test_db)

    assert len(tickers) == 3
    assert tickers[0].ticker == "AAPL"
    assert tickers[1].ticker == "GOOGL"
    assert tickers[2].ticker == "AMZN"

    assert tickers[0].name == "Apple Inc."
    assert tickers[0].exchange == "NASDAQ"
    assert tickers[1].name == "Alphabet Inc."
    assert tickers[1].exchange == "NASDAQ"
    assert tickers[2].name == "Amazon.com Inc."
    assert tickers[2].exchange == "NASDAQ"
