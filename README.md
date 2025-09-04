# Equity Navigator

## Description

The Equity Navigator is a web application that enables users to fetch and visualize historical stock data interactively. Users can input a stock ticker, select a date range, and view key metrics and a line chart of closing prices. The dashboard is designed for simplicity, speed, and clarity, making it ideal for quick stock performance overviews.

## Features

- Input a stock ticker symbol to view historical data
- Select a custom date range
- Display key metrics: current closing price, percentage change, high/low
- Interactive line chart of daily closing prices
- Volume Chart: Bar chart of trading volume for the selected date range
- Multiple Ticker Comparison: Input and compare multiple stock tickers on the same chart
- Advanced Technical Indicators: SMA, EMA, RSI, MACD, Bollinger Bands, Stochastic Oscillator, ATR, VWAP, Ichimoku Cloud
- Multi-Timeframe Analysis: Analyze data in daily, weekly, monthly, and intraday intervals
- Real-Time & Intraday Data: Live price updates, intraday charting, and streaming volume display
- Live Ticker Panel: Sidebar shows live prices and streaming volume for selected tickers
- Portfolio Management: Create and track virtual portfolios, view performance, allocation, and risk metrics
- Custom Overlays: Add user-defined indicator formulas using pandas syntax
- Asset Class Comparison: Compare stocks and ETFs on the same chart
- Download Data: Download displayed key metrics and historical data as CSV files
- Customizable Chart Types: Choose between line, candlestick, or area charts for price visualization

## Technology Stack

- **Frontend & Backend:**
  - Python 3.8+
  - Streamlit >=1.30.0
- **Data Fetching:**
  - yfinance >=0.2.36
- **Visualization:**
  - plotly >=5.20.0
- **Technical Analysis:**
  - pandas_ta >=0.3.14

## Project Architecture

The application is a single-page Streamlit app. User inputs are processed in real-time, data is fetched from Yahoo Finance via yfinance, and results are displayed using Streamlit widgets and Plotly charts. All logic is contained in a single Python script (`app.py`).

Key components:

- **Data Fetching:** Retrieves historical data for stocks and ETFs using yfinance, supporting multiple tickers and timeframes (daily, weekly, monthly, intraday).
- **Analytics & Charting:** Calculates and overlays technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, Stochastic Oscillator, ATR, VWAP, Ichimoku Cloud) and supports user-defined formulas. Comparison charts allow analysis across asset classes.
- **Visualization:** Interactive charts (line, candlestick, area) and volume bar charts for selected tickers and timeframes. Event annotations (earnings, splits) are displayed on price charts.
- **User Interface:** Streamlit widgets for input, indicator selection, timeframe, overlays, and downloads. Multi-language support via i18n.

## Project Structure

```
./Equity-Navigator
├── app.py
├── i18n.py
├── indicators.py
├── LICENSE
├── README.md
├── requirements.txt
└── stock_events.py
```

- **app.py**: Main Streamlit application script. Implements the dashboard logic, user interface, and data visualization.
- **i18n.py**: Internationalization and language support.
- **indicators.py**: Implements advanced technical indicators and user-defined overlays.
- **stock_events.py**: Fetches and formats significant stock events for chart annotation.
- **README.md**: Project documentation. Provides an overview, setup instructions, and usage guidelines.
- **requirements.txt**: Lists Python dependencies required to run the application.

## Installation

1. Install dependencies:

   ```bash
    conda create --name equity_navigator python=3.10
    conda activate equity_navigator

    pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:

```bash
streamlit run app.py
```

2. Open the provided local URL in your browser.
3. Enter one or more stock tickers (comma or space separated), select dates, and click "Go" to view results.
4. The dashboard will display a table of key metrics for all valid tickers, a closing price comparison chart, and a stacked trading volume bar chart for the selected date range.
5. Select a technical indicator from the dropdown to overlay moving averages or display RSI, MACD, or Bollinger Bands for the selected tickers.
6. Use the download buttons to export key metrics and historical data for all selected tickers as CSV files.
7. Select a chart type (line, candlestick, or area) to customize the price visualization for all selected tickers.
8. **Portfolio Management:**

- Use the sidebar to add tickers and quantities to your virtual portfolio.
- View your current portfolio, allocation pie chart, total value, and risk metrics (volatility, beta).
- Clear the portfolio at any time using the sidebar button.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
