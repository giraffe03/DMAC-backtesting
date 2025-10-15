import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA


choice = 'AAPL'
data_raw = yf.download(choice, period="2y", progress=False, actions=True)


data_raw.columns = [col[0] for col in data_raw.columns] # 'Close", 'Dividends', etc


data_raw['Dividends'] = data_raw['Dividends'].fillna(0)
data_raw['Stock Splits'] = data_raw['Stock Splits'].replace(0, 1)  # 0 means no split

data_raw = data_raw.sort_index(ascending=False)  # newest first
cum_factor = (data_raw['Stock Splits']).cumprod()
data_raw['Adj Close'] = data_raw['Close'] / cum_factor  # adjust Close for splits
data_raw = data_raw.sort_index(ascending=True)  # back to chronological order

data_raw['Adj Close'] = data_raw['Adj Close'] - (data_raw['Dividends'] / cum_factor)


data_raw.to_csv(f"{choice}_data_with_adj_close.csv")

print(data_raw.columns)


fig = px.line(data_raw, y='Adj Close', title='{} Close Price'.format(choice), labels={'Adj Close':'{} Adj Close (USD)'.format(choice)})
fig.show()



window1 = 10
sma1 = pd.DataFrame()
sma1['Adj Close'] = data_raw['Adj Close'].rolling(window = window1).mean()
sma1

window2 = 50
sma2 = pd.DataFrame()
sma2['Adj Close'] = data_raw['Adj Close'].rolling(window = window2).mean()
sma2


fig.add_scatter(x=sma1.index,y=sma1['Adj Close'], mode='lines',name='SMA'+str(window1))
fig.add_scatter(x=sma2.index,y=sma2['Adj Close'], mode='lines',name='SMA'+str(window2))
fig.show()


data = pd.DataFrame()
data['Price'] = data_raw['Adj Close']
data['SMA'+str(window1)] = sma1['Adj Close']
data['SMA'+str(window2)] = sma2['Adj Close']

def dualMACrossover(data):
    sigPriceBuy = []
    sigPriceSell = []
    flag = -1 # Flag denoting when the 2 moving averages crossed each other
    for i in range(len(data)):
        if data['SMA'+str(window1)][i] > data['SMA'+str(window2)][i]:
            if flag != 1:
                sigPriceBuy.append(data['Price'][i])
                sigPriceSell.append(np.nan)
                flag = 1
            else:
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(np.nan)
        elif data['SMA'+str(window1)][i] < data['SMA'+str(window2)][i]:
            if flag!=0:
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(data['Price'][i])
                flag=0
            else:
                sigPriceBuy.append(np.nan)
                sigPriceSell.append(np.nan)
        else:
            sigPriceBuy.append(np.nan)
            sigPriceSell.append(np.nan)
    return (sigPriceBuy,sigPriceSell)

buy_sell = dualMACrossover(data)
data['BuySignalPrice'] = buy_sell[0]
data['SellSignalPrice'] = buy_sell[1]

fig = px.line(data, y='Price', title='Strategy Visualization', labels = {'index':'Date'})
fig.add_scatter(x=data.index,y=data['SMA'+str(window1)], mode='lines',name='SMA'+str(window1))
fig.add_scatter(x=data.index,y=data['SMA'+str(window2)], mode='lines',name='SMA'+str(window2))

fig.add_trace(go.Scatter(mode="markers", x=data.index, y=data.BuySignalPrice, marker_symbol='triangle-up',
                           marker_line_color="#000000", marker_color="#000000", 
                           marker_line_width=2, marker_size=15, name='Buy'))

fig.add_trace(go.Scatter(mode="markers", x=data.index, y=data.SellSignalPrice, marker_symbol='triangle-down',
                           marker_line_color="#E74C3C", marker_color="#E74C3C", 
                           marker_line_width=2, marker_size=15, name='Sell'))
fig.show()


class DualMACrossover(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, window1)
        self.ma2 = self.I(SMA, price, window2)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()


bt = Backtest(data_raw, DualMACrossover,
              exclusive_orders=True)
stats = bt.run()
bt.plot()

print(stats)