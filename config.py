# Strategy
import deviation_scalp_strat as strategy
# AVAX [8 #20, 245 #210, 135 #155, 1.0085]
# SOL [8, 225, 155, 1.009]
# ETH [20, 215, 130, 1.0085]
# bad? strategy_arguments = [20, 210, 155, 1.0085, 19]
# 6month bad? strategy_arguments = [18, 200, 100, 1.015, 19] #1.2, 2.6]
strategy_arguments = [74, 202, 360, 1.11, 9] #, 10.5, 2.8]
# length for deviation calc, reference SMA length, deviation lookback, profit target, min/max lookback
trailing_exit_args = [.05,.95]
trade_ticker = 'ETHUSD'
trade_side_1 = 'ETH'
trae_side_2 = 'USD'
tickers = ['XXBT', 'XETH', 'AVAX', 'USD']
interval = 300 # 300 seconds, 5 minute candles
long_thresh = 0.10

# App
debug = False

# Web
port = 8080 # backend
recent_data_length = 500
