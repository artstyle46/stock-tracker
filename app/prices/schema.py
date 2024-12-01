from datetime import date

from pydantic import BaseModel


class DailyPriceResponse(BaseModel):
    id: int
    ticker: str
    close_price: float
    market_cap: float
    date: date

    class Config:
        orm_mode = True
