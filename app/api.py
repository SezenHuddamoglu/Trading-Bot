from fastapi import APIRouter
import logging
from app.trading import get_trade_history, get_current_prices  # trading.py'den fonksiyonları import et

api_router = APIRouter()

# Logger ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@api_router.get("/trades")
def get_trades():
    trades = get_trade_history()  # Binance'den alınan ticaret geçmişini al
    logger.info(f"Trades data: {trades}")  # Loglama
    return {"trades": trades}  # Ticaret geçmişini döndür

@api_router.get("/coins")
def get_coins():
    prices = get_current_prices()  # Binance'den alınan güncel fiyatları al
    logger.info(f"Coins data: {prices}")  # Loglama
    return {"coins": prices}  # Coin fiyatlarını döndür
