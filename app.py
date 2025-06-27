import streamlit as st
import pandas as pd
import ccxt
import ta
import plotly.graph_objects as go

# Initialize Binance exchange for BTC/USDT data
exchange = ccxt.binance({'enableRateLimit': True})

SYMBOLS = {
    'BTC/USD': 'BTC/USDT',
    'GOLD (XAU/USD)': 'OANDA:XAUUSD',  # TradingView symbol for Gold
    'BTC': 'BTC/USDT',
}

TIMEFRAMES = ['5m', '15m']

@st.cache_data(ttl=60)
def fetch_ohlcv(symbol, timeframe='5m', limit=200):
    if symbol != 'BTC/USDT':
        return pd.DataFrame()
    try:
        data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        st.warning(f"Error fetching data: {str(e)}")
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

def tradingview_widget_embed(symbol="BINANCE:BTCUSDT", interval="5", width="100%", height=500):
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="width:{width}; height:{height}px;">
      <div id="tradingview_{symbol.replace(':','_')}"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "width": "100%",
        "height": {height},
        "symbol": "{symbol}",
        "interval": "{interval}",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_top_toolbar": true,
        "save_image": false,
        "container_id": "tradingview_{symbol.replace(':','_')}"
      }}
      );
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    st.components.v1.html(widget_html, height=height, scrolling=False)

def main():
    st.title("Live BTC/USD, GOLD, BTC Trading Signals & Charts")

    symbol_name = st.selectbox("Select Symbol:", list(SYMBOLS.keys()))
    symbol = SYMBOLS[symbol_name]

    timeframe = st.selectbox("Select Timeframe:", TIMEFRAMES)

    interval_numeric = timeframe.replace('m', '')  # e.g. '5' or '15' for TradingView widget

    if symbol_name == 'GOLD (XAU/USD)':
        st.subheader(f"Live TradingView Chart for {symbol_name}")
        tradingview_widget_embed(symbol=symbol, interval=interval_numeric, height=500)
        st.info("Signal generation not supported for GOLD (XAU/USD) due to data source limitations.")
    else:
        df = fetch_ohlcv(symbol, timeframe, limit=200)
        if df.empty:
            st.error("Failed to fetch price data.")
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

        fig.update_layout(title=f"{symbol_name} Price Chart with EMA", xaxis_title="Time", yaxis_title="Price")
        st.plotly_chart(fig, use_container_width=True)

        st.write("Latest Price Data Snapshot:")
        st.dataframe(df.tail(5))

        st.subheader("TradingView Chart (live data & tools)")
        tradingview_widget_embed(symbol="BINANCE:BTCUSDT", interval=interval_numeric, height=500)

if __name__ == "__main__":
    main()
