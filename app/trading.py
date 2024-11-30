import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime, timedelta, timezone
import threading
import logging
from typing import Dict, List
import time

# Logger yapılandırması
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Binance API bilgileri (çevresel değişkenlerden alınmalı)
api_key = "v7d1l6s5reAT0vJViQTzoGup1J1M9zAo1VhxH0HbYEPY3UEVTD8cYk0ooGSj2IB8"
secret_key = "v0UTEbZvUY3wYvCHiewRka8tcRoit9FanJTyO1bd2C5ax6tWJZa8LkZjtObbtV6c"


client = Client(api_key=api_key, api_secret=secret_key)
# Ticaret parametreleri
INITIAL_BALANCE = 10000  # Başlangıç bakiyesi
LOSS_THRESHOLD = 0.90  # Zarar durdurma eşiği
RSI_PERIOD = 14
TRADE_INTERVALS = ["1m", "5m", "15m", "30m", "1h"]
balance = INITIAL_BALANCE
eth_coins = 0
trade_history = {}
price_history = {}
lock = threading.Lock()
coin_states = {}  # Her coin için state saklanacak
stop_signals = {}

def perform_backtest(data, initial_balance, indicator_type, lower_limit, upper_limit, interval):
    """
    Çoklu coin ve indikatörlere göre backtest fonksiyonu.
    """
    balance = initial_balance
    coins = 0
    trades = []
    state = 0  # 0: No position, 1: Holding coins

    # Veriyi belirli interval ile yeniden örnekleme
    data = data.resample(interval).mean()  # Örneğin '1h', '15m' gibi

    for i in range(len(data) - 1):
        current_price = data['Close'].iloc[i]
        indicator_value = None

        # Seçilen indikatöre göre değer hesaplama
        if indicator_type == "RSI":
            recent_data = data['Close'].iloc[max(0, i-14):i+1]
            indicator_value = compute_rsi(recent_data, 14)  # RSI hesaplama fonksiyonu
        elif indicator_type == "MACD":
            macd, signal = compute_macd(data['Close'].iloc[:i+1])
            indicator_value = macd - signal
        elif indicator_type == "Bollinger":
            sma, upper_band, lower_band = compute_bollinger_bands(data['Close'].iloc[:i+1])
            indicator_value = (current_price - sma) / (upper_band - lower_band)

        # İşlem mantığı
        if state == 0 and indicator_value is not None and indicator_value < lower_limit:  # BUY sinyali
            coins = balance / current_price
            balance -= coins * current_price
            trades.append({"action": "BUY", "price": current_price, "balance": balance, "indicator_value": indicator_value})
            state = 1
        elif state == 1 and indicator_value is not None and indicator_value > upper_limit:  # SELL sinyali
            balance += coins * current_price
            coins = 0
            trades.append({"action": "SELL", "price": current_price, "balance": balance, "indicator_value": indicator_value})
            state = 0

    # Son bakiye
    final_balance = balance + coins * data['Close'].iloc[-1]
    return {"trades": trades, "final_balance": final_balance}

def load_historical_data(symbol, interval, start_date):
    klines = client.get_historical_klines(symbol, interval, start_date)
    df = pd.DataFrame(klines, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ])
    df["Close"] = pd.to_numeric(df["Close"])
    df["Date"] = pd.to_datetime(df["Open Time"], unit="ms")
    df.set_index("Date", inplace=True)
    return df

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
def log_trade(action, price, amount, indicator, coin):
    global balance
    with lock:
        trade = {
            "action": action,
            "price": price,
            "amount": amount,
            "timestamp": datetime.now(timezone.utc),
            "indicator": indicator,
            "balance": balance,
            "coin": coin
        }
        if coin not in trade_history:
            trade_history[coin] = []
        trade_history[coin].append(trade)
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
    
def get_trade_history(coin=None):
    with lock:
        if coin:
            return trade_history.get(coin, [])
        return trade_history



# Global stop flags
stop_flags = {}

def reset_trades(coin):
    """Belirli bir coin için işlem geçmişini sıfırla ve önceki işlemi durdur."""
    if coin in stop_flags:
        stop_flags[coin] = True  # Önceki işlemi durdur
    stop_flags[coin] = False    # Yeni işlem için durdurmayı kapat


