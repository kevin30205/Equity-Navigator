"""
Stock Dashboard
A web application for visualizing historical stock data.
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from datetime import date
from typing import Optional, Tuple

# --- Helper Functions ---
def fetch_stock_data(ticker: str, start: date, end: date) -> Optional[Tuple[str, pd.DataFrame]]:
    """
    Fetch historical stock data for a given ticker and date range.

    Args:
        ticker (str): Stock ticker symbol.
        start (date): Start date.
        end (date): End date.

    Returns:
        Optional[Tuple[str, pandas.DataFrame]]: Tuple of resolved ticker and DataFrame, or None if invalid.
    """
    try:
        ticker = ticker.upper().strip()
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start, end=end)
        if hist.empty:
            return None
        return ticker, hist
    except Exception:
        return None
