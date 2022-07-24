import sys
import io
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime, tzinfo
import pytz
import websocket
from websocket import create_connection
import _thread
import time
import json
import config as config
import deviation_scalp_strat as strategy

class OHLC:
    def __init__(self, ticker):
        self.ticker = ticker
        self.open = 0.0
        self.high = 0.0
        self.low = sys.float_info.max
        self.close = 0.0
        self.volume = 0.0
        self.trades = 0
        try:
            self.history = pd.read_csv('data/' + ticker + '.csv', index_col=0) # If there is old data, use that
        except:                                                                 # Otherwise, create the dataframe from scratch
            print('Failed to use old data for ' + ticker + ', starting a new database instead.')
            self.history = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Trades'])
            self.history.set_index('Date')
        self.time = datetime.now(tz=pytz.UTC)
        self.prev_close = 0.0
        self.no_trades = True
    
    def new_data(self, data):
        if(data > self.high or self.high == 0.0):
            self.high = data
        if(data < self.low or self.low == 0.0):
            self.low = data
        if(self.open == 0.0):
            self.open = data
        self.close = data
        self.trades = self.trades + 1
        self.no_trades = False # Why do I need a bool? Can't I just check if (self.trades == 0) ?
    
    def new_candle(self, _datetime):
        self.close_time = _datetime.strftime("%Y-%m-%d %H:%M:%S") # Yikes, compatability issues will likely stem from such a change TODO read and write date like this, get rid of the unnamed index column
        if(self.no_trades):
            self.open = self.prev_close
            self.close = self.prev_close
            self.low = self.prev_close
            self.high = self.prev_close
            
        if(self.close != 0.0): # If this is the first candle and there were no trades, it's probably better to skip the candle than to record and plot 0
            new_candle = pd.Series([_datetime, self.open, self.high, self.low, self.close, self.volume, self.trades], index=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Trades'])
            self.history.loc[_datetime] = new_candle

        self.open = 0.0 # Reset values for the next candle
        self.high = 0.0
        self.low = sys.float_info.max
        self.prev_close = self.close
        self.close = self.close
        self.volume = 0.0
        self.trades = 0
        self.history.to_csv('data/' + self.ticker + '.csv') # Rewrite entire csv file with data held in memory - this is probably a bad approach
        self.no_trades = True

    def update_data(self, data): # Takes a JSON object
        new_candle = pd.Series([data['date'], data['open'], data['high'], data['low'], data['close'], data['volume'], data['trades']], index=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Trades'])
        self.history.loc[data['date']] = new_candle
        self.history.to_csv('data/' + self.ticker + '.csv')



def new_candle():
    _datetime = datetime.now(tz=pytz.UTC)
    print("New Candle!")
    BTCUSD.new_candle(_datetime)
    ETHBTC.new_candle(_datetime)
    ETHUSD.new_candle(_datetime)
    AVAXUSD.new_candle(_datetime)
    SOLUSD.new_candle(_datetime)
    SOLBTC.new_candle(_datetime)

def handle_command(_command):
    command = json.loads(_command)
    if(command['command'] == 'update_data'):
        try:
            update_data(command)
        except:
            print('Exception occured while trying to update data, it\'s probably your formatting') # This should really be an in-browser alert
# {"command": "update_data","ticker": "ETHBTC","date": "2022-12-07 20:05:00.000000+00:00","open": 0.08483,"high": 0.08486,"low": 0.08483,"close": 0.08486,"trades": 67,"volume": 0.0}
def update_data(command):
    if(command['ticker'] == 'ETHBTC'): # There must be a better way to do this
        ETHBTC.update_data(command)
    if(command['ticker'] == 'BTCUSD'):
        BTCUSD.update_data(command)
    if(command['ticker'] == 'ETHUSD'):
        ETHUSD.update_data(command)
    if(command['ticker'] == 'AVAXUSD'):
        AVAXUSD.update_data(command)

def ws_thread(*args):
    global BTCPRICE
    BTCPRICE = 'Connected and Subscribed'
    ws = websocket.WebSocketApp("wss://ws.kraken.com/", on_open = ws_open, on_close=ws_close, on_message = ws_message)
    ws.run_forever()

# Define WebSocket callback functions
def ws_message(ws, message): # Connect to WebSocket API and subscribe to trade feed for XBT/USD
    obj = json.loads(message)
    if ((len(obj) == 4) and ('connectionID' not in obj)):
    # log_ws(message)
        # print(obj[3] + " : " + obj[1][0][0]) # On each trade, prints stuff like ETH/USD : 2700.00
        if(obj[3] == 'XBT/USD'):
            global BTCUSD
            BTCUSD.new_data(float(obj[1][0][0]))
        if(obj[3] == 'ETH/XBT'):
            global ETHBTC
            ETHBTC.new_data(float(obj[1][0][0]))
        if(obj[3] == 'ETH/USD'):
            global ETHUSD
            ETHUSD.new_data(float(obj[1][0][0]))
        if(obj[3] == 'AVAX/USD'):
            global AVAXUSD
            AVAXUSD.new_data(float(obj[1][0][0]))
        if(obj[3] == 'SOL/USD'):
            global SOLUSD
            SOLUSD.new_data(float(obj[1][0][0]))
        if(obj[3] == 'SOL/BTC'):
            global SOLBTC
            SOLBTC.new_data(float(obj[1][0][0]))
    # [321, [['60938.20000', '0.03825548', '1635112722.279822', 's', 'l', '']], 'trade', 'XBT/USD'] The sort of thing you get back from Kraken

def ws_open(ws):
    ws.send('{"event":"subscribe", "subscription":{"name":"trade"}, "pair":["XBT/USD", "ETH/XBT", "ETH/USD", "AVAX/USD", "SOL/USD", "SOL/BTC", "LUNA/USD"]}')
    print("WebSocket connected and subscribed!", file=sys.stderr)

def ws_close(ws, arg2, arg3): # I don't think the arguments are very important here
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print('Disconnected from Kraken market feed at %s' % current_time)
    reconnect_delay = 5
    print("Attempting reconnect..")
    while True: # and internet_connected() ?
        time.sleep(reconnect_delay)
        try:
            ws = websocket.WebSocketApp("wss://ws.kraken.com/", on_open = ws_open, on_close=ws_close, on_message = ws_message)
            ws.run_forever()
            break
        except:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print('Failed to reconnect')
            print("Attempting reconnect in %s seconds.." % reconnect_delay)
        
BTCUSD = OHLC("BTCUSD")
ETHBTC = OHLC("ETHBTC")
ETHUSD = OHLC("ETHUSD")
AVAXUSD = OHLC("AVAXUSD")
SOLUSD = OHLC("SOLUSD")
SOLBTC = OHLC("SOLBTC")
WSSTARTED = False
SCHEDULER = BackgroundScheduler()
# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger('apscheduler.executors.default').propagate = False
# logging.getLogger('apscheduler.scheduler').propagate = False
# logging.getLogger('matplotlib').propagate = False

def run(scheduler):
    scheduler.add_job(new_candle, 'interval', seconds=config.interval) # call new_candle every x seconds
    # scheduler.start()

    _thread.start_new_thread(ws_thread, ())
    global WSSTARTED
    WSSTARTED = True