threads = {}
# Ticaret Döngüsü
def start_trading(coin, indicator, upper, lower, interval):
    global stop_flags, threads
    if coin not in coin_states:
        coin_states[coin] = 0 
    # Eski iş parçacığını durdur
    if coin in threads and threads[coin].is_alive():
        stop_flags[coin] = True  # Durdurma sinyalini ayarla
        threads[coin].join()  # Eski iş parçacığını sonlandır

    # Yeni işlem için durdurma sinyalini sıfırla ve iş parçacığını başlat
    stop_flags[coin] = False
    threads[coin] = threading.Thread(target=trading_loop, args=(coin, indicator, upper, lower, interval))
    threads[coin].start()
    print(f"----------")
    print(f"Trading started for {coin} with interval {interval}, Indicator: {indicator}, Lower Limit: {lower}, Upper Limit: {upper}")
    print(f"----------")

def trading_loop(coin, indicator, upper, lower, interval):
      """Asıl işlem döngüsü."""
      print(f"Trading started for {coin} with interval {interval}, Indicator: {indicator}, Lower Limit: {lower}, Upper Limit: {upper}")
    
      try:
        lower = float(lower)
        upper = float(upper)

        while not stop_flags[coin]: # Sonsuz döngü
            
            print(f"Trading started for {coin} with interval {interval}, Indicator: {indicator}, Lower Limit: {lower}, Upper Limit: {upper}")
            coin_pair = f"{coin}USDT"  # USDT çifti
            df = update_price_history(coin_pair, interval, 1)
            close_prices = df["Close"]
            curr_price = close_prices.iloc[-1]
            #print(f'state', coin_states[coin] == 0 )

            if indicator == "RSI":
                rsi = compute_rsi(close_prices.values, RSI_PERIOD)
                print(f"RSI for {coin}: {rsi}")
                if coin_states[coin]== 0 and rsi < lower:
                    print("RSI: BUY signal triggered")
                    buy_process(curr_price, indicator,coin)
                elif coin_states[coin] == 1 and rsi > upper:
                    print("RSI: SELL signal triggered")
                    sell_process(curr_price, indicator,coin)
                else:
                    log_hold_state(curr_price, indicator)

            elif indicator == "MACD":
                macd, macd_signal = compute_macd(close_prices)
                print(f"MACD for {coin}: {macd}, Signal: {macd_signal}")
                if coin_states[coin] == 0 and macd > macd_signal:
                    print("MACD: BUY signal triggered")
                    buy_process(curr_price, indicator,coin)
                elif coin_states[coin] == 1 and macd < macd_signal:
                    print("MACD: SELL signal triggered")
                    sell_process(curr_price, indicator,coin)
                else:
                    log_hold_state(curr_price, indicator)

            elif indicator == "Bollinger":
                upper_band, lower_band = compute_bollinger_bands(df)
                print(f"Bollinger Bands for {coin}: Lower {lower_band}, Upper {upper_band}")
                if coin_states[coin]== 0 and curr_price <= lower_band:
                    print("Bollinger: BUY signal triggered")
                    buy_process(curr_price, indicator,coin)
                elif coin_states[coin]== 1 and curr_price >= upper_band:
                    print("Bollinger: SELL signal triggered")
                    sell_process(curr_price, indicator,coin)
                else:
                    log_hold_state(curr_price, indicator)

            logging.info(f"Trading Status: Current Price: {curr_price} | Indicator: {indicator}")

            # Belirli bir süre bekle (örneğin, 10 saniye)
            time.sleep(10)

      except Exception as e:
        print(f"Error in trading: {e}")

def get_price_data(coin, interval="5m"):
    klines = client.get_historical_klines(f"{coin}USDT", interval, "1 day ago UTC")
    df = pd.DataFrame(klines, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ])
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")  # dtype dönüşümünü kontrol et
    df.dropna(subset=["Close"], inplace=True) #Bozuk olanları çıkart.
    df["Date"] = pd.to_datetime(df["Open Time"], unit="ms")
    df.set_index("Date", inplace=True)
    return df


def update_price_history(symbol, interval="5m", days=1):
    """Fiyat geçmişini güncelle."""
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


def buy_process(curr_price, indicator, coin):
    global balance, eth_coins
    num_coins_to_buy = balance / curr_price
    eth_coins += num_coins_to_buy
    balance = 0  # Tüm bakiyeyi kullandık
    log_trade("Buy", curr_price, num_coins_to_buy, indicator, coin)
    coin_states[coin] = 1  # Satış bekleniyor

def sell_process(curr_price, indicator, coin):
    global balance, eth_coins
    profit = eth_coins * curr_price
    log_trade("Sell", curr_price, eth_coins, indicator, coin)
    balance += profit
    eth_coins = 0
    coin_states[coin] = 0  # Alım bekleniyor

