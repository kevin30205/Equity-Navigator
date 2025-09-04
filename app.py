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

# --- UI Layout ---
st.set_page_config(page_title="Stock Dashboard", layout="centered")
st.title("📈 Streamlit Stock Dashboard")

with st.form("stock_form"):
    ticker_input = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA)", value="AAPL")
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start Date", value=date(2024, 1, 1))
    end_date = col2.date_input("End Date", value=date.today())
    submitted = st.form_submit_button("Go")
