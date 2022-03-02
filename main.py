from account import Account
import pytrade
import sys
import io
import random
import logging
from flask import Flask, flash, Response, redirect, request, render_template, url_for
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure
import ta
import pandas as pd
import numpy as np
import yfinance
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import dateutil
import time
import mplfinance as mpf
from datetime import date, datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
# import riskribbon_strategy_reduced as strategy
import util.csv as csv
import config as config

def round_dt_up(dt, delta):
    return dt + (datetime.min - dt) % delta

# def run_strategy():
    # ticker = 'ETHBTC'
    # df = strategy.get_ticker_df_from_csv(ticker)
    # df.index = pd.DatetimeIndex(df['Date'])
    # df = strategy.define_indicators(ticker,df, ['riskribbon'] ) # get rid of the 'indicators' argument
#     SCHEDULER.add_job(strategy.generate_signals, args=strategy.define_indicators, trigger='interval', seconds=300) # call new_candle every x seconds
#     SCHEDULER.start()

def on_new_candle(event):
    if not event.exception:
        print('event' + str(event))
        global ACCOUNT
        ticker = 'ETHBTC'
        ticker = config.trade_ticker
        df = csv.read_to_df(ticker)
        df.index = pd.DatetimeIndex(df['Date'])
        df = config.strategy.define_indicators(ticker,df, ['riskribbon'] ) # get rid of the 'indicators' argument
        ACCOUNT.get_balances() # Perhaps this should be below strategy.generate_signals() It really depends on whether it takes much time
        config.strategy.generate_signals(df, ACCOUNT)
        print('Account Balacnces:\n' + str(ACCOUNT.btc_bal) + ' BTC\n' + str(ACCOUNT.eth_bal) + ' ETH\n'
         + str(ACCOUNT.avax_bal) + ' AVAX\n' + str(ACCOUNT.usd_bal) + ' USD\n')
        

app = Flask(__name__)
# logging.basicConfig(level=logging.DEBUG)
RISK_SCATTER_TICKERS = ['BTC-USD', 'SPY']
END = dt.datetime.now() + dt.timedelta(days=1)
START = END - dt.timedelta(minutes=1000)

RESTART_CHART = 'RESTART_CHART'
RESTART_DATA_COLLECTION = 'RESTART_DATA_COLLECTION'
RESTART_ACCOUNT = 'RESTART_ACCOUNT'
SCHEDULER = BackgroundScheduler()
ACCOUNT = Account( ["ETH/USD","ETH/XBT","BTC/USD","AVAX/USD"] ) # pass in an array from config.py

@app.route("/send_order", methods=["POST","GET"])
def send_order():#event):
    print(3)
    global ACCOUNT
    # ticker = event #.ticker ?
    ticker = config.trade_ticker # AVAX/USD
    # if(ticker == 'AVAX/USD'): ticker = 'AVAX/USD'
    ticker='AVAXUSD'
    df = csv.read_to_df(config.trade_side_1 + config.trae_side_2)
    ticker = config.trade_side_1 + "/" + config.trade_side_2
    last_row = df[-1:]
    entry_price = last_row['Close'].item()
    exit_price = entry_price * 1.006
    volume = (ACCOUNT.usd_bal * 0.98) / entry_price
    print('entry_price')
    print(entry_price)
    print(volume)
    print()
    ACCOUNT.send_order(_pair = ticker, _type = "buy", _ordertype = "market", 
                       _price = round(entry_price,2), _volume = round(volume,2))
    print("3.5")
    # Await?
    time.sleep(3)
    ACCOUNT.send_order(_pair = ticker, _type = "sell", _ordertype = "limit", 
                        _price = round(exit_price,2), _volume = round(volume,2))
    print("3.75")
    return "Sent!"


@app.route("/order", methods=["POST","GET"])
def order_route():
    return render_template("order.html")

if __name__ == "__main__":
    now = datetime.now()
    data_collect_start = round_dt_up(now, timedelta(minutes=(config.interval/60)))
    data_record_and_trade_start = data_collect_start + timedelta(minutes=5, seconds=1)

    SCHEDULER.add_job(pytrade.run, args=[SCHEDULER], run_date=data_collect_start) # I should probably use some arguments here such as ticker(s) and interval
    SCHEDULER.add_listener(on_new_candle, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    SCHEDULER.start()

    print("Now:\t\t" + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))
    print("Start:\t\t" + str(data_collect_start.hour) + ":" + str(data_collect_start.minute) + ":" + str(data_collect_start.second))
    print("First Candle:\t" + str(data_collect_start.hour) + ":" + str(data_collect_start.minute + 5) + ":" + str(data_collect_start.second))
    
    import chart as chart
    chart.strategy = config.strategy # The strategy can be switched out like this, and probably just the same for the backtester

    app.run(debug=True, use_reloader=False, host='0.0.0.0',port=8080)
    app.debug = True
    app.secret_key = 'WX78654H'

    # TODO
    # Keep a CSV of executed trades
    # I wonder if I could pass variable = plot_svg(get_stat_df_from_csv(is_connected), "Server Uptime") to html and expect it retrun the right plot if I use {{variable}}