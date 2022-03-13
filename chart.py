from __main__ import app
# from flask import current_app as app
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
# from pandas_datareader import data as web
import yfinance
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import dateutil
import mplfinance as mpf
import deviation_scalp_strat as strategy # I should definte some simple default strategy

@app.route("/",methods=["POST","GET"])
def index():
    ticker='AVAXUSD'
    default_indicators = 'riskribbon'
    if(request.method == "POST"):
        
        # form_name = request.form['form-name']
        if('download_tickers' in request.form):
            download_tickers = request.form['download_tickers']
            download_multiple_stocks(download_tickers)
            ticker=download_tickers.split(' ')[0]
        elif('ticker' in request.form):
            new_tick = request.form['ticker']
            new_tick = new_tick.replace('-','.') # yahoo uses '-' in crypto tickers (BTC-USD) which interferes with the retrieving of variables from the url
            new_tick = new_tick.replace('/','')
            # save_to_csv_yahoo(ticker)
            new_start = request.form['start']
            new_start = new_start.replace('-','.') # same thing with dates, so I replaced them with '.'
            new_end = request.form['end']
            new_end = new_end.replace('-','.')
            new_start_dt = dt.datetime.today() - dt.timedelta(days=365) # Maybe a slightly wasetful way to handle no
            if(new_start != ''):                                        # entry, but oh well
                new_start_dt = dt.datetime.strptime(new_start, "%Y.%m.%d").date()
                global START
                START = new_start_dt
            new_end_dt = dt.datetime.today() + dt.timedelta(days=1) # Because crypto uses UTC time, sometimes
            if(new_end != ''):                                      # Your local day will be a day behind,
                new_end_dt = dt.datetime.strptime(new_end, "%Y.%m.%d").date() # Causing the latest daily candle
                global END                                          # not to appear
                END = new_end_dt
            
            new_indicators = request.form['indicators']
            new_indicators = new_indicators.replace(',','')
            if(new_indicators == ''):
                new_indicators = 'none'
            return render_template("app.html", ticker=new_tick, start=START, end=END, sday=new_start_dt.day, smonth=new_start_dt.month,
                                    syear=new_start_dt.year, eday=new_end_dt.day, emonth=new_end_dt.month, 
                                    eyear=new_end_dt.year, indicators=new_indicators)

    return render_template("app.html", ticker=ticker, start=START, end=END, sday=START.day, smonth=START.month,
                                    syear=START.year, eday=END.day, emonth=END.month, 
                                    eyear=END.year, indicators=default_indicators)

# @app.route("/stat",methods=["POST","GET"]) # This is no longer very useful, but I will probably want to re-use the code in concept, just with some different data
# def stat():
#     _data = get_stat_df_from_csv('is_connected')
#     return plot_svg(_data, "Server Uptime")

# @app.route("/matplot-as-image-<int:num_x_points>.svg")
# def plot_svg(data, title):
#     s = mpf.make_mpf_style(base_mpf_style='yahoo', rc={'font.size': 16, 'text.color': '#c4d0ff',
#                             'axes.labelcolor':'#c4d0ff', 'xtick.color':'#c4d0ff', 'ytick.color':'#c4d0ff'},
#                             facecolor="#434345", edgecolor="#000000", figcolor="#292929", y_on_right=False) 
#     fig = mpf.figure(figsize=(12, 8), style=s)
#     # fig.tight_layout()
#     fig.subplots_adjust(bottom=0.2)
#     axis = fig.gca()
#     dates = [dateutil.parser.parse(s) for s in data['Date']]
#     axis.plot(dates, data['is_connected'], "")
    
#     axis.set_xticklabels(axis.get_xticks(), rotation = 25)
#     axis.set_xticks(dates)
#     axis.set_title(title)
#     date_form = mdates.DateFormatter("%Y-%m-%d %H:%M:%S")
#     axis.xaxis.set_major_formatter(date_form)
#     axis.xaxis.set_major_locator(mdates.HourLocator(interval=1)) # I need to figure out how to set this dynamically, Actually I'm not sure this is nessecary at all
    
#     output = io.BytesIO()
#     FigureCanvasSVG(fig).print_svg(output)
#     return Response(output.getvalue(), mimetype="image/svg+xml")

