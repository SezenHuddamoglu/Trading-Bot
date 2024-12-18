import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime, timedelta, timezone
import threading
import logging
from typing import Dict, List
import time
from app.indicator_functions import (
    compute_stochastic_rsi, 
    compute_rsi, 
    compute_macd, 
    compute_ema, 
    compute_ma, 
    compute_adx, 
    compute_vwap, 
    compute_cci
)
from app.models import Trade

# Configure logging to display messages with timestamps
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Binance API keys (replace with your actual keys)
api_key = ""
secret_key = ""

# Initialize Binance client with API keys
client = Client(api_key=api_key, api_secret=secret_key)

# Initial balance in USD
INITIAL_BALANCE = 10000  

balance = INITIAL_BALANCE  # Current balance in USD
eth_coins = 0  # Amount of Ethereum coins owned
trade_history = {}  # History of all trades
price_history = {}  # Historical price data for each coin
lock = threading.Lock()  # Lock to ensure thread safety
coin_states = {}  # Keeps track of each coin's state (buy/sell)
stop_flags = {}  # Flags to stop trading threads
coin_data = {} 

# Record a trade (buy/sell)
def log_trade(action, price, amount, indicator, coin, balance):
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

# Log the hold state when no trade is executed
def log_hold_state(curr_price, indicator):
    print(f"HOLD: Current Price: {curr_price:.2f} | Indicator: {indicator}")
    logging.info(f"HOLD: Current Price: {curr_price:.2f} | Indicator: {indicator}")

# Fetch current prices of specified coins from Binance API
def get_current_prices(target_coins):
    """
    Retrieve current prices and change percentages for the given coins from Binance.
    """
    all_tickers = client.get_ticker()
    filtered_data = [
        {
            "symbol": ticker["symbol"].replace("USDT", ""),
            "price": float(ticker["lastPrice"]),
            "change": float(ticker["priceChangePercent"]) / 100
        }
        for ticker in all_tickers
        if ticker["symbol"] in [f"{coin}USDT" for coin in target_coins]
    ]
    return filtered_data

# Retrieve trade history, optionally filtered by coin
def get_trade_history(coin=None):
    with lock:
        if coin:
            return trade_history.get(coin, [])
        return trade_history

# Reset trade history and stop any ongoing trade for a specific coin
def reset_trades(coin):
    if coin in stop_flags:
        stop_flags[coin] = True  # Stop previous trading loop
    stop_flags[coin] = False  # Reset stop flag for new trading

threads = {}  # Dictionary to manage trading threads

# Start a trading loop for a specific coin
def start_trading(coin, indicator, upper, lower, interval):
    global stop_flags, threads, coin_data
    if coin not in coin_states:
        coin_states[coin] = 0  # Initialize coin state
    if coin not in coin_data:
        coin_data[coin] = {'balance': balance, 'amount': 0}  # Örneğin 1000 USDT ile başlatılıyor


    # Stop any existing thread for this coin
    if coin in threads and threads[coin].is_alive():
        stop_flags[coin] = True  # Signal to stop
        threads[coin].join()

    # Reset stop flag and start a new trading thread
    stop_flags[coin] = False
    threads[coin] = threading.Thread(target=trading_loop, args=(coin, indicator, upper, lower, interval))
    threads[coin].start()
    print(f"----------\nTrading started for {coin} with interval {interval}, Indicator: {indicator}, Lower Limit: {lower}, Upper Limit: {upper}\n----------")

