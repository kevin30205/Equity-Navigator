from typing import Dict, Any
import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd


def create_portfolio_section(port_data: Dict[str, Any]) -> None:
    """
    Create the portfolio performance and allocation section.

    Parameters:
    port_data (dict): A dictionary containing historical stock data for portfolio tickers.

    Returns:
    None
    """
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