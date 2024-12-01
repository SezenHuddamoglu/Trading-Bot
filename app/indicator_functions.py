


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

    # Calculate True Range (TR)
    tr = np.maximum.reduce([high[1:] - low[1:], 
                            abs(high[1:] - close[:-1]), 
                            abs(low[1:] - close[:-1])])

    # Calculate +DI and -DI
    up_move = high[1:] - high[:-1]
    down_move = low[:-1] - low[1:]
    plus_di = 100 * np.where((up_move > down_move) & (up_move > 0), up_move, 0) / tr
    minus_di = 100 * np.where((down_move > up_move) & (down_move > 0), down_move, 0) / tr

    # Smooth +DI, -DI and True Range
    tr_smooth = np.convolve(tr, np.ones(period), 'valid')
    plus_di_smooth = np.convolve(plus_di, np.ones(period), 'valid')
    minus_di_smooth = np.convolve(minus_di, np.ones(period), 'valid')

    # Calculate DX and ADX
    dx = 100 * abs(plus_di_smooth - minus_di_smooth) / (plus_di_smooth + minus_di_smooth)
    adx = np.convolve(dx, np.ones(period) / period, 'valid')

    return adx[-1]

def compute_vwap(close_prices, volumes):
    cumulative_price_volume = (close_prices * volumes).cumsum()
    cumulative_volume = volumes.cumsum()
    return cumulative_price_volume / cumulative_volume

def compute_cci(high, low, close, period=20):
    tp = (high + low + close) / 3  # Typical Price
    sma_tp = tp[-period:].mean()  # Simple Moving Average of TP
    mean_dev = abs(tp[-period:] - sma_tp).mean()  # Mean Deviation
    cci = (tp[-1] - sma_tp) / (0.015 * mean_dev)  # CCI Formula
    return cci

