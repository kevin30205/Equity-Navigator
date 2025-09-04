"""
Equity Navigator
A web application for visualizing historical stock data.
"""

# --- Imports ---
import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from datetime import date
from typing import Optional, Tuple, List, Dict
from stock_events import get_stock_events
from i18n import t, LANGUAGES
from indicators import (
    add_stochastic, add_atr, add_vwap, add_ichimoku, add_user_indicator
)

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

# --- Helper Functions ---
@st.cache_data(show_spinner=True)
def fetch_stock_data_multi(tickers: List[str], start: date, end: date) -> Dict[str, pd.DataFrame]:
    """
    Fetch historical stock data for multiple tickers and a date range.

    Args:
        tickers (List[str]): List of stock ticker symbols.
        start (date): Start date.
        end (date): End date.

    Returns:
        Dict[str, pd.DataFrame]: Dictionary mapping ticker to its DataFrame (only valid tickers).
    """
    data = {}
    for ticker in tickers:
        try:
            t = ticker.upper().strip()
            stock = yf.Ticker(t)
            hist = stock.history(start=start, end=end)
            if not hist.empty:
                data[t] = hist
        except Exception:
            continue
    return data


# --- Real-Time & Intraday Data ---
st_autorefresh = getattr(st, "autorefresh", None)
if st_autorefresh:
    st_autorefresh(interval=10000, key="realtime_refresh")  # 10s refresh


# --- Language Selector ---
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'en'
lang = st.selectbox("🌐 Language", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=list(LANGUAGES.keys()).index(st.session_state['lang']))
st.session_state['lang'] = lang

st.set_page_config(page_title=t("title", lang), layout="wide")
st.title(t("title", lang))