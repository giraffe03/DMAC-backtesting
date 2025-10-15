Dual Moving Avg Trader — SMA Crossover Backtest & Visualizer

A very simple yet complete algorithmic trading project that implements and backtests a dual moving average (SMA) crossover strategy in Python. The project uses historical market data from Yahoo Finance and visualizes buy/sell signals with Plotly.

🚀 Overview

Data retrieval and cleaning with yfinance (auto-adjusted for splits/dividends)
Strategy logic for dual moving average crossover (short SMA vs. long SMA)
Interactive visualization of signals and moving averages using plotly
Backtesting of the strategy using backtesting.py, producing performance metrics

🧠 Strategy Logic

Buy Signal: When the short-term SMA crosses above the long-term SMA
Sell Signal: When the short-term SMA crosses below the long-term SMA
Default parameters: Short = 10 days, Long = 50 days
Example ticker: GC=F (Gold Futures), but you can easily change it with the choice variable

⚙️ Requirements

Install dependencies:

``` pip install numpy pandas matplotlib plotly yfinance backtesting```

▶️ How to Run

Clone this repo and open the script or notebook.
Set your desired ticker in the code (e.g., choice = 'AAPL').
Run the script — it will:
Download 2 years of data
Compute SMAs and generate buy/sell signals
Visualize the results
Backtest and print performance stats

📊 Example Output

Interactive chart showing price, moving averages, and buy/sell markers
Backtest results (CAGR, Sharpe ratio, drawdown, win rate)
Exported CSV file with adjusted-close prices and signals
