"""
i18n.py
Internationalization support for Equity Navigator.
"""

from typing import Dict

# Supported languages
LANGUAGES = {
    "en": "English",
    "zh": "中文",
    "es": "Español"
}

# Translation dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "title": "📈 Stock Dashboard",
        "ticker_input": "Enter Stock Ticker(s) (comma or space separated, e.g., AAPL, TSLA, MSFT)",
        "start_date": "Start Date",
        "end_date": "End Date",
        "indicator": "Technical Indicator",
        "chart_type": "Chart Type",
        "submit": "Go",
        "key_metrics": "Key Metrics",
        "current_close": "Current Close",
        "pct_change": "% Change",
        "high_low": "High / Low",
        "download_data": "Download Data",
        "download_key_metrics": "Download Key Metrics as CSV",
        "download_history": "Download {ticker} Historical Data as CSV",
        "error_no_data": "No valid tickers or no data available for selected range.",
        "sma": "SMA (20)",
        "ema": "EMA (20)",
        "rsi": "RSI (14)",
        "macd": "MACD",
        "bollinger": "Bollinger Bands (20)",
    "line": "Line",
    "candlestick": "Candlestick",
    "area": "Area",
    "Daily": "Daily",
    "Weekly": "Weekly",
    "Monthly": "Monthly",
    "Intraday": "Intraday"
    },
    "zh": {
        "title": "📈 股票儀表板",
        "ticker_input": "輸入股票代碼（以逗號或空格分隔，例如：AAPL, TSLA, MSFT）",
        "start_date": "開始日期",
        "end_date": "結束日期",
        "indicator": "技術指標",
        "chart_type": "圖表類型",
        "submit": "查詢",
        "key_metrics": "主要指標",
        "current_close": "最新收盤價",
        "pct_change": "漲跌幅",
        "high_low": "最高 / 最低",
        "download_data": "下載資料",
        "download_key_metrics": "下載主要指標 CSV",
        "download_history": "下載 {ticker} 歷史資料 CSV",
        "error_no_data": "無有效股票代碼或所選區間無資料。",
        "sma": "SMA (20)",
        "ema": "EMA (20)",
        "rsi": "RSI (14)",
        "macd": "MACD",
        "bollinger": "布林通道 (20)",
    "line": "線圖",
    "candlestick": "K線圖",
    "area": "面積圖",
    "Daily": "日線",
    "Weekly": "週線",
    "Monthly": "月線",
    "Intraday": "即時"
    },
    "es": {
        "title": "📈 Panel de Acciones",
        "ticker_input": "Ingrese los símbolos de acciones (separados por coma o espacio, ej.: AAPL, TSLA, MSFT)",
        "start_date": "Fecha de inicio",
        "end_date": "Fecha de fin",
        "indicator": "Indicador técnico",
        "chart_type": "Tipo de gráfico",
        "submit": "Buscar",
        "key_metrics": "Métricas clave",
        "current_close": "Cierre actual",
        "pct_change": "% Cambio",
        "high_low": "Alto / Bajo",
        "download_data": "Descargar datos",
        "download_key_metrics": "Descargar métricas clave CSV",
        "download_history": "Descargar historial de {ticker} CSV",
        "error_no_data": "No hay símbolos válidos o datos disponibles para el rango seleccionado.",
        "sma": "SMA (20)",
        "ema": "EMA (20)",
        "rsi": "RSI (14)",
        "macd": "MACD",
        "bollinger": "Bandas de Bollinger (20)",
    "line": "Línea",
    "candlestick": "Velas",
    "area": "Área",
    "Daily": "Diario",
    "Weekly": "Semanal",
    "Monthly": "Mensual",
    "Intraday": "Intradía"
    }
}