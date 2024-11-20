from fastapi import APIRouter
from app.trading import get_current_prices, get_trade_history

router = APIRouter()

@router.get("/coins")
def read_coins():
    # """
    # Anlık coin fiyatlarını döner.
    # """
    return get_current_prices()

@router.get("/trades")
def read_trades():
    # """
    # Yapılan alım-satım işlemlerini döner.
    # """
    return get_trade_history()
