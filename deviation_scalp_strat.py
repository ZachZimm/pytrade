import numpy as np
import ta
import time
import mplfinance as mpf

IS_LONG = False

def define_dev(df, dev_length = 20):
    df['dev'] = df['Close'].rolling(dev_length).std()
    dev_bands = ta.volatility.BollingerBands(close=df['dev'], window=dev_length, window_dev=1)
    df['dev_upper'] = dev_bands.bollinger_hband()
    df['dev_sma'] = dev_bands.bollinger_mavg()
    df['dev_lower'] = dev_bands.bollinger_lband()

    return df

def define_min_max(df, min_max_length = 5):
    df['min'] = df['Low'].rolling(min_max_length).min()
    df['max'] = df['High'].rolling(min_max_length).max()

    return df

def define_signals(df):
    df['open_long'] = np.where((df['dev'] > df['dev_sma']) & (df['dev'].shift(1) <= df['dev_sma'].shift(1)), df['Close'] * 1, np.nan) 
    df['close_long'] = np.where((df['Close'].shift(5) > df['Close']) & (df['Close'] < df['min']), df['Close'] * 1, np.nan) # implement low_bound / high_bound
    return df


def intersection(lst1, lst2): # Returns the intersection of two lists
    return list(set(lst1) & set(lst2))

def define_indicators(_ticker, _df, _indicators, is_backtest = False): # This should proably accept a bool for backtesting 
    max_lookback = 2000 # This should probably be determined on a per-strategy basis
    if(is_backtest):    # Maybe set a maximum where I call this function in chart.py as well
        max_lookback = 2000
    # _df = define_hull(_df)
    _df = define_dev(_df, 20)
    _df = define_min_max(_df,5)
    _df = define_signals(_df)
    return _df

def add_indicators(_ticker, _df, _indicators):
    panels = 1
    _adps = [] # Indicators: risk riskscatter riskdif sma ext hull

    if(_df['dev'].isnull().all() == False):
        _adps.append(mpf.make_addplot(_df['dev'], color='#f3ff35', panel=panels)) # while high values represent high instantaneous risk. The
        _adps.append(mpf.make_addplot(_df['dev_sma'], color='#fc6f03', panel=panels))
        # _adps.append(mpf.make_addplot(_df['dev_upper'], color='#2191EB', panel=panels))
        # _adps.append(mpf.make_addplot(_df['dev_lower'], color='#2191EB', panel=panels))        

        if(_df['open_long'].isnull().all() == False):
            # _df['buyline'] = _df['riskbuycrossover1'].dropna().mean()
            # _adps.append(mpf.make_addplot(_df['buyline'], color='#febf01', panel=0))
            _adps.append(mpf.make_addplot(_df['open_long'], color='#febf01',type="scatter", panel=0))
            _adps.append(mpf.make_addplot(_df['open_long'], color='#febf01',type="scatter", panel=0))
        if(_df['close_long'].isnull().all() == False):
            # _df['sellline'] = _df['risksellcrossunder1'].dropna().mean()
            # _adps.append(mpf.make_addplot(_df['sellline'], color='#adff2f', panel=0))
            _adps.append(mpf.make_addplot(_df['close_long'], color='#adff2f',type="scatter", panel=0))
            _adps.append(mpf.make_addplot(_df['close_long'], color='#adff2f',type="scatter", panel=0))
    
    return _adps

def generate_signals(_df, account):
    last_row = _df[-1:]
    # print("Last Row: ")
    ticker = "AVAX/USD"
    global IS_LONG

    if (not IS_LONG and last_row['open_long'].iloc[0] == last_row['Close'].iloc[0]): # I don't want to have to use .iloc[-1] in the conditional, it should be part of last_row
        entry_price = last_row['Close'].item()
        exit_price = entry_price * 1.006 # This should come round(from,2) the config file too
        volume = (account.usd_bal * 0.98) / entry_price

        account.send_order(_pair = ticker, _type = "buy", _ordertype = "market", 
                       _price = entry_price, _volume = round(volume,2))
        # Await?
        time.sleep(3)
        account.send_order(_pair = ticker, _type = "sell", _ordertype = "limit", 
                            _price = exit_price, _volume = round(volume,2))
    
        IS_LONG = True

    # if (last_row['riskbuycrossover2'].iloc[0] == last_row['Close'].iloc[0]): 
    #     volume = float(account.btc_bal) * 0.5 # This volume should probably not be the same as the other buy condition)
    #     account.send_order(_pair = "ETH/XBT", _type = "buy", _ordertype = "limit", 
    #                        _price = str(last_row['Close']), _volume = volume)
    #     print('Buy %s at %s' % (volume, last_row['Close']))
    
    if (IS_LONG and last_row['close_long'].iloc[0] == last_row['Close'].iloc[0]):
        volume = (account.avax_bal * 0.25) / float(last_row['Close'].iloc[0])

        account.send_order(_pair = "AVAXUSD", _type = "sell", _ordertype = "market", 
                           _price = round(last_row['Close'].item(),2), _volume = round(volume,2))
        print('Sell %s at %s' % (volume.item(), last_row['Close'].iloc[0]))

        IS_LONG = False

    # if (last_row['risksellcrossunder2'].iloc[0] == last_row['Close'].iloc[0]):
    #     volume = float(account.eth_bal) * 0.75 * float(last_row['Close'].iloc[0])
    #     print('Sell %s at %s' % (volume, last_row['Close']))