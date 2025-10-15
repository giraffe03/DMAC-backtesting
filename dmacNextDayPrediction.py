import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

## Substitute 'GC=F' with any ticker of your choice
data_raw = yf.download("GC=F", period="2y", progress=False, actions=True)

data_raw.columns = [col[0] for col in data_raw.columns]


data_raw['Dividends'] = data_raw['Dividends'].fillna(0)
data_raw['Stock Splits'] = data_raw['Stock Splits'].replace(0, 1)
 
data_raw = data_raw.sort_index(ascending=False)
cum_factor = data_raw['Stock Splits'].cumprod()
data_raw['Adj Close'] = data_raw['Close'] / cum_factor
data_raw = data_raw.sort_index(ascending=True)
data_raw['Adj Close'] = data_raw['Adj Close'] - (data_raw['Dividends'] / cum_factor)

 
data_raw.to_csv("GCF_data_with_adj_close.csv")


fig = px.line(data_raw, y='Adj Close', title='GOLD Adj Close Price', labels={'Adj Close':'Adj Close (USD)'})
fig.show()


window1, window2 = 7, 28
data_raw['SMA10'] = data_raw['Adj Close'].rolling(window=window1).mean()
data_raw['SMA50'] = data_raw['Adj Close'].rolling(window=window2).mean()


def dualMACrossover(df):
    buy_signals, sell_signals = [], []
    flag = -1
    for i in range(len(df)):
        if df['SMA10'][i] > df['SMA50'][i]:
            if flag != 1:
                buy_signals.append(df['Adj Close'][i])
                sell_signals.append(np.nan)
                flag = 1
            else:
                buy_signals.append(np.nan)
                sell_signals.append(np.nan)
        elif df['SMA10'][i] < df['SMA50'][i]:
            if flag != 0:
                buy_signals.append(np.nan)
                sell_signals.append(df['Adj Close'][i])
                flag = 0
            else:
                buy_signals.append(np.nan)
                sell_signals.append(np.nan)
        else:
            buy_signals.append(np.nan)
            sell_signals.append(np.nan)
    return buy_signals, sell_signals

buy_sell = dualMACrossover(data_raw)
data_raw['BuySignal'] = buy_sell[0]
data_raw['SellSignal'] = buy_sell[1]


fig = px.line(data_raw, y='Adj Close', title='Strategy Visualization', labels={'index':'Date'})
fig.add_scatter(x=data_raw.index, y=data_raw['SMA10'], mode='lines', name='SMA10')
fig.add_scatter(x=data_raw.index, y=data_raw['SMA50'], mode='lines', name='SMA50')
fig.add_trace(go.Scatter(mode="markers", x=data_raw.index, y=data_raw.BuySignal,
                         marker_symbol='triangle-up', marker_line_color="#000000",
                         marker_color="#000000", marker_line_width=2, marker_size=15, name='Buy'))
fig.add_trace(go.Scatter(mode="markers", x=data_raw.index, y=data_raw.SellSignal,
                         marker_symbol='triangle-down', marker_line_color="#E74C3C",
                         marker_color="#E74C3C", marker_line_width=2, marker_size=15, name='Sell'))
fig.show()


sma_data = data_raw.dropna(subset=['SMA10','SMA50'])

if len(sma_data) >= 2:
    latest = sma_data.iloc[-2:]  # last two valid rows
    if latest['SMA10'].iloc[-1] > latest['SMA50'].iloc[-1] and latest['SMA10'].iloc[-2] <= latest['SMA50'].iloc[-2]:
        print("Signal for tomorrow: BUY")
    elif latest['SMA10'].iloc[-1] < latest['SMA50'].iloc[-1] and latest['SMA10'].iloc[-2] >= latest['SMA50'].iloc[-2]:
        print("Signal for tomorrow: SELL")
    else:
        print("Signal for tomorrow: HOLD / No action")
else:
    print("Not enough data to generate a signal yet.")