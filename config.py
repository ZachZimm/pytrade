# Strategy
import deviation_scalp_strat as strategy
strategy_arguments = [8, 245, 135, 1.0085] # length for deviation calc, reference SMA length, deviation lookback, profit target
trade_ticker = 'AVAXUSD'
trade_side_1 = 'AVAX'
trae_side_2 = 'USD'
tickers = ['XXBT', 'XETH', 'AVAX', 'USD']
interval = 300 # 5 minute candles

# App
port = 8080 # backend
debug = False