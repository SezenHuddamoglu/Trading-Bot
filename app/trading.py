import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime, timedelta, timezone
import threading
import time
from tabulate import tabulate
from app.models import CoinPrice, Trade
from typing import List
import logging

# Logger'ı yapılandır
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Binance API anahtarlarınızı buraya ekleyin
api_key = "AhXe1renGVWgAKMX4gup2UWqF4n0XTpoyrXwYZCy2m60BGVe5x7wyiMweBpRSGLo"
secret_key = "2B3AgEpYaQOwLEQPq04Hq017F5i6ElzbEK6D9sdkcUg09RedJf96IoIuTf80hVrG"
testnet = True

client = Client(api_key=api_key, api_secret=secret_key)

symbol = "ETHUSDT"
bar_length = "5m"
g_symbol = "ETHUSDT"

# Verilerin saklanacağı listeler
price_history = []
trade_history: List[Trade] = []
current_prices: List[CoinPrice] = []

# Ticaret durumu
initial_balance = 10000  
balance = initial_balance
eth_coins = 0 
stop_trading = False  
loss_threshold = 0.90

state = 0  # 0 = nothing, 1 = bought, -1 = stoploss
total_profit = 0

# Lock nesnesi thread-safe veri erişimi için
data_lock = threading.Lock()

def computeRSI(data, time_window):
    diff = np.diff(data)
    up_chg = 0 * diff
    down_chg = 0 * diff

    up_chg[diff > 0] = diff[diff > 0]
    down_chg[diff < 0] = -diff[diff < 0]

    up_chg_avg = pd.Series(up_chg).ewm(com=time_window - 1, min_periods=time_window).mean()
    down_chg_avg = pd.Series(down_chg).ewm(com=time_window - 1, min_periods=time_window).mean()

    rs = up_chg_avg / down_chg_avg
    rsi = 100 - 100 / (1 + rs)
    return rsi.iloc[-1]

def MACD(interval, symbol):
    klines2 = client.get_klines(symbol=symbol, interval=interval, limit=60)
    closeVal = [float(entry[4]) for entry in klines2]
    closeVal = pd.Series(closeVal)
    ema12 = closeVal.ewm(span=12, adjust=False).mean()
    ema26 = closeVal.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()

    if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
        return 'BUY'
    elif macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]:
        return 'SELL'
    else:
        return 'HOLD'

def computeSupertrend(df, atr_period=14, multiplier=3):
    hl2 = (df['High'] + df['Low']) / 2
    atr = df['High'].rolling(window=atr_period).max() - df['Low'].rolling(window=atr_period).min()

    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)
    supertrend = np.where(df['Close'] <= lowerband, upperband, lowerband)
    return supertrend[-1]

def computeBollingerBands(df, window=20, num_std=2):
    rolling_mean = df['Close'].rolling(window=window).mean()
    rolling_std = df['Close'].rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band.iloc[-1], lower_band.iloc[-1]

def stopLoss(symbol):
    today = datetime.now().date()
    week_ago = today - timedelta(days=6)
    week_ago_str = week_ago.strftime('%d %b, %Y')
    klines2 = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, week_ago_str)
    highVal = [float(entry[2]) for entry in klines2]
    lowVal = [float(entry[3]) for entry in klines2]
    closeVal = [float(entry[4]) for entry in klines2]
    avgDownDrop = (sum(highVal) / len(highVal) - sum(lowVal) / len(lowVal)) / (sum(closeVal) / len(closeVal))
    stopVal = closeVal[-2] * (1 - avgDownDrop)
    return stopVal

def log_trade(action, price, amount, indicator):
    trade = Trade(
        action=action,
        price=price,
        amount=amount,
        timestamp=datetime.now(timezone.utc),
        indicator=indicator
    )
    with data_lock:
        trade_history.append(trade)
    logging.info(f"Trade executed: {trade.dict()}")

def update_current_prices():
    price = client.get_symbol_ticker(symbol=g_symbol)
    current_price = float(price['price'])
    # Yüzde değişimi hesaplamak için geçmiş fiyatlardan faydalanabilirsiniz
    with data_lock:
        if price_history:
            last_price = price_history[-1][1]
            change = ((current_price - last_price) / last_price) * 100
        else:
            change = 0.0
        coin_price = CoinPrice(symbol=g_symbol, price=current_price, change=change)
        current_prices.clear()
        current_prices.append(coin_price)

