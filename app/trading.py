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
API_KEY = "v7d1l6s5reAT0vJViQTzoGup1J1M9zAo1VhxH0HbYEPY3UEVTD8cYk0ooGSj2IB8"
SECRET_KEY  = "v0UTEbZvUY3wYvCHiewRka8tcRoit9FanJTyO1bd2C5ax6tWJZa8LkZjtObbtV6c"
TESTNET = True
client = Client(api_key=API_KEY, api_secret=SECRET_KEY)

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
    with data_lock:
        return [trade.dict() for trade in trade_history]
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

# Ticaret Döngüsü
def start_trading(coin, indicator, upper, lower, interval):
    print(f"----------")
    print(f"----------")
   
    print(f"Trading started for {coin} with interval {interval}, Indicator: {indicator}, Lower Limit: {lower}, Upper Limit: {upper}")
   
    print(f"----------")
    print(f"----------")

    try:
        # Modify the coin symbol to match the trading pair format (e.g., ETHUSDT)
        coin_pair = f"{coin}USDT"  # Assuming you want to trade against USDT (modify if using a different pair)

        # Fiyat verisini alın
        df = update_price_history(coin_pair, interval, 1)  # 1 günlük veri
        close_prices = df["Close"]

        # Seçilen indikatöre göre işlem yap
        if indicator == "RSI":
            rsi = compute_rsi(close_prices.values, RSI_PERIOD)
            print(f"RSI for {coin}: {rsi}")
            if rsi < lower:
                print("RSI: BUY signal triggered")
            elif rsi > upper:
                print("RSI: SELL signal triggered")

        elif indicator == "MACD":
            macd, macd_signal = compute_macd(close_prices)
            print(f"MACD for {coin}: {macd}, Signal: {macd_signal}")
            if macd > macd_signal:
                print("MACD: BUY signal triggered")
            elif macd < macd_signal:
                print("MACD: SELL signal triggered")

        elif indicator == "Bollinger":
            upper_band, lower_band = compute_bollinger_bands(df)
            current_price = close_prices.iloc[-1]
            print(f"Bollinger Bands for {coin}: Lower {lower_band}, Upper {upper_band}")
            if current_price <= lower_band:
                print("Bollinger: BUY signal triggered")
            elif current_price >= upper_band:
                print("Bollinger: SELL signal triggered")

        else:
            print(f"Unknown indicator: {indicator}")
    except Exception as e:
        print(f"Error in trading: {e}")


