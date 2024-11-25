import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Sidebar for User Inputs
st.sidebar.title("Trade Signal Configurations")

# Currency Pair Selection
currency_pairs = {
    "XAUUSD": "GC=F",  # Gold futures
    "EURUSD": "EURUSD=X",  # Euro to USD Forex
    "GBPUSD": "GBPUSD=X",  # British Pound to USD Forex
    "USDJPY": "USDJPY=X",  # USD to Japanese Yen Forex
}
selected_pair = st.sidebar.selectbox("Select Currency Pair", list(currency_pairs.keys()))
ticker_symbol = currency_pairs[selected_pair]

# Account Balance and Lot Size Inputs
account_balance = st.sidebar.number_input("Account Balance (USD)", min_value=0.0, value=1000.0, step=100.0)
risk_percentage = st.sidebar.slider("Risk Percentage (%)", min_value=0, max_value=10, value=2)

# Function to calculate lot size
def calculate_lot_size(balance, risk_percent, entry_price, stop_loss):
    risk_amount = balance * (risk_percent / 100)
    pip_risk = abs(entry_price - stop_loss)
    lot_size = risk_amount / pip_risk
    return round(lot_size, 2)

# Fetch historical data using yfinance
def fetch_data(symbol, period="1d", interval="1m"):
    data = yf.download(tickers=symbol, period=period, interval=interval)
    data.reset_index(inplace=True)
    return data

# Generate Trade Signal
def generate_signal(data):
    # Example trading logic: Moving Average Crossover
    short_window = 10  # Short-term moving average
    long_window = 50  # Long-term moving average
    data["SMA10"] = data["Close"].rolling(window=short_window).mean()
    data["SMA50"] = data["Close"].rolling(window=long_window).mean()
    
    if data["SMA10"].iloc[-1] > data["SMA50"].iloc[-1]:  # Buy signal
        return "Buy", data["Close"].iloc[-1]
    else:  # Sell signal
        return "Sell", data["Close"].iloc[-1]

# Main Interface
st.title("Trade Signal Generator with yfinance")

# Fetch data and generate signal
data = fetch_data(ticker_symbol, period="5d", interval="15m")

if not data.empty:
    signal, entry_price = generate_signal(data)
    stop_loss = entry_price * 0.995  # Example: Stop loss 0.5% below entry
    lot_size = calculate_lot_size(account_balance, risk_percentage, entry_price, stop_loss)

    # Display Signal
    st.write(f"**{selected_pair} - {signal} Signal**")
    st.write(f"Entry Price: {entry_price}")
    st.write(f"Lot Size: {lot_size}")
    st.write(f"Stop Loss: {stop_loss}")

    # Chart Visualization
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data["Datetime"],
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Candlesticks"
    ))
    fig.add_trace(go.Scatter(
        x=data["Datetime"],
        y=data["SMA10"],
        mode="lines",
        name="SMA10"
    ))
    fig.add_trace(go.Scatter(
        x=data["Datetime"],
        y=data["SMA50"],
        mode="lines",
        name="SMA50"
    ))
    fig.add_trace(go.Scatter(
        x=[data["Datetime"].iloc[-1]],
        y=[entry_price],
        mode='markers+text',
        text=["Entry"],
        textposition="top center",
        name="Entry Point"
    ))
    st.plotly_chart(fig)

else:
    st.write("Failed to fetch data for the selected pair.")
