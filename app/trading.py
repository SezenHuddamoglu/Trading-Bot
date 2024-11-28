import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime, timedelta, timezone
import threading
import logging
from typing import List
import time 
from threading import Thread

# Logger yapılandırması
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Binance API bilgileri (çevresel değişkenlerden alınmalı)
api_key = ""
secret_key = ""


client = Client(api_key=api_key, api_secret=secret_key)

# Ticaret parametreleri
INITIAL_BALANCE = 10000  # Başlangıç bakiyesi
LOSS_THRESHOLD = 0.90  # Zarar durdurma eşiği
RSI_PERIOD = 14
TRADE_INTERVALS = ["1m", "5m", "15m", "30m", "1h"]

# Ticaret değişkenleri
balance = INITIAL_BALANCE
eth_coins = 0
stop_trading = False
trade_history = []
price_history = []
lock = threading.Lock()
state = 0

# RSI Hesaplama
def compute_rsi(data, period):
    diff = np.diff(data)
    gain = np.maximum(diff, 0)
    loss = np.abs(np.minimum(diff, 0))
    avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

# MACD Hesaplama
def compute_macd(prices, short_window=12, long_window=26, signal_window=9):
    short_ema = prices.ewm(span=short_window, adjust=False).mean()
    long_ema = prices.ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd.iloc[-1], signal.iloc[-1]

# Bollinger Band Hesaplama
def compute_bollinger_bands(data, window=20, num_std_dev=2):
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std_dev)
    lower_band = rolling_mean - (rolling_std * num_std_dev)
    return upper_band.iloc[-1], lower_band.iloc[-1]

# İşlem kaydı
def log_trade(action, price, amount, indicator):
    global balance
    with lock:
        trade = {
            "action": action,
            "price": price,
            "amount": amount,
            "timestamp": datetime.now(timezone.utc),
            "indicator": indicator,
            "balance": balance,
        }
        trade_history.append(trade)
    logging.info(f"Trade executed: {trade}")

def log_hold_state(curr_price, indicator):
    print(f"HOLD: Current Price: {curr_price:.2f} | Indicator: {indicator}")
    logging.info(f"HOLD: Current Price: {curr_price:.2f} | Indicator: {indicator}")

    
def get_current_prices(target_coins):
    """
    Binance API'sinden belirlenen coin'ler için güncel fiyatları ve değişim oranlarını alır.
    """
    #target_coins = ["BNB", "BTC", "ETH", "DOGE", "SOL", "XRP"]
    all_tickers = client.get_ticker()  # Binance'den tüm coin bilgilerini alır
    filtered_data = [
        {
            "symbol": ticker["symbol"].replace("USDT", ""),  # "USDT" kısmını kaldır
            "price": float(ticker["lastPrice"]),
            "change": float(ticker["priceChangePercent"]) / 100  # Yüzdelik oranı ondalık hale getir
        }
        for ticker in all_tickers
        if ticker["symbol"] in [f"{coin}USDT" for coin in target_coins]  # USDT çiftlerini filtrele
    ]
    return filtered_data
    
def get_trade_history():
    with lock:
        # trade_history içindeki datetime gibi serileştirilemeyen verileri kontrol edin
        serialized_history = []
        for trade in trade_history:
            serialized_trade = trade.copy()  # Orijinal veriyi koruyarak kopya oluşturun
            if isinstance(trade["timestamp"], datetime):
                serialized_trade["timestamp"] = trade["timestamp"].isoformat()  # Tarihi ISO formatına çevirin
            serialized_history.append(serialized_trade)
        return serialized_history

# Fiyat Güncelleme
def update_price_history(symbol, interval, days):
    start_time = datetime.now(timezone.utc) - timedelta(days=days)
    klines = client.get_historical_klines(symbol, interval, start_str=str(start_time))
    df = pd.DataFrame(klines, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ])
    df["Close"] = pd.to_numeric(df["Close"])
    df["Date"] = pd.to_datetime(df["Open Time"], unit="ms")
    df.set_index("Date", inplace=True)
    return df[["Close", "High", "Low"]]


def buy_process(curr_price, indicator):
    global eth_coins, balance, state
    num_coins_to_buy = balance / curr_price
    eth_coins += num_coins_to_buy
    balance -= num_coins_to_buy * curr_price
    logging.info("BUY PROCESS")
    log_trade("Buy", curr_price, num_coins_to_buy, indicator)
    state = 1

    
def sell_process(curr_price, indicator):
    global eth_coins, balance, state
    profit = eth_coins * curr_price
    logging.info("SELL PROCESS")
    log_trade("Sell", curr_price, eth_coins, indicator)
    balance += profit
    eth_coins = 0
    logging.info(f"Profit: {profit - INITIAL_BALANCE}")
    state = 0

# Ticaret Döngüsü
def start_trading(coin, indicator, upper, lower, interval):
    print(f"----------")
    print(f"Trading started for {coin} with interval {interval}, Indicator: {indicator}, Lower Limit: {lower}, Upper Limit: {upper}")
    print(f"----------")

    with lock:
        if coin not in trades:
            trades[coin] = []  # Yeni coin için trade listesi oluştur

        try:
            lower = float(lower)
            upper = float(upper)

            while True:  # Sonsuz döngü
                coin_pair = f"{coin}USDT"  # USDT çifti
                df = update_price_history(coin_pair, interval, 1)
                close_prices = df["Close"]
                curr_price = close_prices.iloc[-1]

                if indicator == "RSI":
                    rsi = compute_rsi(close_prices.values, RSI_PERIOD)
                    print(f"RSI for {coin}: {rsi}")
                    if state == 0 and rsi < lower:
                        print("RSI: BUY signal triggered")
                        buy_process(curr_price, indicator)
                        trades[coin].append({"action": "BUY", "price": curr_price})
                    elif state == 1 and rsi > upper:
                        print("RSI: SELL signal triggered")
                        sell_process(curr_price, indicator)
                        trades[coin].append({"action": "SELL", "price": curr_price})
                    else:
                        log_hold_state(curr_price, indicator)

                elif indicator == "MACD":
                    macd, macd_signal = compute_macd(close_prices)
                    print(f"MACD for {coin}: {macd}, Signal: {macd_signal}")
                    if state == 0 and macd > macd_signal:
                        print("MACD: BUY signal triggered")
                        buy_process(curr_price, indicator)
                        trades[coin].append({"action": "BUY", "price": curr_price})
                    elif state == 1 and macd < macd_signal:
                        print("MACD: SELL signal triggered")
                        sell_process(curr_price, indicator)
                        trades[coin].append({"action": "SELL", "price": curr_price})
                    else:
                        log_hold_state(curr_price, indicator)

                elif indicator == "Bollinger":
                    upper_band, lower_band = compute_bollinger_bands(df)
                    print(f"Bollinger Bands for {coin}: Lower {lower_band}, Upper {upper_band}")
                    if state == 0 and curr_price <= lower_band:
                        print("Bollinger: BUY signal triggered")
                        buy_process(curr_price, indicator)
                        trades[coin].append({"action": "BUY", "price": curr_price})
                    elif state == 1 and curr_price >= upper_band:
                        print("Bollinger: SELL signal triggered")
                        sell_process(curr_price, indicator)
                        trades[coin].append({"action": "SELL", "price": curr_price})
                    else:
                        log_hold_state(curr_price, indicator)

                logging.info(f"Trading Status: Current Price: {curr_price} | Indicator: {indicator}")

                # Belirli bir süre bekle (örneğin, 10 saniye)
                time.sleep(10)

        except Exception as e:
            print(f"Error in trading: {e}")

