import streamlit as st
from typing import List, Dict
import pandas as pd
import yfinance as yf


@st.cache_data(show_spinner=True)
def fetch_live_data(tickers: List[str], interval: str = "1m") -> Dict[str, pd.DataFrame]:
    """
    Fetch live stock data for multiple tickers.
    Args:
        tickers (List[str]): List of stock ticker symbols.
        interval (str): Data interval (e.g., '1m', '5m', '15m').

    Returns:
        Dict[str, pd.DataFrame]: Dictionary mapping ticker to its DataFrame (only valid tickers).
    """
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
