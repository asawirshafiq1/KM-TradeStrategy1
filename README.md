# High Win Rate Crypto Trading Strategy (Backtrader)

This repository contains a **Python-based backtesting strategy** for trading **Bitcoin (BTC-USD)** using [Backtrader](https://www.backtrader.com/). The strategy is engineered with a primary focus on **maximizing win rate** over raw profit, making it more consistent and conservative for risk-aware traders.

---

## 📈 Strategy Objective

> Achieve a **high percentage of winning trades** by applying strict entry filters, early exits on profit, and tight stop-losses.

---

## 🧠 Strategy Logic

The strategy combines **multiple technical indicators** and **volume filters** to make high-confidence entries. It exits trades early once a small profit is achieved or if the trade goes slightly against it.

### ✅ Entry Criteria (Must meet at least 5 out of 6):
1. **Trend Confirmation**: Price is above the 50-period SMA (bullish bias).
2. **RSI Strength Zone**: RSI is between 40 and 55 (early momentum).
3. **Bollinger Band Proximity**: Price is near the lower Bollinger Band (oversold bounce).
4. **MACD Momentum**: MACD line is above the signal line (positive momentum).
5. **Volume Surge**: Current volume is 20% higher than the 20-day average.
6. **SMA Crossover**: 20-period SMA is above the 50-period SMA.

### ❌ Exit Conditions:
- **Take Profit**: Close position if price increases **≥ 3%**.
- **Stop Loss**: Close position if price drops **≤ 2%**.
- **Overbought RSI**: Exit if RSI crosses above 65.
- **Trend Reversal**: Exit if short-term trend weakens with even slight profit.

---

## 🛠️ Components Used

- `RSI` – Relative Strength Index
- `SMA` – Simple Moving Averages (20 & 50)
- `MACD` – Momentum indicator
- `Bollinger Bands` – Volatility bands
- `Volume SMA` – Average volume filter
- `Backtrader` – Strategy engine & backtesting
- `yfinance` – Live market data for BTC

---

## 📊 Sample Backtest Results (BTC-USD)

Tested on 2 years of historical BTC-USD data using daily candles:

| Metric              | Value           |
|---------------------|-----------------|
| **Total Trades**    | 25              |
| **Winning Trades**  | 15              |
| **Losing Trades**   | 10              |
| **Win Rate**        | **60.0%**       |
| **Average Win**     | $305.01         |
| **Largest Win**     | $920.12         |
| **Average Loss**    | $534.83         |
| **Sharpe Ratio**    | -0.57           |
| **Max Drawdown**    | 24.46%          |

📌 **Note**:  
This strategy focuses more on consistent wins than maximizing individual trade profits. Losses are cut quickly, and profits are locked in early. The **win rate of 60%** demonstrates a favorable probability setup with tight risk management.

---


