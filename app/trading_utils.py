# app/trading_utils.py

from app.trading import start_trading

def start_trading_thread(coin, indicator, upper, lower, interval):
    try:
        print(f"Başlatılıyor: {coin}, {indicator}, {upper}, {lower}, {interval}")
        start_trading(coin, indicator, upper, lower, interval)
    except Exception as e:
        print(f"Ticaret başlatılırken hata oluştu: {e}")
