import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import TIMESTAMP

from config import get_settings
from database import Base
from stocks.enums import StockExchanges

settings = get_settings()


class StockTicker(Base):
    __tablename__ = "stock_ticker"
    __table_args__ = (
        UniqueConstraint(
            "ticker",
            "name",
            "exchange",
            name="_stock_ticker_uk_ticker_name_exchange",
        ),
    )
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, index=True)
    ticker = sa.Column(sa.String, nullable=False, comment="ticker of the stock")
    name = sa.Column(sa.String, nullable=False, comment="name of the stock.")
    exchange = sa.Column(
        sa.Enum(StockExchanges),
        nullable=False,
        comment="Stock exchange where the stock is present.",
    )
    created_at = sa.Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = sa.Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )
