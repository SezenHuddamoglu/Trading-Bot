import pandas as pd
import numpy as np

def compute_rsi(data, period):
    """
    Compute the Relative Strength Index (RSI) for a given dataset.
    
    Parameters:
    - data: A list or array of price data.
    - period: The period over which to calculate the RSI.
    
    Returns:
    - The latest RSI value.
    """
    diff = np.diff(data)  # Calculate price changes
    gain = np.maximum(diff, 0)  # Positive gains
    loss = np.abs(np.minimum(diff, 0))  # Negative losses (as positive values)
    avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()  # Average gain
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()  # Average loss
    rs = avg_gain / avg_loss  # Relative strength
    rsi = 100 - (100 / (1 + rs))  # RSI formula
    return rsi.iloc[-1]  # Return the most recent RSI value

def compute_macd(prices, short_window=12, long_window=26, signal_window=9):
    """
    Compute the Moving Average Convergence Divergence (MACD) and Signal Line.
    
    Parameters:
    - prices: A Pandas Series of price data.
    - short_window: The period for the short EMA.
    - long_window: The period for the long EMA.
    - signal_window: The period for the signal line EMA.
    
    Returns:
    - The latest MACD and Signal Line values.
    """
    short_ema = prices.ewm(span=short_window, adjust=False).mean()  # Short EMA
    long_ema = prices.ewm(span=long_window, adjust=False).mean()  # Long EMA
    macd = short_ema - long_ema  # MACD line
    signal = macd.ewm(span=signal_window, adjust=False).mean()  # Signal line
    return macd.iloc[-1], signal.iloc[-1]  # Return latest values

def compute_ma(prices, period):
    """
    Compute the Simple Moving Average (SMA).
    
    Parameters:
    - prices: A list or array of price data.
    - period: The number of periods to calculate the SMA.
    
    Returns:
    - The SMA value.
    """
   
    if isinstance(period, float):
        period = int(period)
    
    return sum(prices[-period:]) / period


def compute_ema(prices, period):
    """
    Compute the Exponential Moving Average (EMA).
    
    Parameters:
    - prices: A list of price data.
    - period: The period for the EMA.
    
    Returns:
    - The EMA value.
    """
    multiplier = 2 / (period + 1)
    ema = prices[0]  # Start with the first price as initial EMA
    for price in prices[1:]:
        ema = (price - ema) * multiplier + ema  # EMA formula
    return ema

def compute_stochastic_rsi(prices, period=14):
    """
    Compute the Stochastic RSI.
    
    Parameters:
    - prices: A list of RSI values.
    - period: The period for Stochastic RSI calculation.
    
    Returns:
    - The Stochastic RSI value.
    """
    if len(prices) < period:
        raise ValueError(f"Yeterli veri yok. İstenen dönem: {period}, Mevcut veri: {len(prices)}")

    lowest_low = min(prices[-period:])  # Lowest RSI in the period
    highest_high = max(prices[-period:])  # Highest RSI in the period
    current_rsi = prices[-1]  # Current RSI value

    denominator = highest_high - lowest_low
    if denominator == 0:
        return 50  

    stochastic_rsi = (current_rsi - lowest_low) / denominator * 100
    return stochastic_rsi


def compute_adx(high, low, close, period=14):
    """
    Compute the Average Directional Index (ADX).
    
    Parameters:
    - high: High prices.
    - low: Low prices.
    - close: Close prices.
    - period: The period for the ADX calculation.
    
    Returns:
    - The latest ADX value.
    """
    min_length = min(len(high), len(low), len(close))  # Ensure all arrays have the same length
    high = np.array(high[:min_length])
    low = np.array(low[:min_length])
    close = np.array(close[:min_length])
    
    tr1 = high[1:] - low[1:]  # True Range calculations
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    tr = np.maximum.reduce([tr1, tr2, tr3])
    
    up_move = high[1:] - high[:-1]  # Positive directional movement
    down_move = low[:-1] - low[1:]  # Negative directional movement
    
    plus_di = np.where((up_move > down_move) & (up_move > 0), up_move, 0) / tr
    minus_di = np.where((down_move > up_move) & (down_move > 0), down_move, 0) / tr
    
    tr_smooth = np.convolve(tr, np.ones(period), 'valid')  # Smoothed True Range
    plus_di_smooth = np.convolve(plus_di, np.ones(period), 'valid')  # Smoothed +DI
    minus_di_smooth = np.convolve(minus_di, np.ones(period), 'valid')  # Smoothed -DI
    
    dx = 100 * np.abs(plus_di_smooth - minus_di_smooth) / (plus_di_smooth + minus_di_smooth)  # DX formula
    adx = np.convolve(dx, np.ones(period) / period, 'valid')  # ADX formula
    
    if adx.size == 0:
        raise ValueError("ADX calculation failed. Insufficient data.")
    
    return adx[-1]  # Return the most recent ADX value

def compute_vwap(close_prices, volumes):
    """
    Compute the Volume Weighted Average Price (VWAP).
    
    Parameters:
    - close_prices: A Pandas Series of closing prices.
    - volumes: A Pandas Series of trading volumes.
    
    Returns:
    - The VWAP value.
    """
    if close_prices.empty or volumes.empty:
        raise ValueError("Close prices or volumes are empty.")
    cumulative_price_volume = (close_prices * volumes).cumsum()  # Cumulative price-volume
    cumulative_volume = volumes.cumsum()  # Cumulative volume
    return cumulative_price_volume / cumulative_volume  # VWAP formula

import pandas as pd
import numpy as np


def compute_cci(high, low, close, period=20):
    """
    Commodity Channel Index (CCI) hesaplama fonksiyonu.
    
    Parametreler:
        - high: High fiyatlar (list veya pd.Series).
        - low: Low fiyatlar (list veya pd.Series).
        - close: Close fiyatlar (list veya pd.Series).
        - period: CCI hesaplama periyodu (default: 20).

    Geri Dönüş:
        - Son hesaplanan CCI değeri (float).
    """
    try:
        # Girdileri Pandas Series'e çevir
        high = pd.Series(high, dtype="float64")
        low = pd.Series(low, dtype="float64")
        close = pd.Series(close, dtype="float64")

        # Yeterli veri kontrolü
        if len(high) < period or len(low) < period or len(close) < period:
            raise ValueError("CCI hesaplamak için yeterli veri yok.")
        
        # Typical Price hesaplama
        tp = (high + low + close) / 3

        # SMA (Simple Moving Average) hesaplama
        sma_tp = tp.rolling(window=period).mean()

        # Mean Deviation manuel hesaplama
        mean_dev = tp.rolling(window=period).apply(
            lambda x: (abs(x - x.mean())).mean(), raw=True
        )

        # Son CCI hesaplama
        cci = (tp - sma_tp) / (0.015 * mean_dev)

        # Son CCI değerini döndür
        return cci.iloc[-1]
    
    except Exception as e:
        raise ValueError(f"CCI hesaplama sırasında hata: {e}")
