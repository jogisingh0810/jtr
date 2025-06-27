import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import plotly.graph_objects as go

# Supported symbols
SYMBOLS = {
    'BTC/USD': 'BTC-USD',
    'GOLD (XAU/USD)': 'XAUUSD=X',
}

TIMEFRAMES = {
    '5m': '5m',
    '15m': '15m',
}

@st.cache_data(ttl=60)
def fetch_yfinance_data(symbol, interval='5m', period='1d'):
    try:
        df = yf.download(tickers=symbol, interval=interval, period=period, progress=False)
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        df.index.name = 'timestamp'
        return df
    except Exception as e:
        st.warning(f"Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()

def add_indicators(df):
    if df.empty:
        return df
    df['EMA20'] = ta.trend.ema_indicator(df['close'], window=20)
    df['EMA50'] = ta.trend.ema_indicator(df['close'], window=50)
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)
    macd = ta.trend.MACD(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    return df

def generate_signal(df):
    if df.empty or len(df) < 2:
        return 'No data'
    last = df.iloc[-1]
    prev = df.iloc[-2]
    macd_cross_up = (prev['MACD'] < prev['MACD_signal']) and (last['MACD'] > last['MACD_signal'])
    macd_cross_down = (prev['MACD'] > prev['MACD_signal']) and (last['MACD'] < last['MACD_signal'])
    if (last['EMA20'] > last['EMA50']) and (last['RSI'] < 70) and macd_cross_up:
        return 'Buy'
    elif (last['EMA20'] < last['EMA50']) and (last['RSI'] > 30) and macd_cross_down:
        return 'Sell'
    else:
        return 'Hold'

def main():
    st.title("Live BTC/USD & GOLD (XAU/USD) Trading Signals with yFinance")

    symbol_name = st.selectbox("Select Symbol:", list(SYMBOLS.keys()))
    timeframe = st.selectbox("Select Timeframe:", list(TIMEFRAMES.keys()))
    yf_symbol = SYMBOLS[symbol_name]
    yf_interval = TIMEFRAMES[timeframe]

    df = fetch_yfinance_data(yf_symbol, interval=yf_interval)

    if df.empty:
        st.error("Failed to fetch data.")
        return

    df = add_indicators(df)
    signal = generate_signal(df)

    st.subheader(f"Latest Signal for {symbol_name} on {timeframe}: {signal}")

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['open'], high=df['high'],
        low=df['low'], close=df['close'],
        name='Price')])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], mode='lines', name='EMA20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], mode='lines', name='EMA50'))
    fig.update_layout(title=f"{symbol_name} Price Chart", xaxis_title="Time", yaxis_title="Price")

    st.plotly_chart(fig, use_container_width=True)
    st.write("Latest Price Data Snapshot:")
    st.dataframe(df.tail(5))

if __name__ == "__main__":
    main()