# app/trading.py (eklemeler)

def get_current_prices():
    with data_lock:
        return [coin.dict() for coin in current_prices]

def get_trade_history():
    with data_lock:
        return [trade.dict() for trade in trade_history]

def start_trading():
    global balance, eth_coins, stop_trading, state, total_profit
    while True:
        if stop_trading:
            logging.info("Trading stopped due to significant losses.")
            break  # Döngüyü kırarak ticareti durdur

        try:
            price = client.get_symbol_ticker(symbol=g_symbol)
            curr_price = float(price['price'])  # Güncel fiyat
            curr_time = datetime.now(timezone.utc)
            
            with data_lock:
                price_history.append((curr_time, curr_price))
            
            logging.info(f"Current Price: {curr_price} | Time: {curr_time}")

            klines = client.get_historical_klines(symbol=g_symbol, interval=bar_length, start_str=str(datetime.now(timezone.utc) - timedelta(days=60)), end_str=str(datetime.now(timezone.utc)))
            df = pd.DataFrame(klines, columns=["Open Time", "Open", "High", "Low", "Close", "Volume",
                                               "Close Time", "Quote Asset Volume", "Number of Trades",
                                               "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"])
            df["Date"] = pd.to_datetime(df["Open Time"], unit="ms")
            df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
            df.set_index("Date", inplace=True)

            for column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

            # Göstergeleri hesapla
            close_prices = df['Close'].values
            rsi = computeRSI(close_prices, 14)
            macd_signal = MACD(bar_length, g_symbol)
            supertrend_signal = computeSupertrend(df)
            upper_band, lower_band = computeBollingerBands(df)

            logging.info(f'RSI: {rsi}, MACD: {macd_signal}, Supertrend: {supertrend_signal}, Bollinger Upper: {upper_band}, Bollinger Lower: {lower_band}')

            eth_value = eth_coins * curr_price 
            total_portfolio_value = balance + eth_value  

            # Zararı durdur kontrolü
            if total_portfolio_value < initial_balance * loss_threshold:
                stop_trading = True 
                logging.info(f"Significant loss detected. Current portfolio value: {total_portfolio_value}. Stopping trading.")
                break  

            # Ticaret kararları
            if state == 0:
                if (rsi < 50 or macd_signal == 'BUY' or curr_price <= lower_band ):
                    num_coins_to_buy = balance / curr_price  
                    eth_coins += num_coins_to_buy  
                    balance -= num_coins_to_buy * curr_price  

                    if rsi < 50:
                        indicator = "RSI-based"
                    elif curr_price <= lower_band:
                        indicator = "Bollinger Band-based"
                    else:
                        indicator = "MACD-based"
                    
                    log_trade("Buy", curr_price, num_coins_to_buy, indicator)
                    logging.info(f"BUY: RSI: {rsi} | MACD: {macd_signal} | Price: {curr_price} | Indicator: {indicator}")
                    state = 1
                    
            elif state == 1:
                if (rsi > 55 or macd_signal == 'SELL' or curr_price >= upper_band ):
                    balance += eth_coins * curr_price  
                    log_trade("Sell", curr_price, eth_coins, "Strategy-based")
                    logging.info(f"SELL: RSI: {rsi} | MACD: {macd_signal} | Price: {curr_price} | Indicator: Strategy-based")
                    eth_coins = 0  
                    state = 0 

            elif float(curr_price) < stopLoss(g_symbol):
                stop_trading = True  # 'STOPLOSS'
                log_trade("Stoploss", curr_price, eth_coins, "Stoploss")
                logging.info(f"STOPLOSS triggered at price: {curr_price}")
                break

            # Anlık fiyatları güncelle
            update_current_prices()

            # Frontend için veri güncellemeleri
            time.sleep(10 * 1) if bar_length == '5m' else time.sleep(10 * 5)
        
        except Exception as e:
            logging.error(f"Error in trading loop: {e}")
            time.sleep(10)  # Hata durumunda bekleme süresi
