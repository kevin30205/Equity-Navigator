"""
stock_events.py
Module for fetching and formatting significant stock events (earnings, splits) for annotation on charts.
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Any