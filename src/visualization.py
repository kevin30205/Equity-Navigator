from plotly import graph_objects as go
import streamlit as st
from typing import Dict, List, Tuple, Any
import pandas as pd

def create_volume_chart(data: Dict[str, Any]) -> None:
    """
    Create a volume chart using the provided data.

    Parameters:
    data (dict): A dictionary containing historical stock data.

    Returns:
    None
    """
    fig_volume = go.Figure()
    for ticker, hist in data.items():
        fig_volume.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name=ticker, marker_color=None))
    fig_volume.update_layout(barmode='stack', title="Trading Volume Comparison", xaxis_title="Date", yaxis_title="Volume", template="plotly_white", margin=dict(l=40, r=40, t=40, b=20))
    st.plotly_chart(fig_volume, use_container_width=True)


def add_macd_chart(data: Dict[str, Any], add_macd) -> None:
    """
    Create a MACD chart using the provided data.

    Parameters:
    data (dict): A dictionary containing historical stock data.
    add_macd (function): A function to calculate MACD.

    Returns:
    None
    """
    fig_macd = go.Figure()
    for ticker, hist in data.items():
        macd, signal = add_macd(hist)
        fig_macd.add_trace(go.Scatter(x=hist.index, y=macd, mode='lines', name=f"{ticker} MACD"))
        fig_macd.add_trace(go.Scatter(x=hist.index, y=signal, mode='lines', name=f"{ticker} Signal"))
    fig_macd.update_layout(title="MACD Comparison", xaxis_title="Date", yaxis_title="MACD", template="plotly_white", margin=dict(l=40, r=40, t=40, b=20))
    st.plotly_chart(fig_macd, use_container_width=True)


def add_rsi_chart(data: Dict[str, Any], add_rsi) -> None:
    """
    Create an RSI chart using the provided data.

    Parameters:
    data (dict): A dictionary containing historical stock data.
    add_rsi (function): A function to calculate RSI.

    Returns:
    None
    """
    fig_rsi = go.Figure()
    for ticker, hist in data.items():
        fig_rsi.add_trace(go.Scatter(x=hist.index, y=add_rsi(hist, 14), mode='lines', name=f"{ticker} RSI(14)"))
    fig_rsi.update_layout(title="RSI (14) Comparison", xaxis_title="Date", yaxis_title="RSI", template="plotly_white", margin=dict(l=40, r=40, t=40, b=20), yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig_rsi, use_container_width=True)


def create_price_chart(data: Dict[str, Any], chart_type: str, indicator: str, overlay: str, start_date: str, end_date: str,
                       add_sma, add_ema, add_bollinger, add_stochastic, add_atr, add_vwap, add_ichimoku, add_user_indicator,
                       get_stock_events) -> None:
    """
    Create a price chart with various indicators and overlays.

    Parameters:
    data (dict): A dictionary containing historical stock data.
    chart_type (str): The type of chart to create (e.g., "Line", "Area", "Candlestick").
    indicator (str): The technical indicator to overlay on the chart.
    overlay (str): A user-defined overlay indicator.
    start_date (str): The start date for the chart.
    end_date (str): The end date for the chart.
    add_sma (function): A function to calculate Simple Moving Average.
    add_ema (function): A function to calculate Exponential Moving Average.
    add_bollinger (function): A function to calculate Bollinger Bands.
    add_stochastic (function): A function to calculate Stochastic Oscillator.
    add_atr (function): A function to calculate Average True Range.
    add_vwap (function): A function to calculate Volume Weighted Average Price.
    add_ichimoku (function): A function to calculate Ichimoku Cloud.
    add_user_indicator (function): A function to calculate user-defined indicators.
    get_stock_events (function): A function to retrieve stock events.
    end_date (str): The end date for the chart.
    add_sma (function): A function to calculate Simple Moving Average.
    add_ema (function): A function to calculate Exponential Moving Average.
    add_bollinger (function): A function to calculate Bollinger Bands.
    add_stochastic (function): A function to calculate Stochastic Oscillator.
    add_atr (function): A function to calculate Average True Range.
    add_vwap (function): A function to calculate Volume Weighted Average Price.
    add_ichimoku (function): A function to calculate Ichimoku Cloud.
    add_user_indicator (function): A function to calculate user-defined indicators.
    get_stock_events (function): A function to retrieve stock events.

    Returns:
    None
    """
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

def display_key_metrics(data: Dict[str, Any], lang: str, t, timeframe: str, live_ticker, live_volume) -> pd.DataFrame:
    """
    Display key metrics for the provided stock data.

    Parameters:
    data (dict): A dictionary containing historical stock data.
    lang (str): Selected language code.
    t (function): Translation function.
    timeframe (str): Selected timeframe.
    live_ticker: Streamlit component for live ticker display.
    live_volume: Streamlit component for live volume display.

    Returns:
    pd.DataFrame: DataFrame containing key metrics.
    """
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

    return metrics_df
