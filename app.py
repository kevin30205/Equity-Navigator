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
from src.stock_events import get_stock_events
from src.i18n import t, LANGUAGES
from src.indicators import (
    add_stochastic, add_atr, add_vwap, add_ichimoku, add_user_indicator, add_sma, add_ema, add_bollinger, add_rsi, add_macd
)
from src.data_fetching.historical_data import fetch_stock_data_multi_timeframe
from src.data_fetching.live_data import fetch_live_data
from src.dashboard import set_page_config, select_language, setup_autorefresh, display_download_buttons, portfolio_management_ui, stock_form_ui
from src.visualization import create_volume_chart, add_macd_chart, add_rsi_chart, create_price_chart, display_key_metrics
from src.portfolio import create_portfolio_section


def main():
    # --- Real-Time & Intraday Data ---
    setup_autorefresh()

    # --- Language Selector ---
    lang = select_language(session_state=st.session_state)

    # --- Page Configuration ---
    set_page_config(lang=lang)

    # --- Portfolio Management Sidebar ---
    st.session_state['portfolio'], live_ticker, live_volume = portfolio_management_ui()

    # --- Stock Input Form ---
    ticker_input, start_date, end_date, indicator, chart_type, submitted, timeframe, overlay = stock_form_ui(lang)

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
        
        if timeframe == "Intraday":
            data = fetch_live_data(tickers, interval="1m")
            port_data = fetch_live_data(port_tickers, interval="1m") if port_tickers else {}
        else:
            data = fetch_stock_data_multi_timeframe(tickers, start_date, end_date, interval)
            port_data = fetch_stock_data_multi_timeframe(port_tickers, start_date, end_date, interval) if port_tickers else {}
        
        if not data and not port_data:
            st.error(t("error_no_data", lang))
        else:
            metrics_df = display_key_metrics(data=data, lang=lang, t=t, timeframe=timeframe, live_ticker=live_ticker, live_volume=live_volume)

            # --- Portfolio Performance & Allocation ---
            if port_data:
                create_portfolio_section(port_data=port_data)

            # --- Download Buttons ---
            display_download_buttons(data=data, metrics_df=metrics_df, lang=lang)

        # --- Customizable Chart: Closing Prices + Indicators ---
        create_price_chart(
            data=data,
            chart_type=chart_type if chart_type in ["Line", "Candlestick", "Area"] else "Line",
            indicator=indicator,
            overlay=overlay,
            start_date=str(start_date),
            end_date=str(end_date),
            add_sma=add_sma,
            add_ema=add_ema,
            add_bollinger=add_bollinger,
            add_stochastic=add_stochastic,
            add_atr=add_atr,
            add_vwap=add_vwap,
            add_ichimoku=add_ichimoku,
            add_user_indicator=add_user_indicator,
            get_stock_events=get_stock_events
        )

        # --- RSI Chart ---
        if indicator == "RSI (14)":
            add_rsi_chart(data=data, add_rsi=add_rsi)

        # --- MACD Chart ---
        if indicator == "MACD":
            add_macd_chart(data=data, add_macd=add_macd)

        # --- Volume Chart: Trading Volume (Stacked) ---
        create_volume_chart(data=data)


if __name__ == "__main__":
    main()
