import sqlalchemy as sa
from sqlalchemy.sql.schema import ForeignKey

from config import get_settings
from database import Base
from indexes.enums import IndexStrategy, PerformanceCalculation
from stocks.models import StockTicker

settings = get_settings()


class StockIndex(Base):
    __tablename__ = "stock_index"
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, index=True)
    name = sa.Column(
        sa.String, nullable=False, comment="Name of the Index.", unique=True
    )
    strategy = sa.Column(
        sa.Enum(IndexStrategy),
        nullable=False,
        server_default=IndexStrategy.MARKET_CAP,
        comment="Strategy used to add the stock in the index",
    )
    performance_calculation = sa.Column(
        sa.Enum(PerformanceCalculation),
        nullable=False,
        server_default=PerformanceCalculation.EQUAL_WEIGHTED,
        comment="Performance calculation of index",
    )
    ticker_count = sa.Column(sa.Integer, nullable=False)


class StockIndexTicker(Base):
    __tablename__ = "stock_index_ticker"
    """
    Every day n stock ticker per composition will be added to this table.
    """
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, index=True)
    date = sa.Column(sa.Date, nullable=False, comment="Stock Index ticker date")
    stock_ticker_id = sa.Column(
        sa.Integer, ForeignKey("stock_ticker.id"), nullable=False
    )
    stock_index_id = sa.Column(sa.Integer, ForeignKey("stock_index.id"), nullable=False)


class IndexPerformance(Base):
    __tablename__ = "index_performance"
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, index=True)
    stock_index_id = sa.Column(sa.Integer, ForeignKey("stock_index.id"), nullable=False)
    date = sa.Column(sa.Date, nullable=False, comment="Index Performance date")
    value = sa.Column(
        sa.Float, nullable=False, comment="Index performance value for a date"
    )