@app.route("/mplfinance2-<string:ticker>-<start>-<end>-<indicators>.png", methods=["POST","GET"])
def plot_finance2(ticker, start, end, indicators):
    data = get_ticker_df_from_csv(ticker)
    output = io.BytesIO()
    ticker = ticker.replace('.','-')
    data = get_ticker_df_from_csv(ticker)
    indicators = indicators.split(' ')
    start = dt.datetime.strptime(start, "%Y.%m.%d").date()
    end = dt.datetime.strptime(end, "%Y.%m.%d").date()
    # indicators = ['risk','riskscatter'] 
    # indicators = [ 'risk','riskscatter', 'sma'] #'riskdif']
    # indicators = ['risk','riskscatter', 'sma', 'ext'] 
    output = mplfinance_plot(data, ticker, indicators, 'candlestick', start.year, start.month, start.day, end.year, end.month, end.day)
    return Response(output.getvalue(), mimetype="image/png")

def get_ticker_df_from_csv(ticker):
    try:
        df = pd.read_csv('./data/' + ticker + '-active_strategy.csv')
    except FileNotFoundError:
        print('File does not exist')
    else:
        df = df.dropna(subset=['Close'])
        return df

def get_stat_df_from_csv(file):
    try:
        df = pd.read_csv('stat/' + file + '.csv')
    except FileNotFoundError:
        print('File does not exist')
    else:
        df.index = df.index = pd.DatetimeIndex(df['Date'])
        return df

def save_to_csv_yahoo(ticker):
    # df = web.DataReader(ticker.strip(), 'yahoo', start, end)
    df = yfinance.download(ticker.strip(), period="MAX")
    df.to_csv('./data/' + ticker + ".csv")
    return df

def plot_indicator(df,index):   # Not really sure if this works, I haven't used it for a long time. Maybe the matplotlib SVG chart would be better for standalone indicators anyways? Or a second panel?
    df.index = pd.DatetimeIndex(df['Date'])
    s = mpf.make_mpf_style(base_mpf_style='charles', rc={'font.size': 8})
    fig = mpf.figure(figsize=(12, 8),style=s)
    ax = fig.add_subplot(2,1,1)
    ax.set_title(index)
    buf=io.BytesIO()
    mpf.plot(df, type='line', ax=ax, show_nontrading=True,savefig=buf)
    return buf

def download_multiple_stocks(tickers):
    tickers = tickers.split(' ')
    if(len(tickers) == 1):
        save_to_csv_yahoo(tickers[0])
    for x in tickers:
        save_to_csv_yahoo(x)

def mplfinance_plot(df, ticker, indicators, chart_type, syear, smonth, sday, eyear, emonth, eday):
    start = f"{syear}-{smonth}-{sday}"
    end = f"{eyear}-{emonth}-{eday}"
    df.index = pd.DatetimeIndex(df['Date'])
    # df = strategy.define_indicators(ticker, df, indicators)
    df_sub = df.loc[start:end]
    s = mpf.make_mpf_style(base_mpf_style='yahoo', rc={'font.size': 16, 'text.color': '#c4d0ff',
                            'axes.labelcolor':'#c4d0ff', 'xtick.color':'#c4d0ff', 'ytick.color':'#c4d0ff'},
                            facecolor="#434345", edgecolor="#000000", figcolor="#292929", y_on_right=False,
                            gridcolor="#727272") 
    fig = mpf.figure(figsize=(12, 8), style=s)
    title = ticker
    adps = strategy.add_indicators(ticker, df_sub, indicators)
    buf = io.BytesIO()
    # if('line' in indicators):
    #     chart_type = 'line'
    # if('renko' in indicators):
    #     chart_type = 'renko' # doesn't work when addplot is set in mpf.plot()
    #     adps=False # maybe?
    # hlines = dict(hlines=[0.2,0.8], colors=['g','r'], linestyle='-.') # Only works on primary y axis
    out = mpf.plot(df_sub, type=chart_type, title=title, tight_layout=True, addplot=adps,
              volume=False, figscale=3, show_nontrading=True, style=s, 
              savefig=buf)#panel_ratios=(3,1),hlines=hlines,mav=(50,350))
    # for var in (df_sub['sma350'], df_sub['sma50']): # Annotation is not supported in MPLFinance, but apparently there are some tricky workarounds (get the axis) to look into
    #     fig.annotate('%0.2f' % var.max(), xy=(1, var.max()), xytext=(8, 0), # Seeing as I need the axis to display on a log scale, it's probably worth doing
    #              xycoords=('axes fraction', 'data'), textcoords='offset points')
    # if('risk' in indicators or 'riskribbon' in indicators):
    #     for var in (df_sub['sma350'], df_sub['sma50']):
    #         print(var.max())
    return buf

# logging.basicConfig(level=logging.DEBUG)
END = dt.datetime.now() + dt.timedelta(days=1)
START = END - dt.timedelta(minutes=1000)


# TODO
# I wonder if I could pass variable = plot_svg(get_stat_df_from_csv(is_connected), "Server Uptime") to html and expect it retrun the right plot if I use {{variable}}