from datetime import date

from pydantic import BaseModel

from indexes.enums import IndexStrategy, PerformanceCalculation


class StockIndexCreate(BaseModel):
    name: str
    strategy: IndexStrategy = IndexStrategy.MARKET_CAP
    performance_calculation: PerformanceCalculation = (
        PerformanceCalculation.EQUAL_WEIGHTED
    )
    ticker_count: int


class IndexPerformanceResponse(BaseModel):
    date: date
    index_value: float

    class Config:
        orm_mode = True


class SummaryMetricsResponse(BaseModel):
    cumulative_return: float
    average_daily_change: float
    composition_changes: list[int]
    daily_changes: list[float]


class TickerResponse(BaseModel):
    ticker: str
    market_cap: float
    close_price: float


class CompositionResponse(BaseModel):
    data: list[TickerResponse]
    target_date: date


class StockIndexResponse(BaseModel):
    id: int
    date: date
    stock_ticker_id: int
    stock_index_id: int
