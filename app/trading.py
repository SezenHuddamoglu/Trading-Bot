import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime, timedelta, timezone
import threading
import logging
from typing import Dict, List
import time
from app.indicator_functions import compute_stochastic_rsi,compute_ichimoku,compute_rsi,compute_macd,compute_ema,compute_ma,compute_bollinger_bands,compute_adx,compute_vwap,compute_cci

# Logger yapılandırması
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Binance API bilgileri (çevresel değişkenlerden alınmalı)
api_key = "v7d1l6s5reAT0vJViQTzoGup1J1M9zAo1VhxH0HbYEPY3UEVTD8cYk0ooGSj2IB8"
secret_key = "v0UTEbZvUY3wYvCHiewRka8tcRoit9FanJTyO1bd2C5ax6tWJZa8LkZjtObbtV6c"


client = Client(api_key=api_key, api_secret=secret_key)
# Ticaret parametreleri
INITIAL_BALANCE = 10000  # Başlangıç bakiyesi
LOSS_THRESHOLD = 0.90  # Zarar durdurma eşiği
TRADE_INTERVALS = ["1m", "5m", "15m", "30m", "1h"]
balance = INITIAL_BALANCE
eth_coins = 0
trade_history = {}
price_history = {}
lock = threading.Lock()
coin_states = {}  # Her coin için state saklanacak
stop_signals = {}




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
      #print(f"Trading started for {coin} with interval {interval}, Indicator: {indicator}, Lower Limit: {lower}, Upper Limit: {upper}")
    
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
                RSI_PERIOD = 14
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

            elif indicator == "Bollinger Bands":
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
                    
            elif indicator == "Moving Average":
                period=upper
                ma = compute_ma(close_prices.values, period)
                print(f"MA for {coin}: {ma}")
                if coin_states[coin] == 0 and curr_price > ma:
                    print("MA: BUY signal triggered")
                    buy_process(curr_price, indicator, coin)
                elif coin_states[coin] == 1 and curr_price < ma:
                    print("MA: SELL signal triggered")
                    sell_process(curr_price, indicator, coin)
                else:
                    log_hold_state(curr_price, indicator)

            elif indicator == " Exponential Moving Average":
                period=upper
                ema = compute_ema(close_prices.values, period)
                print(f"EMA for {coin}: {ema}")
                if coin_states[coin] == 0 and curr_price > ema:
                    print("EMA: BUY signal triggered")
                    buy_process(curr_price, indicator, coin)
                elif coin_states[coin] == 1 and curr_price < ema:
                    print("EMA: SELL signal triggered")
                    sell_process(curr_price, indicator, coin)
                else:
                    log_hold_state(curr_price, indicator)
                    
            # elif indicator == "Ichimoku Cloud":
            #     conv, base, span_a, span_b = compute_ichimoku(
            #         close_prices.values, high_prices.values, low_prices.values
            #     )
            #     print(f"Ichimoku for {coin}: Conversion: {conv}, Base: {base}, Span A: {span_a}, Span B: {span_b}")
            #     if coin_states[coin] == 0 and curr_price > max(span_a, span_b):
            #         print("Ichimoku: BUY signal triggered")
            #         buy_process(curr_price, indicator, coin)
            #     elif coin_states[coin] == 1 and curr_price < min(span_a, span_b):
            #         print("Ichimoku: SELL signal triggered")
            #         sell_process(curr_price, indicator, coin)
            #     else:
            #         log_hold_state(curr_price, indicator)
                    
                    
            elif indicator == "Stochastic RSI":
                #period değişkeni alınacak
                STOCH_RSI_PERIOD=14
                stoch_rsi = compute_stochastic_rsi(close_prices.values, STOCH_RSI_PERIOD)
                print(f"Stochastic RSI for {coin}: {stoch_rsi}")
                if coin_states[coin] == 0 and stoch_rsi < lower:
                    print("Stochastic RSI: BUY signal triggered")
                    buy_process(curr_price, indicator, coin)
                elif coin_states[coin] == 1 and stoch_rsi > upper:
                    print("Stochastic RSI: SELL signal triggered")
                    sell_process(curr_price, indicator, coin)
                else:
                    log_hold_state(curr_price, indicator)
                    
            elif indicator == "Average Directional Index":
                adx = compute_adx(high_prices.values, low_prices.values, close_prices.values)
                print(f"ADX for {coin}: {adx}")
                if coin_states[coin] == 0 and adx > upper:
                    print("ADX: BUY signal triggered")
                    buy_process(curr_price, indicator, coin)
                elif coin_states[coin] == 1 and adx < lower:
                    print("ADX: SELL signal triggered")
                    sell_process(curr_price, indicator, coin)
                else:
                    log_hold_state(curr_price, indicator)
                    
                    
            elif indicator == "CCI":
                cci = compute_cci(high_prices.values, low_prices.values, close_prices.values)
                print(f"CCI for {coin}: {cci}")
                if coin_states[coin] == 0 and cci < lower:
                    print("CCI: BUY signal triggered")
                    buy_process(curr_price, indicator, coin)
                elif coin_states[coin] == 1 and cci > upper:
                    print("CCI: SELL signal triggered")
                    sell_process(curr_price, indicator, coin)
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
