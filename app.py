import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np  # ✅ Add this
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator


st.set_page_config(layout="wide")

st.title("Joginder Singh's Trading Dashboard")

symbol = st.selectbox("Select Symbol", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X"])
df = yf.download(symbol, interval="5m", period="1d")

# Calculate indicators
from ta.trend import EMAIndicator
df["Close"] = df["Close"].squeeze()
ema20 = df["Close"].ewm(span=20, adjust=False).mean()
if isinstance(ema20.values, np.ndarray) and ema20.values.ndim > 1:
    ema20 = pd.Series(ema20.values.flatten(), index=df.index, name="EMA20")
ema20 = pd.Series(EMAIndicator(close=df["Close"], window=20).ema_indicator().values.ravel(), name="EMA20")
df["EMA20"] = ema20
ema50 = df["Close"].ewm(span=50, adjust=False).mean()
if isinstance(ema50.values, np.ndarray) and ema50.values.ndim > 1:
    ema50 = pd.Series(ema50.values.flatten(), index=df.index, name="EMA50")
ema50 = pd.Series(EMAIndicator(close=df["Close"], window=20).ema_indicator().values.ravel(), name="EMA50")
df["EMA50"] = ema50
rsi = RSIIndicator(close=df["Close"], window=14).rsi()
if isinstance(rsi.values, np.ndarray) and rsi.values.ndim > 1:
    rsi = pd.Series(rsi.values.flatten(), index=df.index, name="RSI")
df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()

# Display chart
st.line_chart(df[["Close", "EMA20", "EMA50"]])

# Signal logic
latest = df.iloc[-1]
signal = ""
if latest["RSI"] < 30 and latest["EMA20"] > latest["EMA50"]:
    signal = "Buy Signal"
elif latest["RSI"] > 70 and latest["EMA20"] < latest["EMA50"]:
    signal = "Sell Signal"
else:
    signal = "No Clear Signal"

st.subheader(f"Signal: {signal}")
