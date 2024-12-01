from datetime import datetime

from pydantic import BaseModel

from stocks.enums import StockExchanges


class StockRequest(BaseModel):
    ticker: str
    name: str
    exchange: StockExchanges = StockExchanges.NASDAQ


class StockResponse(BaseModel):
    id: int
    ticker: str
    name: str
    exchange: StockExchanges
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
