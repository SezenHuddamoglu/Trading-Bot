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
api_key = "v7d1l6s5reAT0vJViQTzoGup1J1M9zAo1VhxH0HbYEPY3UEVTD8cYk0ooGSj2IB8"
secret_key = "v0UTEbZvUY3wYvCHiewRka8tcRoit9FanJTyO1bd2C5ax6tWJZa8LkZjtObbtV6c"
testnet = True

client = Client(api_key=api_key, api_secret=secret_key)

symbol = "ETHUSDT"
bar_length = "5m"
g_symbol = "ETHUSDT"

now = datetime.now(timezone.utc)
historical_days = 60
past = str(now - timedelta(days=historical_days))

# Verilerin saklanacağı listeler
price_history = []
trade_history: List[Trade] = []
current_prices: List[CoinPrice] = []

bars = client.get_historical_klines(symbol=symbol, interval=bar_length, start_str=past, end_str=str(now))

df = pd.DataFrame(bars)
df["Date"] = pd.to_datetime(df.iloc[:, 0], unit="ms")
df.columns = ["Open Time", "Open", "High", "Low", "Close", "Volume",
              "Clos Time", "Quote Asset Volume", "Number of Trades",
              "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore", "Date"]
df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
df.set_index("Date", inplace=True)

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
    
    down_chg[diff < 0] = diff[diff < 0]

    up_chg = pd.DataFrame(up_chg)
    down_chg = pd.DataFrame(down_chg)
    
    up_chg_avg = up_chg.ewm(com=time_window - 1, min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window - 1, min_periods=time_window).mean()
    
    rs = abs(up_chg_avg / down_chg_avg)
    rsi = 100 - 100 / (1 + rs)
    rsi = int(rsi[0].iloc[-1])
    return rsi

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
    global balance  # Global balance değişkenini kullanıyoruz
    trade = Trade(
        action=action,
        price=price,
        amount=amount,
        timestamp=datetime.now(timezone.utc),
        indicator=indicator,
        deposit=balance  # Balance'ı yeni alan olarak ekleyin
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

def start_trading():
    global balance, eth_coins, stop_trading, state, total_profit
    while True:
        for interval in ['1m','5m', '15m','30m','45m','1h']:
            if stop_trading:
                logging.info("Trading stopped due to significant losses.")
                break  # Döngüyü kırarak ticareti durdur

            try:
                price = client.get_symbol_ticker(symbol=g_symbol)
                curr_price = float(price['price'])  # Güncel fiyat
                curr_time = datetime.now(timezone.utc)
                
                with data_lock:
                    price_history.append((curr_time, curr_price))
                
                logging.info(f"Interval: {interval} | Current Price: {curr_price} | Time: {curr_time}")

                
                """df = pd.DataFrame(klines, columns=["Open Time", "Open", "High", "Low", "Close", "Volume",
                                                "Close Time", "Quote Asset Volume", "Number of Trades",
                                                "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"])
                df["Date"] = pd.to_datetime(df["Open Time"], unit="ms")
                df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
                df.set_index("Date", inplace=True) """

                for column in df.columns:
                    df[column] = pd.to_numeric(df[column], errors="coerce")

                klines = client.get_historical_klines(symbol=g_symbol, interval=bar_length, start_str=str(datetime.now(timezone.utc) - timedelta(days=60)), end_str=str(datetime.now(timezone.utc)))
                close_prices = df['Close'].values
                
                rsi = computeRSI(close_prices, 14)
                macd_signal = MACD(bar_length, g_symbol)
                supertrend_signal = computeSupertrend(df)
                upper_band, lower_band = computeBollingerBands(df)

                logging.info(f'RSI: {rsi}, MACD: {macd_signal}, Supertrend: {supertrend_signal}, Bollinger Upper: {upper_band}, Bollinger Lower: {lower_band}')
                logging.info(f'------------------------')
                eth_value = eth_coins * curr_price 
                total_portfolio_value = balance + eth_value  

                # Zararı durdur kontrolü
                if total_portfolio_value < initial_balance * loss_threshold:
                    stop_trading = True 
                    logging.info(f"Significant loss detected. Current portfolio value: {total_portfolio_value}. Stopping trading.")
                    break  

                # Ticaret kararları
                if state == 0:
                    if (rsi < 60 or macd_signal == 'BUY' or curr_price <= lower_band ):
                        print("balancebuy ",balance)
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
                    if (rsi > 70 or macd_signal == 'SELL' or curr_price >= upper_band ):
                        
                        profit = (eth_coins * curr_price) - balance 
                        balance += eth_coins * curr_price  
                        
                        if rsi > 55:
                            indicator = "RSI-based"
                        elif curr_price >= upper_band:
                            indicator = "Bollinger Band-based"
                        else:
                            indicator = "MACD-based"
                            
                        log_trade("Sell", curr_price, eth_coins, indicator)    
                        logging.info(f"SELL: RSI: {rsi} | MACD: {macd_signal} | Price: {curr_price} | Indicator: {indicator}")
                        logging.info(f"Profit: {profit}")
                        eth_coins = 0  

                        state = 0 

                elif float(curr_price) < stopLoss(g_symbol):
                    stop_trading = True  # 'STOPLOSS'
                    state = -1
                    log_trade("Stoploss", curr_price, eth_coins, "Stoploss")
                    logging.info(f"STOPLOSS triggered at price: {curr_price}")
                    break
                
                else:
                    indicator="HOLD"
                    log_trade("Hold", curr_price, eth_coins, indicator)    

                # Anlık fiyatları güncelle
                update_current_prices()
                
                print(f"Current Balance: {balance} USDT, ETH Owned: {eth_coins}")

                # Frontend için veri güncellemeleri
                time.sleep(10 * 1) if bar_length == '5m' else time.sleep(10 * 5)
        
            except Exception as e:
                logging.error(f"Error in trading loop: {e}")
                time.sleep(10)  # Hata durumunda bekleme süresi