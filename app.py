import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(layout="wide")

st.title("Joginder Singh's Trading Dashboard")

symbol = st.selectbox("Select Symbol", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X"])
df = yf.download(symbol, interval="5m", period="1d")

# Calculate indicators
df["EMA20"] = ta.trend.ema_indicator(df["Close"], window=20).ema_indicator()
df["EMA50"] = ta.trend.ema_indicator(df["Close"], window=50).ema_indicator()
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
