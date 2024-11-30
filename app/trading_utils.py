import threading
from app.trading import start_trading

threads = {}

def start_trading_thread(coin, indicator, upper, lower, interval, trade_map):
    thread = threading.Thread(
        target=start_trading,
        args=(coin, indicator, upper, lower, interval),
        daemon=True
    )
    thread.start()
    trade_map[coin] = thread
    return thread
