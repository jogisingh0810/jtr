import streamlit as st
import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator

st.set_page_config(layout="wide")

st.title("Joginder Singh's Trading Dashboard")

symbol = st.selectbox("Select Symbol", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X"])
df = yf.download(symbol, interval="5m", period="1d")

# Calculate indicators
from ta.trend import EMAIndicator
df["Close"] = df["Close"].squeeze()
ema20 = pd.Series(EMAIndicator(close=df["Close"], window=20).ema_indicator().values.ravel(), name="EMA20")
df["EMA20"] = ema20
ema50 = pd.Series(EMAIndicator(close=df["Close"], window=20).ema_indicator().values.ravel(), name="EMA50")
df["EMA50"] = ema50
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