# Trading loop function, executed in a separate thread
def trading_loop(coin, indicator, upper, lower, interval):
    """Main trading loop."""
    try:
        lower = float(lower)
        upper = float(upper)

        while not stop_flags[coin]:  # Loop until stop signal
            coin_pair = f"{coin}USDT"
            df = update_price_history(coin_pair, interval, 1)
            close_prices = df["Close"]
            high_prices = df["High"]
            low_prices = df["Low"]
            volumes = df["Volume"]
            curr_price = close_prices.iloc[-1]

            # Trading logic based on selected indicator
            if indicator == "RSI":
                RSI_PERIOD = 14
                rsi = compute_rsi(close_prices.values, RSI_PERIOD)
                if coin_states[coin] == 0 and rsi < lower:
                    print("RSI: BUY signal triggered")
                    buy_process(curr_price, indicator, coin)
                elif coin_states[coin] == 1 and rsi > upper:
                    print("RSI: SELL signal triggered")
                    sell_process(curr_price, indicator, coin)
                else:
                    log_hold_state(curr_price, indicator)


            elif indicator == "MACD":
                # Calculate MACD and signal line
                macd, macd_signal = compute_macd(close_prices)
                print(f"MACD for {coin}: {macd}, Signal: {macd_signal}")
                if coin_states[coin] == 0 and macd > macd_signal:
                    print("MACD: BUY signal triggered")
                    buy_process(curr_price, indicator,coin)
                elif coin_states[coin] == 1 and macd < macd_signal:
                    print("MACD: SELL signal triggered")
                    sell_process(curr_price, indicator, coin)
                    
                # Otherwise, log HOLD state
                else:
                    log_hold_state(curr_price, indicator)

            elif indicator == "Moving Average":
                # Calculate simple moving average (SMA)
                period = upper
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

            elif indicator == "Exponential Moving Average":
                # Calculate exponential moving average (EMA)
                ema = compute_ema(close_prices.values, upper)
                print(f"EMA for {coin}: {ema}")
                if coin_states[coin] == 0 and curr_price > ema:
                    print("EMA: BUY signal triggered")
                    buy_process(curr_price, indicator, coin)
                elif coin_states[coin] == 1 and curr_price < ema:
                    print("EMA: SELL signal triggered")
                    sell_process(curr_price, indicator, coin)
                else:
                    log_hold_state(curr_price, indicator)

            elif indicator == "Stochastic RSI":
                # Calculate Stochastic RSI
                STOCH_RSI_PERIOD = 14
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
                # Calculate ADX
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

            elif indicator == "Volume Weighted Average Price":
                # Calculate VWAP
                vwap = compute_vwap(close_prices, volumes).iloc[-1]
                print(f"VWAP for {coin}: {vwap}")
                if coin_states[coin] == 0 and curr_price < lower * vwap:
                    print("VWAP: BUY signal triggered")
                    buy_process(curr_price, indicator, coin)
                elif coin_states[coin] == 1 and curr_price > upper * vwap:
                    print("VWAP: SELL signal triggered")
                    sell_process(curr_price, indicator, coin)
                else:
                    log_hold_state(curr_price, indicator)

            elif indicator == "Commodity Channel Index":
                # Calculate CCI
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

            # Log trading status
            logging.info(f"Trading Status: Current Price: {curr_price} | Indicator: {indicator} | Deposit: {balance}")

            # Wait for 10 seconds before the next iteration
            time.sleep(10)

    except Exception as e:
        # Handle and log errors during trading
        print(f"Error in trading: {e}")

# Functions for fetching and processing price data
def get_price_data(coin, interval="5m"):
    # Fetch historical price data for the given coin and interval
    klines = client.get_historical_klines(f"{coin}USDT", interval, "1 day ago UTC")
    df = pd.DataFrame(klines, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ])
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")  # Convert 'Close' to numeric
    df.dropna(subset=["Close"], inplace=True)  # Remove rows with missing data
    df["Date"] = pd.to_datetime(df["Open Time"], unit="ms")  # Convert timestamp to datetime
    df.set_index("Date", inplace=True)  # Set datetime as index
    return df

def update_price_history(symbol, interval="5m", days=1):
    # Update price history for the given symbol and interval
    start_time = datetime.now(timezone.utc) - timedelta(days=days)
    klines = client.get_historical_klines(symbol, interval, start_str=str(start_time))
    df = pd.DataFrame(klines, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ])
    df["Close"] = pd.to_numeric(df["Close"])
    df["High"] = pd.to_numeric(df["High"])
    df["Low"] = pd.to_numeric(df["Low"])
    df["Volume"] = pd.to_numeric(df["Volume"])
    df["Date"] = pd.to_datetime(df["Open Time"], unit="ms")
    df.set_index("Date", inplace=True)
    return df[["Close", "High", "Low", "Volume"]]

# Functions to handle buy and sell processes
def buy_process(curr_price, indicator, coin):
    global coin_data  

    
    coin_balance = coin_data[coin]['balance']
    coin_amount = coin_data[coin]['amount']

    num_coins_to_buy = coin_balance / curr_price
    coin_data[coin]['amount'] += num_coins_to_buy  
    coin_data[coin]['balance'] = 0  # Use entire balance for purchase
 
    log_trade("Buy", curr_price, num_coins_to_buy, indicator, coin, coin_data[coin]['balance'])
    coin_states[coin] = 1   # Waiting for SELL signal

