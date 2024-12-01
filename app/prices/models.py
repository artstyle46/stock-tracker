import sqlalchemy as sa
from sqlalchemy.sql.schema import ForeignKey

from config import get_settings
from database import Base
from stocks.models import StockTicker

settings = get_settings()


class DailyPrices(Base):
    __tablename__ = "daily_prices_all"
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, index=True)
    stock_ticker_id = sa.Column(
        sa.Integer, ForeignKey("stock_ticker.id"), nullable=True
    )
    date = sa.Column(sa.Date, nullable=False, comment="Price of the stock at a date")
    close_price = sa.Column(
        sa.Float, nullable=False, comment="Close price of the stock."
    )
    market_cap = sa.Column(sa.Float, nullable=False, comment="Market cap of the stock.")
