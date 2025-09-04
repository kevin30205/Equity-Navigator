"""
Additional technical indicators and overlays for Equity Navigator
Implements: Stochastic Oscillator, ATR, VWAP, Ichimoku Cloud, and user-defined indicator support
"""

import pandas as pd
from typing import Optional, Tuple, Dict


# --- Indicator Functions ---
def add_sma(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """Simple Moving Average"""
    return df['Close'].rolling(window=window).mean()


def add_ema(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """Exponential Moving Average"""
    return df['Close'].ewm(span=window, adjust=False).mean()


def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Relative Strength Index"""
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def add_macd(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """MACD and Signal Line"""
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal


def add_bollinger(df: pd.DataFrame, window: int = 20) -> Tuple[pd.Series, pd.Series]:
    """Bollinger Bands"""
    sma = add_sma(df, window)
    std = df['Close'].rolling(window=window).std()
    upper = sma + 2 * std
    lower = sma - 2 * std
    return upper, lower


def add_stochastic(df: pd.DataFrame, k_window: int = 14, d_window: int = 3) -> Tuple[pd.Series, pd.Series]:
    """Stochastic Oscillator (K%D)"""
    low_min = df['Low'].rolling(window=k_window).min()
    high_max = df['High'].rolling(window=k_window).max()
    k = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    d = k.rolling(window=d_window).mean()
    return k, d


def add_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Average True Range (ATR)"""
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean()
    return atr


def add_vwap(df: pd.DataFrame) -> pd.Series:
    """Volume Weighted Average Price (VWAP)"""
    vwap = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    return vwap


def add_ichimoku(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """Ichimoku Cloud"""
    high9 = df['High'].rolling(window=9).max()
    low9 = df['Low'].rolling(window=9).min()
    tenkan_sen = (high9 + low9) / 2
    high26 = df['High'].rolling(window=26).max()
    low26 = df['Low'].rolling(window=26).min()
    kijun_sen = (high26 + low26) / 2
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
    high52 = df['High'].rolling(window=52).max()
    low52 = df['Low'].rolling(window=52).min()
    senkou_span_b = ((high52 + low52) / 2).shift(26)
    chikou_span = df['Close'].shift(-26)
    return {
        'tenkan_sen': tenkan_sen,
        'kijun_sen': kijun_sen,
        'senkou_span_a': senkou_span_a,
        'senkou_span_b': senkou_span_b,
        'chikou_span': chikou_span
    }


def add_user_indicator(df: pd.DataFrame, formula: str) -> Optional[pd.Series]:
    """
    Evaluate a user-defined indicator formula safely.
    Args:
        df (pd.DataFrame): Stock data.
        formula (str): Formula using pandas syntax, e.g. 'Close.rolling(10).mean()'.
    Returns:
        Optional[pd.Series]: Resulting indicator series, or None if invalid.
    """
    allowed_names = {'Close', 'Open', 'High', 'Low', 'Volume'}
    try:
        # Only allow access to columns, no builtins or globals
        local_dict = {col: df[col] for col in allowed_names if col in df.columns}
        result = eval(formula, {"__builtins__": None}, local_dict)
        if isinstance(result, pd.Series):
            return result
    except Exception:
        return None
    return None
