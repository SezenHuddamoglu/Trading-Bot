import pandas as pd
import numpy as np


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
def compute_bollinger_bands(close_prices, window=20):
    if len(close_prices) < window:
        raise ValueError("Not enough data to calculate Bollinger Bands")
    rolling_mean = close_prices.rolling(window=window).mean()
    rolling_std = close_prices.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * 2)
    lower_band = rolling_mean - (rolling_std * 2)
    return upper_band.iloc[-1], lower_band.iloc[-1]


def compute_ma(prices, period):
    return prices[-period:].mean()

def compute_ema(prices, period):
    multiplier = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = (price - ema) * multiplier + ema
    return ema

def compute_ichimoku(prices, high_prices, low_prices):
    conversion_line = (max(high_prices[-9:]) + min(low_prices[-9:])) / 2
    base_line = (max(high_prices[-26:]) + min(low_prices[-26:])) / 2
    leading_span_a = (conversion_line + base_line) / 2
    leading_span_b = (max(high_prices[-52:]) + min(low_prices[-52:])) / 2
    return conversion_line, base_line, leading_span_a, leading_span_b

def compute_stochastic_rsi(prices, period=14):
    lowest_low = min(prices[-period:])
    highest_high = max(prices[-period:])
    current_rsi = prices[-1]
    stochastic_rsi = (current_rsi - lowest_low) / (highest_high - lowest_low) * 100
    return stochastic_rsi

def compute_adx(high, low, close, period=14):
    import numpy as np
    
    # Girdi veri uzunluklarını eşitle
    min_length = min(len(high), len(low), len(close))
    high = np.array(high[:min_length])
    low = np.array(low[:min_length])
    close = np.array(close[:min_length])

    # True Range hesaplama
    tr1 = high[1:] - low[1:]
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    
    tr = np.maximum.reduce([tr1, tr2, tr3])
    
    # +DI ve -DI hesapla
    up_move = high[1:] - high[:-1]
    down_move = low[:-1] - low[1:]
    
    plus_di = np.where((up_move > down_move) & (up_move > 0), up_move, 0) / tr
    minus_di = np.where((down_move > up_move) & (down_move > 0), down_move, 0) / tr

    # Ortalama almak için smooth işlemine geç
    tr_smooth = np.convolve(tr, np.ones(period), 'valid')
    plus_di_smooth = np.convolve(plus_di, np.ones(period), 'valid')
    minus_di_smooth = np.convolve(minus_di, np.ones(period), 'valid')

    # DX ve ADX hesapla
    dx = 100 * np.abs(plus_di_smooth - minus_di_smooth) / (plus_di_smooth + minus_di_smooth)
    adx = np.convolve(dx, np.ones(period) / period, 'valid')
    
    if adx.size == 0:
        raise ValueError("ADX hesaplanamadı. Veri yetersiz.")
    
    return adx[-1]

def compute_vwap(close_prices, volumes):
    if close_prices.empty or volumes.empty:
        raise ValueError("Close prices or volumes are empty.")
    cumulative_price_volume = (close_prices * volumes).cumsum()
    cumulative_volume = volumes.cumsum()
    return cumulative_price_volume / cumulative_volume


def compute_cci(high, low, close, period=20):
    # float olarak işlem yaptığınızdan emin olun
    high = pd.to_numeric(high, errors="coerce")
    low = pd.to_numeric(low, errors="coerce")
    close = pd.to_numeric(close, errors="coerce")
    
    if high.isnull().any() or low.isnull().any() or close.isnull().any():
        raise ValueError("Invalid data detected in CCI calculation inputs.")

    tp = (high + low + close) / 3  # Typical Price
    sma_tp = tp[-period:].mean()  # Simple Moving Average of TP
    mean_dev = abs(tp[-period:] - sma_tp).mean()  # Mean Deviation
    
    if mean_dev == 0:
        raise ValueError("Mean deviation is zero, cannot calculate CCI.")
    
    cci = (tp[-1] - sma_tp) / (0.015 * mean_dev)  # CCI Formula
    return cci