def sell_process(curr_price, indicator, coin):
    global coin_data  

   
    coin_balance = coin_data[coin]['balance']
    coin_amount = coin_data[coin]['amount']

  
    profit = coin_amount * curr_price
    coin_data[coin]['balance'] += profit  
    coin_data[coin]['amount'] = 0  
    log_trade("Sell", curr_price, coin_data[coin]['amount'], indicator, coin, coin_data[coin]['balance'])
    coin_states[coin] = 0  # Waiting for BUY signal



def backtest_strategy(coin, indicator, upper, lower, interval, balance):
    """
    Perform a backtest for a given coin and strategy using various indicators.
    """
    print(f"Backtest started for {coin} with interval {interval}, Indicator: {indicator}, Lower Limit: {lower}, Upper Limit: {upper}, Initial Balance {balance}")

    symbol = f"{coin}USDT"
    df = update_price_history(symbol, interval, days=120)  # Fetch historical data for 120 days
    
    # Check if the data is valid
    if df is None or df.empty:
        raise ValueError("Price history could not be retrieved or is empty.")
    
    # Ensure required columns are present in the dataframe
    if not all(col in df.columns for col in ["Close", "High", "Low"]):
        raise ValueError("Required columns are missing in the data.")
    
    close_prices = df["Close"]
    high_prices = df["High"]
    low_prices = df["Low"]
    
    trades = []  # List to store trades made during the backtest
    state = 0  # 0: Waiting for Buy, 1: Waiting for Sell
    initial_balance = balance
    coins_held = 0
    
    for i in range(len(close_prices)):
        curr_price = close_prices.iloc[i]  # Current closing price
        curr_time = df.index[i]  # Current timestamp
        
        # Apply different indicators for backtesting
        if indicator == "RSI":
            # Skip the first 14 days (insufficient data for RSI)
            if i < 14:
                continue
            rsi = compute_rsi(close_prices[:i+1], 14)  # Compute RSI for the current window of data
            if state == 0 and rsi < lower:  # Buy when RSI is below lower threshold
                trade = buyBacktest(curr_price, initial_balance, indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                coins_held = trade.amount
                initial_balance = 0  # Use all balance to buy coins
                state = 1  # Now waiting to sell
            elif state == 1 and rsi > upper:  # Sell when RSI is above upper threshold
                trade = sellBacktest(curr_price, coins_held, indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                initial_balance = trade.deposit  # Update balance from the sale
                coins_held = 0
                state = 0  # Now waiting to buy
        
        elif indicator == "MACD":
            # Skip the first 26 days (insufficient data for MACD)
            if i < 26:
                continue
            macd, signal_line = compute_macd(close_prices[:i+1])  # Compute MACD
            if state == 0 and macd > signal_line:  # Buy when MACD crosses above signal line
                trade = buyBacktest(curr_price, initial_balance, indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                coins_held = trade.amount
                initial_balance = 0  # Use all balance to buy coins
                state = 1  # Now waiting to sell
            elif state == 1 and macd < signal_line:  # Sell when MACD crosses below signal line
                trade = sellBacktest(curr_price, coins_held, indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                initial_balance = trade.deposit  # Update balance from the sale
                coins_held = 0
                state = 0  # Now waiting to buy
        
        # Implement backtest logic for other indicators in a similar way
        elif indicator == "Moving Average":
            if i < 20:
                continue
            upper = int(upper)
            ma = compute_ma(close_prices[:i+1], upper)  # Compute Moving Average
            if state == 0 and curr_price > ma:  # Buy when current price is above Moving Average
                trade = buyBacktest(curr_price, initial_balance, indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                coins_held = trade.amount
                initial_balance = 0  # Use all balance to buy coins
                state = 1
            elif state == 1 and curr_price < ma:  # Sell when current price is below Moving Average
                trade = sellBacktest(curr_price, coins_held, indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                initial_balance = trade.deposit  # Update balance from the sale
                coins_held = 0
                state = 0
        
        elif indicator == "Exponential Moving Average":
            if i < 20:
                continue
            ema = compute_ema(close_prices[:i+1], upper)  # Compute Exponential Moving Average
            if state == 0 and curr_price > ema:  # Buy when current price is above EMA
                trade = buyBacktest(curr_price, initial_balance, indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                coins_held = trade.amount
                initial_balance = 0  # Use all balance to buy coins
                state = 1
            elif state == 1 and curr_price < ema:  # Sell when current price is below EMA
                trade = sellBacktest(curr_price, coins_held, indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                initial_balance = trade.deposit  # Update balance from the sale
                coins_held = 0
                state = 0
        
        elif indicator == "Stochastic RSI":
            if i < 14:
                continue
            stoch_rsi = compute_stochastic_rsi(close_prices[:i+1], 14)  # Compute Stochastic RSI
            if state == 0 and stoch_rsi < lower:  # Buy when Stochastic RSI is below lower threshold
                trade = buyBacktest(curr_price, initial_balance, indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                coins_held = trade.amount
                initial_balance = 0  # Use all balance to buy coins
                state = 1
            elif state == 1 and stoch_rsi > upper:  # Sell when Stochastic RSI is above upper threshold
                trade = sellBacktest(curr_price, coins_held, indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                initial_balance = trade.deposit  # Update balance from the sale
                coins_held = 0
                state = 0
        
        elif indicator == "Average Directional Index":
            if i < 14:
                continue
            adx = compute_adx(high_prices[:i+1], low_prices[:i+1], close_prices[:i+1], 14)  # Compute ADX
            if state == 0 and adx > upper:  # Buy when ADX is above upper threshold
                trade = buyBacktest(curr_price, initial_balance, indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                coins_held = trade.amount
                initial_balance = 0  # Use all balance to buy coins
                state = 1
            elif state == 1 and adx < lower:  # Sell when ADX is below lower threshold
                trade = sellBacktest(curr_price, coins_held, indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                initial_balance = trade.deposit  # Update balance from the sale
                coins_held = 0
                state = 0
        
        elif indicator == "Commodity Channel Index":
            if i < 20:
                continue
            

            try:
                cci = compute_cci(high_prices, low_prices, close_prices, 20)
                print("CCI Value:", cci)
            except Exception as e:
                print(f"CCI Calculation Error: {e}")


            try:
                if state == 0 and cci < lower:  # Buy when CCI is below lower threshold
                    trade = buyBacktest(curr_price, initial_balance, indicator, curr_time)
                    trades.append(trade.dict())  # Store trade as a dictionary
                    coins_held = trade.amount
                    initial_balance = 0  # Use all balance to buy coins
                    state = 1
                elif state == 1 and cci > upper:  # Sell when CCI is above upper threshold
                    trade = sellBacktest(curr_price, coins_held, indicator, curr_time)
                    trades.append(trade.dict())  # Store trade as a dictionary
                    initial_balance = trade.deposit  # Update balance from the sale
                    coins_held = 0
                    state = 0
            except Exception as e:
                print(f"Trade Execution Error: {e}")        
        
        elif indicator == "Volume Weighted Average Price":
            vwap = compute_vwap(df['Close'], df['Volume'])  # Compute VWAP
            
            # Get the current VWAP value for the given timestamp
            current_vwap = vwap.iloc[i]
            
            # Print VWAP for debugging
            print(f"VWAP for {coin} at {df.index[i]}: {current_vwap}")
            
            # Buy when current price is lower than VWAP
            if state == 0 and curr_price < current_vwap:
                trade = buyBacktest(float(curr_price), float(initial_balance), indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                coins_held = trade.amount
                initial_balance = 0  # Use all balance to buy coins
                state = 1
                
            # Sell when current price is higher than VWAP
            elif state == 1 and curr_price > current_vwap:
                trade = sellBacktest(float(curr_price), coins_held, indicator, curr_time)
                trades.append(trade.dict())  # Store trade as a dictionary
                initial_balance = trade.deposit  # Update balance from the sale
                coins_held = 0
                state = 0
            else:
                log_hold_state(curr_price, indicator)
        
    # Final balance after all trades
    final_balance = coins_held * close_prices.iloc[-1] if coins_held > 0 else initial_balance
    profit = final_balance - balance  
    return {"finalBalance": final_balance, "profit": profit, "trades": trades}

def buyBacktest(price, balance, indicator, timestamp):
    """Perform a buy trade and return a Trade object."""
    amount = balance / price
    return Trade(
        action="BUY",
        price=price,
        amount=amount,
        timestamp=timestamp,  # Timestamp from the data
        indicator=indicator,
        deposit=balance,
    )

def sellBacktest(price, amount, indicator, timestamp):
    """Perform a sell trade and return a Trade object."""
    deposit = amount * price
    return Trade(
        action="SELL",
        price=price,
        amount=amount,
        timestamp=timestamp,  # Timestamp from the data
        indicator=indicator,
        deposit=deposit,
    )
