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
    @st.cache_data(show_spinner=True)
    def fetch_stock_data_multi_timeframe(tickers: List[str], start: date, end: date, interval: str) -> Dict[str, pd.DataFrame]:
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
    if timeframe == "Intraday":
        data = fetch_live_data(tickers, interval="1m")
        port_data = fetch_live_data(port_tickers, interval="1m") if port_tickers else {}
    else:
        data = fetch_stock_data_multi_timeframe(tickers, start_date, end_date, interval)
        port_data = fetch_stock_data_multi_timeframe(port_tickers, start_date, end_date, interval) if port_tickers else {}
    if not data and not port_data:
        st.error(t("error_no_data", lang))
    else:
        # --- Live Ticker & Volume Display ---
        if timeframe == "Intraday":
            ticker_info = []
            for ticker, hist in data.items():
                last_row = hist.iloc[-1]
                price = last_row['Close']
                volume = last_row['Volume']
                ticker_info.append(f"{ticker}: ${price:,.2f} | Vol: {volume:,}")
            live_ticker.markdown("**Live Prices:**<br>" + "<br>".join(ticker_info), unsafe_allow_html=True)
            live_volume.markdown("**Streaming Volume:**<br>" + "<br>".join([f"{ticker}: {hist.iloc[-1]['Volume']:,}" for ticker, hist in data.items()]), unsafe_allow_html=True)
        # --- Key Metrics Table ---
        st.subheader(t("key_metrics", lang))
        metrics = []
        for ticker, hist in data.items():
            current_close = hist['Close'][-1]
            start_close = hist['Close'][0]
            pct_change = ((current_close - start_close) / start_close) * 100
            high = hist['Close'].max()
            low = hist['Close'].min()
            metrics.append({
                t("current_close", lang): f"${current_close:,.2f}",
                t("pct_change", lang): f"{pct_change:.2f}%",
                t("high_low", lang): f"${high:,.2f} / ${low:,.2f}",
                "Ticker": ticker
            })
        metrics_df = pd.DataFrame(metrics)
        st.dataframe(metrics_df)

        # --- Portfolio Performance & Allocation ---
        if port_data:
            st.subheader("Portfolio Performance & Allocation")
            port_table = []
            total_value = 0
            values = []
            for item in st.session_state['portfolio']:
                ticker = item['ticker']
                qty = item['quantity']
                if ticker in port_data:
                    price = port_data[ticker]['Close'][-1]
                    value = price * qty
                    values.append(value)
                    total_value += value
                    port_table.append({
                        "Ticker": ticker,
                        "Quantity": qty,
                        "Last Price": price,
                        "Value": value
                    })
            if port_table:
                port_df = pd.DataFrame(port_table)
                port_df["Allocation %"] = (port_df["Value"] / total_value * 100).round(2)
                st.dataframe(port_df)
                # Allocation Pie Chart
                fig_alloc = go.Figure(go.Pie(labels=port_df["Ticker"], values=port_df["Value"], hole=0.4))
                fig_alloc.update_layout(title="Portfolio Allocation")
                st.plotly_chart(fig_alloc, use_container_width=True)
                # Portfolio Performance
                st.write(f"**Total Portfolio Value:** ${total_value:,.2f}")
                # Risk Metrics
                st.subheader("Portfolio Risk Metrics")
                # Volatility (std dev of returns)
                returns = []
                for ticker in port_df["Ticker"]:
                    hist = port_data[ticker]["Close"]
                    ret = hist.pct_change().dropna()
                    returns.append(ret)
                if returns:
                    port_returns = pd.concat(returns, axis=1).mean(axis=1)
                    volatility = port_returns.std() * (252 ** 0.5)  # annualized
                    st.write(f"**Portfolio Volatility (annualized):** {volatility:.2%}")
                # Beta (vs. S&P 500)
                try:
                    sp500 = yf.Ticker("SPY").history(period="1y", interval="1d")
                    sp500_ret = sp500["Close"].pct_change().dropna()
                    if returns:
                        port_ret = pd.concat(returns, axis=1).mean(axis=1)
                        beta = port_ret.cov(sp500_ret) / sp500_ret.var()
                        st.write(f"**Portfolio Beta (vs. S&P 500):** {beta:.2f}")
                except Exception:
                    st.write("Beta calculation unavailable.")

        # --- Download Buttons ---
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

        # --- Customizable Chart: Closing Prices + Indicators ---
    fig_price = go.Figure()
    for ticker, hist in data.items():
        events = get_stock_events(ticker, pd.to_datetime(start_date), pd.to_datetime(end_date))
        # Chart type
        if chart_type == "Line":
            fig_price.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name=ticker))
        elif chart_type == "Area":
            fig_price.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name=ticker, fill='tozeroy'))
        elif chart_type == "Candlestick":
            if {'Open', 'High', 'Low', 'Close'}.issubset(hist.columns):
                fig_price.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name=ticker))
        # Indicator overlays
        if indicator == "SMA (20)":
            fig_price.add_trace(go.Scatter(x=hist.index, y=add_sma(hist, 20), mode='lines', name=f"{ticker} SMA(20)", line=dict(dash='dash')))
        elif indicator == "EMA (20)":
            fig_price.add_trace(go.Scatter(x=hist.index, y=add_ema(hist, 20), mode='lines', name=f"{ticker} EMA(20)", line=dict(dash='dot')))
        elif indicator == "Bollinger Bands (20)":
            upper, lower = add_bollinger(hist, 20)
            fig_price.add_trace(go.Scatter(x=hist.index, y=upper, mode='lines', name=f"{ticker} Bollinger Upper", line=dict(color='rgba(0,100,200,0.3)', dash='dot')))
            fig_price.add_trace(go.Scatter(x=hist.index, y=lower, mode='lines', name=f"{ticker} Bollinger Lower", line=dict(color='rgba(200,100,0,0.3)', dash='dot')))
        elif indicator == "Stochastic Oscillator (14,3)":
            k, d = add_stochastic(hist, 14, 3)
            fig_price.add_trace(go.Scatter(x=hist.index, y=k, mode='lines', name=f"{ticker} %K"))
            fig_price.add_trace(go.Scatter(x=hist.index, y=d, mode='lines', name=f"{ticker} %D"))
        elif indicator == "ATR (14)":
            atr = add_atr(hist, 14)
            fig_price.add_trace(go.Scatter(x=hist.index, y=atr, mode='lines', name=f"{ticker} ATR(14)", line=dict(dash='dot')))
        elif indicator == "VWAP":
            vwap = add_vwap(hist)
            fig_price.add_trace(go.Scatter(x=hist.index, y=vwap, mode='lines', name=f"{ticker} VWAP", line=dict(dash='dash')))
        elif indicator == "Ichimoku Cloud":
            ichimoku = add_ichimoku(hist)
            fig_price.add_trace(go.Scatter(x=hist.index, y=ichimoku['tenkan_sen'], mode='lines', name=f"{ticker} Tenkan-sen"))
            fig_price.add_trace(go.Scatter(x=hist.index, y=ichimoku['kijun_sen'], mode='lines', name=f"{ticker} Kijun-sen"))
            fig_price.add_trace(go.Scatter(x=hist.index, y=ichimoku['senkou_span_a'], mode='lines', name=f"{ticker} Senkou Span A"))
            fig_price.add_trace(go.Scatter(x=hist.index, y=ichimoku['senkou_span_b'], mode='lines', name=f"{ticker} Senkou Span B"))
            fig_price.add_trace(go.Scatter(x=hist.index, y=ichimoku['chikou_span'], mode='lines', name=f"{ticker} Chikou Span"))
        elif indicator == "User-Defined" and overlay:
            user_series = add_user_indicator(hist, overlay)
            if user_series is not None:
                fig_price.add_trace(go.Scatter(x=hist.index, y=user_series, mode='lines', name=f"{ticker} Custom Overlay", line=dict(dash='dot')))
        # --- Add event markers (annotations) ---
        for event in events:
            fig_price.add_shape(
                type="line",
                x0=event['date'], x1=event['date'],
                y0=hist['Close'].min(), y1=hist['Close'].max(),
                line=dict(color="red" if event['type']=="Earnings" else "blue", width=1, dash="dot"),
                xref="x", yref="y"
            )
            fig_price.add_annotation(
                x=event['date'],
                y=hist['Close'].max(),
                text=event['type'],
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
                bgcolor="white",
                bordercolor="black",
                font=dict(size=10, color="black"),
                hovertext=event['desc'],
                hoverlabel=dict(bgcolor="white")
            )
    fig_price.update_layout(
        title="Closing Prices & Indicator Overlays (Multi-Timeframe)",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white",
        margin=dict(l=40, r=40, t=40, b=20)
    )
    st.plotly_chart(fig_price, use_container_width=True)

    # --- RSI Chart ---
    if indicator == "RSI (14)":
        fig_rsi = go.Figure()
        for ticker, hist in data.items():
            fig_rsi.add_trace(go.Scatter(x=hist.index, y=add_rsi(hist, 14), mode='lines', name=f"{ticker} RSI(14)"))
        fig_rsi.update_layout(title="RSI (14) Comparison", xaxis_title="Date", yaxis_title="RSI", template="plotly_white", margin=dict(l=40, r=40, t=40, b=20), yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig_rsi, use_container_width=True)

    # --- MACD Chart ---
    if indicator == "MACD":
        fig_macd = go.Figure()
        for ticker, hist in data.items():
            macd, signal = add_macd(hist)
            fig_macd.add_trace(go.Scatter(x=hist.index, y=macd, mode='lines', name=f"{ticker} MACD"))
            fig_macd.add_trace(go.Scatter(x=hist.index, y=signal, mode='lines', name=f"{ticker} Signal"))
        fig_macd.update_layout(title="MACD Comparison", xaxis_title="Date", yaxis_title="MACD", template="plotly_white", margin=dict(l=40, r=40, t=40, b=20))
        st.plotly_chart(fig_macd, use_container_width=True)

    # --- Volume Chart: Trading Volume (Stacked) ---
    fig_volume = go.Figure()
    for ticker, hist in data.items():
        fig_volume.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name=ticker, marker_color=None))
    fig_volume.update_layout(barmode='stack', title="Trading Volume Comparison", xaxis_title="Date", yaxis_title="Volume", template="plotly_white", margin=dict(l=40, r=40, t=40, b=20))
    st.plotly_chart(fig_volume, use_container_width=True)
