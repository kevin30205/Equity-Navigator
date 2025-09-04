"""
Equity Navigator
A web application for visualizing historical stock data.
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from datetime import date
from typing import Optional, Tuple