# Strategy
import deviation_scalp_strat as strategy
# AVAX [8 #20, 245 #210, 135 #155, 1.0085]
# SOL [8, 225, 155, 1.009]
# ETH [20, 215, 130, 1.0085]
strategy_arguments = [20, 210, 155, 1.01] # length for deviation calc, reference SMA length, deviation lookback, profit target
trade_ticker = 'AVAXUSD'
trade_side_1 = 'AVAX'
trae_side_2 = 'USD'
tickers = ['XXBT', 'XETH', 'AVAX', 'USD']
interval = 300 # 300 seconds, 5 minute candles

# App
debug = False

# Web
port = 8080 # backend
recent_data_length = 500
