import sys
import io
import random
import logging
from flask import Flask, flash, Response, redirect, request, render_template, request, url_for
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
# from pandas_datareader import data as web
import yfinance
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import mplfinance as mpf
import websocket
from websocket import create_connection
import _thread
import time
import json

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
BTCPRICE = ''
ETHBTC = ''
WSSTARTED = False

@app.route("/",methods=["POST","GET"])
def index():
    num_x_points = int(request.args.get("num_x_points", 50))
    ticker = str(request.args.get("ticker", 'GLP'))
    tickers = str(request.args.get("tickers", 'MSFT'))
    ticker2='SPY'
    # print('This is standard output', file=sys.stderr)
    if(request.method == "POST"):
        print('This is standard output', file=sys.stderr)
    return render_template("index.html", ticker="XBT/USD")

@app.route("/kraken", methods=["POST", "GET"])
def kraken():
    # Start a new thread for the WebSocket interface
    # ws = create_connection("wss://ws.kraken.com/")
    global WSSTARTED
    if(request.method == "POST"):
        if(WSSTARTED == False):
            _thread.start_new_thread(ws_thread, ())
            WSSTARTED = True
    return render_template("kraken.html", ticker="XBT/USD", price=BTCPRICE, ethbtc=ETHBTC)

def ws_thread(*args):
    global BTCPRICE
    BTCPRICE = 'Connected and Subscribed'
    ws = websocket.WebSocketApp("wss://ws.kraken.com/", on_open = ws_open, on_message = ws_message)
    ws.run_forever()

# Define WebSocket callback functions
def ws_message(ws, message): # Connect to WebSocket API and subscribe to trade feed for XBT/USD
    obj = json.loads(message)
    if ((len(obj) == 4) and ('connectionID' not in obj)):
        print(obj[3] + " : " + obj[1][0][0])
        if(obj[3] == 'XBT/USD'):
            global BTCPRICE
            BTCPRICE = str("{:10.2f}".format(float(obj[1][0][0])))
        if(obj[3] == 'ETH/XBT'):
            global ETHBTC
            ETHBTC = str("{:2.6f}".format(float(obj[1][0][0])))
    # [321, [['60938.20000', '0.03825548', '1635112722.279822', 's', 'l', '']], 'trade', 'XBT/USD']
def ws_open(ws):
    global BTCPRICE
    BTCPRICE = 'Connected and Subscribed!'
    ws.send('{"event":"subscribe", "subscription":{"name":"trade"}, "pair":["XBT/USD", "ETH/XBT"]}')
    print("WebSocket connected and subscribed!", file=sys.stderr)

# Continue other (non WebSocket) tasks in the main thread
# while True:
#     time.sleep(5)
#     print("Main thread: %d" % time.time())

if __name__ == "__main__":
    # import webbrowser
    # webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True, host='0.0.0.0')
    app.debug = True
    app.secret_key = 'WX78654H'
