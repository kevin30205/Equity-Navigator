# Additional technical indicators and overlays for Stock Dashboard
# Implements: Stochastic Oscillator, ATR, VWAP, Ichimoku Cloud, and user-defined indicator support

import pandas as pd
from typing import Optional, Tuple, Dict, Any


def add_stochastic(df: pd.DataFrame, k_window: int = 14, d_window: int = 3) -> Tuple[pd.Series, pd.Series]:
    """Stochastic Oscillator (K%D)"""
    low_min = df['Low'].rolling(window=k_window).min()
    high_max = df['High'].rolling(window=k_window).max()
    k = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    d = k.rolling(window=d_window).mean()
    return k, d