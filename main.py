from account import Account
import pytrade
import sys
import io
import random
import logging
from flask import Flask, flash, Response, redirect, request, render_template, url_for, send_from_directory
from flask_cors import CORS
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
import json
import mplfinance as mpf
from datetime import date, datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
# import riskribbon_strategy_reduced as strategy
import util.csv as csv
import util.logger as logger # Implement a use for this here eventually
import config as config

def round_dt_up(dt, delta):
    return dt + (datetime.min - dt) % delta

def on_new_candle(event):
    if not event.exception:
        global ACCOUNT
        ticker = config.trade_ticker
        df = csv.read_to_df(ticker)
        df.index = pd.DatetimeIndex(df['Date'])
        df = config.strategy.define_indicators(ticker,df, ['riskribbon'] ) # get rid of the 'indicators' argument
        # df = pytrade.define_indicators(ticker,df)
        config.strategy.generate_signals(df, ACCOUNT)
        ACCOUNT.get_balances() # Perhaps this should be below strategy.generate_signals() It really depends on whether it takes much time
        print('\nAccount Balacnces:\n' + str(ACCOUNT.btc_bal) + ' BTC\n' + str(ACCOUNT.eth_bal) + ' ETH\n'
         + str(ACCOUNT.avax_bal) + ' AVAX\n' + str(ACCOUNT.sol_bal) + ' SOL\n' + '$' + str(ACCOUNT.usd_bal) + ' USD\n')

app = Flask(__name__)
CORS(app)
# logging.basicConfig(level=logging.DEBUG)
END = dt.datetime.now() + dt.timedelta(days=1)
START = END - dt.timedelta(minutes=1000)

RESTART_CHART = 'RESTART_CHART'
RESTART_DATA_COLLECTION = 'RESTART_DATA_COLLECTION'
RESTART_ACCOUNT = 'RESTART_ACCOUNT'
SCHEDULER = BackgroundScheduler()
ACCOUNT = Account( ["ETH/USD","ETH/XBT","BTC/USD","AVAX/USD", "SOL/USD"] ) # pass in an array from config.py

@app.route("/data", methods=["GET"])
def serve_data():
    data = {
            "account_bal": (ACCOUNT.usd_bal + (ACCOUNT.active_bal * pytrade.ETHUSD.close)),
            "is_long": ACCOUNT.is_long,
            "last_entry": ACCOUNT.last_entry,
            "Close": pytrade.ETHUSD.close, 
            "prev_close" : pytrade.ETHUSD.prev_close,
            "ticker": config.trade_ticker, 
            "active_bal": ACCOUNT.active_bal,
            "avax_bal": ACCOUNT.avax_bal,
            "eth_bal": ACCOUNT.eth_bal,
            "usd_bal": ACCOUNT.usd_bal, 
            "is_short": ACCOUNT.is_short
            }
    
    return data

@app.route("/strategy_data", methods=["GET"])
def serve_strategy_data():
    path = 'data/' + config.trade_ticker + '-active_strategy.csv'
    data = pd.read_csv(path, index_col=0) # If there is old data, use that
    return data[config.recent_data_length * -1:].to_csv()
    # return send_from_directory('data', path)
    # returntext = ""
    # with open(path, 'r') as f:
    #     returntext = f.read()
    # f.close()
    # if (request.method == "GET"): return returntext
    # else: return render_template('content.html', text=returntext)

@app.route("/strategy_data_full", methods=["GET"])
def serve_strategy_data_full():
    path = 'data/' + config.trade_ticker + '-active_strategy.csv'
    data = pd.read_csv(path) # If there is old data, use that
    del data['Unnamed: 0']
    del data ['Date.1']
    return data.to_csv()
    # return data['Unnamed: 0'].to_csv()


@app.route("/strategy_log", methods=["GET"])
def serve_strategy_log():
    
    path = 'data/' + 'strategy_log.csv'
    returntext = ""
    with open(path, 'r') as f:
        returntext = f.read()
    f.close()
    if (request.method == "GET"): return returntext
    else: return render_template('content.html', text=returntext)

def check_for_order_log():
    try:
        with open(('data/' + 'strategy_log' + '.csv'), 'r') as data:
            is_data = str(data.readline()) == 'Date,type,ticker,price,volume,balance\n'
            if (is_data == False):
                raise ValueError('Found the wrong data in is_connected.csv stat file, overwriting..')
            data.close()
    except:                                                                 
        print('Failed to find old data in is_connected.csv, starting a new database instead and potentially overwriting')
        with open(('data/' + 'strategy_log' + '.csv'), 'w') as data:
                data.write('Date,type,ticker,price,volume,balance\n')
                data.close()
if __name__ == "__main__":
    now = datetime.now()
    check_for_order_log()
    data_collect_start = round_dt_up(now, timedelta(minutes=(config.interval/60)))
    data_record_and_trade_start = data_collect_start + timedelta(minutes=config.interval/60, seconds=1)

    SCHEDULER.add_job(pytrade.run, args=[SCHEDULER], run_date=data_collect_start) # I should probably use some arguments here such as ticker(s) and interval
    SCHEDULER.add_listener(on_new_candle, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    SCHEDULER.start()
    ACCOUNT.get_balances()
    print()
    if(config.debug is True):
        print("!!-- Debug Mode ENABLED --!!")
    print("Now:\t\t" + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))
    print("Start:\t\t" + str(data_collect_start.hour) + ":" + str(data_collect_start.minute) + ":" + str(data_collect_start.second))
    print("First Candle:\t" + str(data_collect_start.hour) + ":" + str(data_collect_start.minute + 5) + ":" + str(data_collect_start.second))
    print("\n")    
    logger.ws_log('trading server started')
    import chart as chart
    chart.strategy = config.strategy # The strategy can be switched out like this, and probably just the same for the backtester

    app.run(debug=True, use_reloader=False, host='0.0.0.0',port=config.port)
    app.secret_key = 'WX78654H'

    # TODO
    # Keep a CSV of executed trades, both sides of the trade
    # Build a backtester
