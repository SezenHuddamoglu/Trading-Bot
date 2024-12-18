from pydantic import BaseModel
from typing import List
from datetime import datetime

class CoinPrice(BaseModel):
    symbol: str
    price: float
    change: float  # Yüzde değişim

class Trade(BaseModel):
    action: str  # "Buy" veya "Sell"
    price: float
    amount: float
    timestamp: datetime
    indicator: str  # "RSI", "MACD", vb.
    deposit: float  
