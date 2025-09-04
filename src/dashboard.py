"""
dashboard.py
Module for Streamlit dashboard layout, configuration, and UI logic.
"""

import streamlit as st
import pandas as pd
from datetime import date
from typing import Dict, List, Tuple, Any

from src.i18n import t, LANGUAGES


def set_page_config(lang: str) -> None:
    """
    Set Streamlit page configuration and title.

    Args:
        lang (str): Selected language code.
    """
    st.set_page_config(page_title=t("title", lang), layout="wide")
    st.title(t("title", lang))


def select_language(session_state: dict) -> str:
    """
    Handle language selection and return selected language.

    Args:
        session_state (dict): Streamlit session state.

    Returns:
        str: Selected language code.
    """
    if 'lang' not in session_state:
        session_state['lang'] = 'en'
    lang = st.selectbox(
        "🌐 Language",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=list(LANGUAGES.keys()).index(session_state['lang'])
    )
    session_state['lang'] = lang
    return lang


def setup_autorefresh() -> None:
    """
    Enable real-time/intraday data refresh if supported by Streamlit.
    """
    st_autorefresh = getattr(st, "autorefresh", None)
    if st_autorefresh:
        st_autorefresh(interval=10000, key="realtime_refresh")  # 10s refresh


def display_download_buttons(data: Dict[str, pd.DataFrame], metrics_df: pd.DataFrame, lang: str) -> None:
    """
    Display download buttons for key metrics and historical data.

    Args:
        data (Dict[str, pd.DataFrame]): Dictionary of historical stock data.
        metrics_df (pd.DataFrame): DataFrame containing key metrics.
        lang (str): Selected language code.

    Returns:
        None
    """
    st.markdown(f"### {t('download_data', lang)}")
    # Prepare download buttons (key metrics + each ticker's historical data)
    download_buttons = []
    csv_metrics = metrics_df.to_csv(index=False).encode('utf-8')
    download_buttons.append({
        "label": t("download_key_metrics", lang),
        "data": csv_metrics,
        "file_name": "key_metrics.csv",
        "mime": "text/csv",
        "key": "download_key_metrics_1"
    })
    download_buttons.append({
        "label": t("download_key_metrics", lang),
        "data": csv_metrics,
        "file_name": "key_metrics.csv",
        "mime": "text/csv",
        "key": "download_key_metrics_2"
    })
    
    for ticker, hist in data.items():
        csv_hist = hist.to_csv().encode('utf-8')
        download_buttons.append({
            "label": t("download_history", lang, ticker=ticker),
            "data": csv_hist,
            "file_name": f"{ticker}_history.csv",
            "mime": "text/csv",
            "key": f"download_{ticker}_history_1"
        })
        download_buttons.append({
            "label": t("download_history", lang, ticker=ticker),
            "data": csv_hist,
            "file_name": f"{ticker}_history.csv",
            "mime": "text/csv",
            "key": f"download_{ticker}_history_2"
        })

    # Display buttons in rows of max 3 per row
    for i in range(0, len(download_buttons), 3):
        cols = st.columns(3)
        for j, btn in enumerate(download_buttons[i:i+3]):
            with cols[j]:
                st.download_button(
                    label=btn["label"],
                    data=btn["data"],
                    file_name=btn["file_name"],
                    mime=btn["mime"],
                    key=btn["key"]
                )

def portfolio_management_ui() -> Tuple[List[Dict[str, Any]], Any, Any]:
    """
    Render the portfolio management UI components.

    Returns:
        Tuple[List[Dict[str, Any]], Any, Any]: Current portfolio, live ticker placeholder, live volume placeholder.
    """
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

    return st.session_state['portfolio'], live_ticker, live_volume


def stock_form_ui(lang: str) -> Tuple[str, date, date, str, str, bool, str, str]:
    """
    Render the stock input form and return user inputs.

    Args:
        lang (str): Selected language code.

    Returns:
        Tuple[str, date, date, str, str, bool, str, str]: Ticker input, start date, end date, indicator, chart type, form submitted flag, timeframe, overlay.
    """
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

    return ticker_input, start_date, end_date, indicator, chart_type, submitted, timeframe, overlay

