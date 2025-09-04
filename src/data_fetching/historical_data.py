import streamlit as st
from datetime import date
from typing import List, Dict
import pandas as pd
import yfinance as yf


# --- Helper Functions ---
@st.cache_data(show_spinner=True)
def fetch_stock_data_multi_timeframe(tickers: List[str], start: date, end: date, interval: str) -> Dict[str, pd.DataFrame]:
    """
    Fetch historical stock data for multiple tickers and a date range.

    Args:
        tickers (List[str]): List of stock ticker symbols.
        start (date): Start date.
        end (date): End date.
        interval (str): Data interval (e.g., '1d', '1wk', '1mo').

    Returns:
        Dict[str, pd.DataFrame]: Dictionary mapping ticker to its DataFrame (only valid tickers).
    """
    data = {}
    for ticker in tickers:
        try:
            t = ticker.upper().strip()
            stock = yf.Ticker(t)
            hist = stock.history(start=start, end=end, interval=interval)
            if not hist.empty:
                data[t] = hist
        except Exception:
            continue
    return data
