import sys
import io
import random
import logging
from flask import Flask, flash, Response, redirect, request, render_template, request, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
# from pandas_datareader import data as web
import yfinance
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, tzinfo
import pytz
import mplfinance as mpf
import websocket
from websocket import create_connection
import _thread
import time
import json

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
        self.no_trades = False
    
    def new_candle(self, _datetime):
        if(self.no_trades):
            self.open = self.prev_close
            self.close = self.prev_close
            self.low = self.prev_close
            self.high = self.prev_close
        if(self.close != 0.0): # If this was the first candle and there were no trades, it's probably better to skip the candle than plot 0
            new_candle = pd.Series([_datetime, self.open, self.high, self.low, self.close, self.volume, self.trades], index=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Trades'])
            self.history.loc[_datetime] = new_candle
        self.open = 0.0
        self.high = 0.0
        self.low = sys.float_info.max
        self.prev_close = self.close
        self.close = 0.0
        self.volume = 0.0
        self.trades = 0
        self.history.to_csv('data/' + self.ticker + '.csv')
        self.no_trades = True

    def update_data(self, data): # Takes a JSON object
        new_candle = pd.Series([data['date'], data['open'], data['high'], data['low'], data['close'], data['volume'], data['trades']], index=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Trades'])
        self.history.loc[data['date']] = new_candle
        self.history.to_csv('data/' + self.ticker + '.csv')

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
BTCUSD = OHLC("BTCUSD")
ETHBTC = OHLC("ETHBTC")
ETHUSD = OHLC("ETHUSD")
WSSTARTED = False

@app.route("/",methods=["POST","GET"])
def index():
    if(request.method == "POST"):
        print('POST Request!', file=sys.stderr)
        if('command_entry' in request.form):
            handle_command(request.form['command_entry'])
    return render_template("kraken.html", ticker="XBT/USD", xbtusd=BTCUSD, ethbtc=ETHBTC, ethusd=ETHUSD)

def new_candle():
    _datetime = datetime.now(tz=pytz.UTC)
    print("New Candle!")
    BTCUSD.new_candle(_datetime)
    ETHBTC.new_candle(_datetime)
    ETHUSD.new_candle(_datetime)

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

def ws_thread(*args):
    global BTCPRICE
    BTCPRICE = 'Connected and Subscribed'
    ws = websocket.WebSocketApp("wss://ws.kraken.com/", on_open = ws_open, on_close=ws_close, on_message = ws_message)
    ws.run_forever()

# Define WebSocket callback functions
def ws_message(ws, message): # Connect to WebSocket API and subscribe to trade feed for XBT/USD
    obj = json.loads(message)
    if ((len(obj) == 4) and ('connectionID' not in obj)):
        print(obj[3] + " : " + obj[1][0][0])
        if(obj[3] == 'XBT/USD'):
            global BTCUSD
            BTCUSD.new_data(float(obj[1][0][0]))
        if(obj[3] == 'ETH/XBT'):
            global ETHBTC
            ETHBTC.new_data(float(obj[1][0][0]))
        if(obj[3] == 'ETH/USD'):
            global ETHUSD
            ETHUSD.new_data(float(obj[1][0][0]))
            
    # [321, [['60938.20000', '0.03825548', '1635112722.279822', 's', 'l', '']], 'trade', 'XBT/USD'] The sort of thing you get back from Kraken

def ws_open(ws):
    ws.send('{"event":"subscribe", "subscription":{"name":"trade"}, "pair":["XBT/USD", "ETH/XBT", "ETH/USD"]}')
    print("WebSocket connected and subscribed!", file=sys.stderr)

def ws_close(ws, arg2, arg3): # I don't think the arguments are very important here
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print('Disconnected from Kraken at %s' % current_time)
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
            print("Attempting reconnect in %s seconds.." % current_time)
        
_thread.start_new_thread(ws_thread, ())
WSSTARTED = True

scheduler = BackgroundScheduler()
scheduler.add_job(new_candle, 'interval', seconds=300) # call new_candle every x seconds
scheduler.start()
logging.getLogger('apscheduler.executors.default').propagate = False
logging.getLogger('apscheduler.scheduler').propagate = False

    
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=3000) # I don't know what the side effects of use_reloader=False are. It's here because apparently
    app.debug = True                                                    # in debug mode, flask initializes twice and that was causing double the output, which was
    app.secret_key = 'WX78654H'                                         # a bit annoying. And use_reloader=False was the first fix I found. Apparently it has
                                                                        # something to do with reloading running code on save, who'd have known?

# TODO
# Download data from Kraken - or TradingView
# Get the old app.css from github and use that. Rename this one to index.css or somehing, there might be a change needed in chart.py
# Refactor OHLC(TV) class into another file
# Record volume - which one is it in the trade message?
# Test with charts, maybe I'll follow Derek and use Plotly
# Get indicators / signals working
# Connect to Kraken with credentials
# Monitor positions, keep track of changes and whether they were made manually - maybe even keep a csv of account values
# Send trades, keep track of all trades sent, and further monitor those positions - maybe use limit orders
# Pat myself on the back
# Do up some nicer UI, chart portfolio changes, buys/sells, # of trades, and the like

# Insert data function?
# Trailing stop?


