"""
stock_events.py
Module for fetching and formatting significant stock events (earnings, splits) for annotation on charts.
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Any

def get_stock_events(ticker: str, start: pd.Timestamp, end: pd.Timestamp) -> List[Dict[str, Any]]:
    """
    Fetch significant events (earnings, splits) for a given ticker within a date range.

    Args:
        ticker (str): Stock ticker symbol.
        start (pd.Timestamp): Start date.
        end (pd.Timestamp): End date.

    Returns:
        List[Dict[str, Any]]: List of event dicts with 'date', 'type', and 'desc'.
    """
    stock = yf.Ticker(ticker)
    events = []
    # Earnings
    try:
        earnings = stock.get_earnings_dates(limit=20)
        if not earnings.empty:
            for _, row in earnings.iterrows():
                event_date = pd.to_datetime(row['Earnings Date'])
                if start <= event_date <= end:
                    events.append({
                        'date': event_date,
                        'type': 'Earnings',
                        'desc': f"Earnings: {row['EPS Actual']} (Est: {row['EPS Estimate']})"
                    })
    except Exception:
        pass
    # Splits
    try:
        splits = stock.splits
        if splits is not None and not splits.empty:
            for split_date, split_ratio in splits.items():
                split_dt = pd.to_datetime(split_date)
                if start <= split_dt <= end:
                    events.append({
                        'date': split_dt,
                        'type': 'Split',
                        'desc': f"Split: {split_ratio}"
                    })
    except Exception:
        pass
    return events
