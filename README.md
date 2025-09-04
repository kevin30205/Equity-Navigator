# Equity Navigator

## Description

The Equity Navigator is a web application that enables users to fetch and visualize historical stock data interactively. Users can input a stock ticker, select a date range, and view key metrics and a line chart of closing prices. The dashboard is designed for simplicity, speed, and clarity, making it ideal for quick stock performance overviews.

## Features

- Input a stock ticker symbol to view historical data
- Select a custom date range
- Display key metrics: current closing price, percentage change, high/low
- Interactive line chart of daily closing prices

## Technology Stack

- **Frontend & Backend:**
  - Python 3.8+
  - Streamlit >=1.30.0
- **Data Fetching:**
  - yfinance >=0.2.36
- **Visualization:**
  - plotly >=5.20.0

## Project Architecture

The application is a single-page Streamlit app. User inputs are processed in real-time, data is fetched from Yahoo Finance via yfinance, and results are displayed using Streamlit widgets and Plotly charts. All logic is contained in a single Python script (`app.py`).

## Project Structure

```
./Equity Navigator
├── app.py
├── LICENSE
├── README.md
└── requirements.txt
```

- **app.py**: Main Streamlit application script. Implements the dashboard logic, user interface, and data visualization.
- **README.md**: Project documentation. Provides an overview, setup instructions, and usage guidelines.
- **requirements.txt**: Lists Python dependencies required to run the application.
