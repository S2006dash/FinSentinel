from pydantic import BaseModel
from typing import Optional


class StockData(BaseModel):
    symbol: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class AnomalyEvent(BaseModel):
    symbol: str
    date: str
    anomaly_score: float
    priority: str
    reason: str
    price_change: Optional[float] = None
    volume_ratio: Optional[float] = None