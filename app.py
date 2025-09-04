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


# --- Portfolio Management Sidebar ---
st.sidebar.header("Portfolio Management")
if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = []

with st.sidebar.form("portfolio_form"):
    st.write("Add asset to portfolio:")
    port_ticker = st.text_input("Ticker", value="AAPL")
    port_qty = st.number_input("Quantity", min_value=1, value=10)
    port_add = st.form_submit_button("Add to Portfolio")
if port_add and port_ticker:
    st.session_state['portfolio'].append({"ticker": port_ticker.upper().strip(), "quantity": port_qty})

if st.sidebar.button("Clear Portfolio"):
    st.session_state['portfolio'] = []

st.sidebar.write("Current Portfolio:")
if st.session_state['portfolio']:
    st.sidebar.table(pd.DataFrame(st.session_state['portfolio']))

st.sidebar.header("Live Ticker & Volume")
live_ticker = st.sidebar.empty()
live_volume = st.sidebar.empty()

with st.form("stock_form"):
    ticker_input = st.text_input(
        t("ticker_input", lang), value="AAPL, TSLA"
    )
    col1, col2 = st.columns(2)
    start_date = col1.date_input(t("start_date", lang), value=date(2024, 1, 1))
    end_date = col2.date_input(t("end_date", lang), value=date.today())
    indicator = st.selectbox(
        t("indicator", lang),
        [
            "None",
            "SMA (20)", "EMA (20)", "Bollinger Bands (20)", "RSI (14)", "MACD",
            "Stochastic Oscillator (14,3)", "ATR (14)", "VWAP", "Ichimoku Cloud",
            "User-Defined"
        ]
    )
    # Multi-timeframe: show translated labels, use English for logic
    timeframe_options = ["Daily", "Weekly", "Monthly", "Intraday"]
    timeframe_labels = [t(opt, lang) for opt in timeframe_options]
    timeframe_label = st.selectbox("Timeframe", options=timeframe_labels, index=0)
    # Map back to English value for logic
    timeframe = timeframe_options[timeframe_labels.index(timeframe_label)]
    overlay = st.text_input(
        "Custom Overlay (pandas formula, e.g. 'Close.rolling(10).mean()')",
        value=""
    )
    chart_type = st.selectbox(
        t("chart_type", lang),
        [t("line", lang), t("candlestick", lang), t("area", lang)]
    )
    submitted = st.form_submit_button(t("submit", lang))

@st.cache_data(show_spinner=True)
def fetch_live_data(tickers: List[str], interval: str = "1m") -> Dict[str, pd.DataFrame]:
    data = {}
    for ticker in tickers:
        try:
            t = ticker.upper().strip()
            stock = yf.Ticker(t)
            hist = stock.history(period="1d", interval=interval)
            if not hist.empty:
                data[t] = hist
        except Exception:
            continue
    return data

if submitted or timeframe == "Intraday" or st.session_state['portfolio']:
    # Parse tickers
    tickers = [t.strip() for t in ticker_input.replace(',', ' ').split() if t.strip()]
    # Portfolio tickers
    port_tickers = [item['ticker'] for item in st.session_state['portfolio']]
    # Multi-timeframe support
    interval_map = {
        "Daily": "1d",
        "Weekly": "1wk",
        "Monthly": "1mo",
        "Intraday": "15m"
    }
    interval = interval_map.get(timeframe, "1d")