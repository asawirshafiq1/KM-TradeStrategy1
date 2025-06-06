import backtrader as bt
import pandas as pd
import datetime
import yfinance as yf

class HighWinRateStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
        ('sma_short', 20),
        ('sma_long', 50),
        ('stop_loss_pct', 0.05),  # 5% stop loss
        ('take_profit_pct', 0.08), # 8% take profit
    )

    def __init__(self):
        # Indicators
        self.rsi = bt.ind.RSI(period=self.params.rsi_period)
        self.sma_short = bt.ind.SMA(period=self.params.sma_short)
        self.sma_long = bt.ind.SMA(period=self.params.sma_long)
        self.bb = bt.ind.BollingerBands(period=20, devfactor=2)
        self.macd = bt.ind.MACD()
        self.volume_sma = bt.ind.SMA(self.data.volume, period=20)
        
        # Trade tracking
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        self.trade_count = 0
        self.win_count = 0

    def next(self):
        # Cancel any pending orders
        if self.order:
            return
        
        # Skip if we don't have enough data
        if len(self.data) < self.params.sma_long:
            return
            
        current_price = self.data.close[0]
        
        # Entry conditions (multiple confirmations for higher win rate)
        if not self.position:
            # Bull market condition: price above long SMA
            trend_up = current_price > self.sma_long[0]
            
            # RSI oversold but not extreme
            rsi_good = 35 < self.rsi[0] < 50
            
            # Price near lower Bollinger Band (potential bounce)
            bb_signal = current_price <= self.bb.lines.bot[0] * 1.02
            
            # MACD showing momentum
            macd_signal = self.macd.macd[0] > self.macd.signal[0]
            
            # Volume confirmation
            volume_good = self.data.volume[0] > self.volume_sma[0] * 1.1
            
            # Short SMA above long SMA (trend confirmation)
            sma_trend = self.sma_short[0] > self.sma_long[0]
            
            # Buy only if multiple conditions met (high probability setup)
            conditions_met = sum([trend_up, rsi_good, bb_signal, macd_signal, volume_good, sma_trend])
            
            if conditions_met >= 4:  # Require at least 4 out of 6 conditions
                cash_available = self.broker.get_cash() * 0.95
                size_to_buy = cash_available / current_price
                self.order = self.buy(size=size_to_buy)
                self.buy_price = current_price
                self.trade_count += 1
                print(f'BUY #{self.trade_count}: ${current_price:.2f} - Conditions: {conditions_met}/6')
                print(f'  RSI: {self.rsi[0]:.1f}, Vol: {volume_good}, Trend: {trend_up}')
        
        else:
            # Exit conditions
            profit_pct = (current_price - self.buy_price) / self.buy_price
            
            # Take profit
            if profit_pct >= self.params.take_profit_pct:
                self.order = self.close()
                print(f'TAKE PROFIT: ${current_price:.2f} (+{profit_pct*100:.1f}%)')
            
            # Stop loss
            elif profit_pct <= -self.params.stop_loss_pct:
                self.order = self.close()
                print(f'STOP LOSS: ${current_price:.2f} ({profit_pct*100:.1f}%)')
            
            # RSI overbought exit
            elif self.rsi[0] > self.params.rsi_overbought:
                self.order = self.close()
                print(f'RSI EXIT: ${current_price:.2f} (RSI: {self.rsi[0]:.1f})')
            
            # Trend reversal exit
            elif (current_price < self.sma_short[0] and 
                  self.sma_short[0] < self.sma_long[0] and
                  profit_pct > 0.02):  # Only if we have some profit
                self.order = self.close()
                print(f'TREND EXIT: ${current_price:.2f} (+{profit_pct*100:.1f}%)')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
                print(f'BUY EXECUTED: ${order.executed.price:.2f}')
            else:
                profit = order.executed.price - self.buy_price - self.buy_comm - order.executed.comm
                if profit > 0:
                    self.win_count += 1
                print(f'SELL EXECUTED: ${order.executed.price:.2f}, P&L: ${profit:.2f}')
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print(f'Order {order.status}')
        
        self.order = None

    def stop(self):
        win_rate = (self.win_count / self.trade_count * 100) if self.trade_count > 0 else 0
        print(f'\nFinal Stats: {self.win_count}/{self.trade_count} wins = {win_rate:.1f}%')

# Load and prepare data
def run_strategy():
    # Get 2 years of data for better testing
    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=365)
    
    print(f"Downloading BTC data from {start_date.date()} to {end_date.date()}")
    btc_df = yf.download('BTC-USD', start=start_date, end=end_date, auto_adjust=False)
    
    # Fix column names
    if btc_df.columns.nlevels > 1:
        btc_df.columns = btc_df.columns.get_level_values(0)
    
    btc_df = btc_df[['Open', 'High', 'Low', 'Close', 'Volume']]
    btc_df.dropna(inplace=True)
    
    print(f"Data loaded: {btc_df.shape[0]} days")
    
    # Create cerebro
    cerebro = bt.Cerebro()
    cerebro.addstrategy(HighWinRateStrategy)
    
    # Add data
    data = bt.feeds.PandasData(dataname=btc_df)
    cerebro.adddata(data)
    
    # Set up broker
    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.001)
    
    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    
    # Run backtest
    print(f'\nStarting Portfolio Value: ${cerebro.broker.getvalue():.2f}')
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()
    
    print(f'Final Portfolio Value: ${final_value:.2f}')
    print(f'Total Return: {((final_value - 10000) / 10000) * 100:.2f}%')
    
    # Detailed analysis
    strat = results[0]
    trade_analysis = strat.analyzers.trades.get_analysis()
    
    print(f"\n=== DETAILED TRADE ANALYSIS ===")
    if 'total' in trade_analysis:
        total_trades = trade_analysis.total.total
        won_trades = trade_analysis.won.total if 'won' in trade_analysis else 0
        lost_trades = trade_analysis.lost.total if 'lost' in trade_analysis else 0
        win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0
        
        print(f"Total Trades: {total_trades}")
        print(f"Winning Trades: {won_trades}")
        print(f"Losing Trades: {lost_trades}")
        print(f'Win Rate: {win_rate:.1f}%')
        
        if 'won' in trade_analysis:
            print(f"Average Win: ${trade_analysis.won.pnl.average:.2f}")
            print(f"Largest Win: ${trade_analysis.won.pnl.max:.2f}")
        
        if 'lost' in trade_analysis:
            print(f"Average Loss: ${trade_analysis.lost.pnl.average:.2f}")
            if 'lost' in trade_analysis and 'pnl' in trade_analysis.lost and 'min' in trade_analysis.lost.pnl:
                print(f"Largest Loss: ${trade_analysis.lost.pnl.min:.2f}")
            else:
                print("Largest Loss: N/A (no losing trades)")
    
    # Sharpe ratio
    sharpe = strat.analyzers.sharpe.get_analysis()
    if 'sharperatio' in sharpe and sharpe['sharperatio'] is not None:
        print(f"Sharpe Ratio: {sharpe['sharperatio']:.2f}")
    
    # Max drawdown
    drawdown = strat.analyzers.drawdown.get_analysis()
    if 'max' in drawdown:
        print(f"Max Drawdown: {drawdown['max']['drawdown']:.2f}%")
    
    # Plot results
    cerebro.plot(style='candlestick', barup='green', bardown='red')
    
    return win_rate

# Run the strategy
if __name__ == '__main__':
    win_rate = run_strategy()