import numpy as np
import ta
import time
import config as config
import mplfinance as mpf

def define_dev(df, dev_length, sma_length, dev_lookback):
    df['dev'] = df['Close'].rolling(dev_length).std()
    df['sma_for_dev'] = ta.trend.sma_indicator(close=df['Close'], window=sma_length)

    df['sma_diff'] = df['Close'] - df['sma_for_dev']
    df['dev_dir'] = df['sma_diff'] * df['dev']
    dev_bands = ta.volatility.BollingerBands(close=df['dev_dir'], window=dev_lookback, window_dev=1)

    df['dev_upper'] = dev_bands.bollinger_hband()
    df['dev_sma'] = dev_bands.bollinger_mavg()
    df['dev_lower'] = dev_bands.bollinger_lband()
    df['dev_s_sma'] = df['dev_dir'].rolling(window=int(dev_lookback/1.2)).mean()
    df['dev_s_s_sma'] = df['dev_dir'].rolling(window=int(dev_lookback/2.6)).mean()
    df['0'] = 0 # May not be nessecary

    return df

def define_min_max(df, min_max_length):
    df['min'] = df['Low'].rolling(min_max_length).min()
    df['max'] = df['High'].rolling(min_max_length).max()

    return df

def define_signals(df):
    # Original
    # df['open_long'] = np.where(((df['dev_dir'] > df['dev_sma']) & (df['dev_sma'] > 0)) & (df['dev_dir'].shift(1) <= df['dev_sma'].shift(1)), df['Close'] * 1, np.nan)
    # df['open_short'] = np.where(((df['dev_dir'] < df['dev_sma']) & (df['dev_sma'] < 0)) & (df['dev_dir'].shift(1) >= df['dev_sma'].shift(1)), df['Close'] * 1, np.nan)
    # New
    # df['open_long'] = np.where(((df['dev_dir'] > df['dev_lower']) & (df['dev_sma'] > 0)) & (df['dev_dir'].shift(1) <= df['dev_lower'].shift(1)), df['Close'] * 1, np.nan) # Buy on dev_dir cross over lower band
    # df['open_short'] = np.where(((df['dev_dir'] < df['dev_upper']) & (df['dev_sma'] > 0)) & (df['dev_dir'].shift(1) >= df['dev_upper'].shift(1)), df['Close'] * 1, np.nan) # Sell on dev_dir cross under upper band

    # df['open_long'] = np.where(((df['dev_s_s_sma'] > df['dev_s_sma']) & (df['dev_dir'] > df['dev_s_s_sma'])) & (df['dev_s_s_sma'].shift(1) <= df['dev_s_sma'].shift(1)), df['Close'] * 1, np.nan) # Buy on dev_super_short_sma (crossover) dev_short_sma
    # df['close_long'] = np.where((df['Close'] < df['min'].shift(1)) & (df['Close'].shift(1) >= df['min'].shift(1)),                                                                                # Sell on lower breakout
    #                             df['Close'], np.nan)                                                                                                                                              # open_short does nothing in this configuration
    # df['open_short'] = np.where(False, df['Close'] * 1, np.nan) # Sell on dev_dir cross under upper band

    # df['open_long'] = np.where(((df['dev_s_s_sma'] < df['dev_s_sma']) & (True)) & (df['dev_s_s_sma'].shift(1) >= df['dev_s_sma'].shift(1)), df['Close'] * 1, np.nan)                           # Buy on dev_short_sma (crossover) dev_super_short_sma
    df['open_long'] = np.where(((df['dev_s_s_sma'] < df['dev_s_sma']) & (True)) & (df['dev_s_s_sma'].shift(1) >= df['dev_s_sma'].shift(1)) | ((df['dev_s_s_sma'] > df['dev_s_sma']) & (True)) & (df['dev_s_s_sma'].shift(1) <= df['dev_s_sma'].shift(1)), df['Close'] * 1, np.nan)
    df['open_short'] = np.where(((df['dev_s_sma'] < df['dev_sma'])) & (df['dev_s_sma'].shift(1) >= df['dev_sma'].shift(1)), df['Close'] * 1, np.nan)                                             # Buy on dev_super_short_sma (crossover) dev_short_sma
    df['close_long'] = np.where((df['Close'] < df['min'].shift(1)) & (df['Close'].shift(1) >= df['min'].shift(1)),
                                 df['Close'], np.nan)                        
    
    return df

def find_closes(df):
    is_long = False
    reached_target = False
    last_entry = 0
    df['half_close'] = np.nan
    df['full_close'] = np.nan
    df['is_long'] = np.nan
    for index, row in df.iterrows():
        if row['open_long'] == row['Close']:
            is_long = True
            last_entry = row['Close']
        if (is_long and reached_target) and (row['close_long'] == row['Close']): # Market sell
            is_long = False
            reached_target = False
            df.loc[index, 'full_close'] = row['Close']
        if (is_long and not reached_target) and (row['open_short'] == row['Close']):
            is_long = False
            df.loc[index, 'full_close'] = row['Close']

        if ((is_long and not reached_target) and (row['High'] >= (last_entry * config.strategy_arguments[3]))): # Limit Sell
            reached_target = True
        #     is_long = False
            df.loc[index, 'half_close'] = (last_entry * config.strategy_arguments[3])
        if is_long:
            df.loc[index, 'is_long'] = (last_entry)

    return df

def intersection(lst1, lst2): # Returns the intersection of two lists
    return list(set(lst1) & set(lst2))

def define_indicators(_ticker, _df, _indicators, is_backtest = False): # This should proably accept a bool for backtesting 
    max_lookback = 2000 # This should probably be determined on a per-strategy basis
    if(is_backtest):    # Maybe set a maximum where I call this function in chart.py as well
        max_lookback = 2000
    # _df = define_hull(_df)
    _df = define_dev(_df, config.strategy_arguments[0], config.strategy_arguments[1], config.strategy_arguments[2]) # length for deviation calc, reference SMA length, deviation lookback, profit target
    _df = define_min_max(_df,config.strategy_arguments[4])
    _df = define_signals(_df)
    _df = find_closes(_df)
    _df.to_csv('data/' + _ticker + '-active_strategy.csv')
    return _df

def add_indicators(_ticker, _df, _indicators):
    panels = 1
    _adps = [] # Indicators: risk riskscatter riskdif sma ext hull

    if(_df['sma_for_dev'].isnull().all() == False): # #2191EB
        _adps.append(mpf.make_addplot(_df['sma_for_dev'], color='#fc6f03', panel=0))

    if(_df['dev'].isnull().all() == False):
        _adps.append(mpf.make_addplot(_df['dev_dir'], color='#f3ff35', panel=panels)) # while high values represent high instantaneous risk. The
        _adps.append(mpf.make_addplot(_df['dev_sma'], color='#fc6f03', panel=panels))
        # _adps.append(mpf.make_addplot(_df['dev_upper'], color='#2191EB', panel=panels))
        # _adps.append(mpf.make_addplot(_df['dev_lower'], color='#2191EB', panel=panels))
        _adps.append(mpf.make_addplot(_df['0'], color='#808080', panel=panels))

        if(_df['open_long'].isnull().all() == False):
            # _df['buyline'] = _df['riskbuycrossover1'].dropna().mean()
            # _adps.append(mpf.make_addplot(_df['buyline'], color='#febf01', panel=0))
            _adps.append(mpf.make_addplot(_df['open_long'], color='#adff2f',type="scatter", panel=0))
            # _adps.append(mpf.make_addplot(_df['open_long'], color='#febf01',type="scatter", panel=0))
        if(_df['open_short'].isnull().all() == False):
            # _df['sellline'] = _df['risksellcrossunder1'].dropna().mean()
            # _adps.append(mpf.make_addplot(_df['sellline'], color='#adff2f', panel=0))
            _adps.append(mpf.make_addplot(_df['open_short'], color='#febf01',type="scatter", panel=0))
            # _adps.append(mpf.make_addplot(_df['close_long'], color='#adff2f',type="scatter", panel=0))
    
    return _adps

def log_order_open(datetime, _type, ticker, price, volume, balance):
    with open('data/' + 'strategy_log' + '.csv', 'a') as data:
        data.write(datetime + ',' + _type + ',' + ticker + ',' + price + ','+ volume + ',' + balance + '\n')
        data.close()

# def log_order_close():

def generate_signals(_df, account):
    last_row = _df[-1:]
    ticker = config.trade_side_1 + '/' + config.trae_side_2 # AVAX/USD
    # --- Check open_long and open_short, make and them continous. if nan and .shift(1) : df['open_close] = last_row['Close'][]
    profit_target = config.strategy_arguments[3]
    entry_vol = 0
    exit_vol = 0
    entry_size = 0.99
    sell_size = 0.99
    limit_exit_size = config.trailing_exit_args[0]
    trailing_exit_size = config.trailing_exit_args[1] # % of available balance, this could go in config, but it should probably be dynmaic
    balance_threshold = 0.7 # % of total balance, could go in config too, but also should be dynamic
    # Execute long order
    if (last_row['open_long'].iloc[0] == last_row['Close'].iloc[0]):
        entry_price = last_row['Close'].item()
        exit_price = entry_price * profit_target

        if((account.usd_bal / entry_price) < (balance_threshold * account.active_bal)): # Hi AVAX, Low USD - in a long position OR successful shorts
            entry_vol = (account.usd_bal * entry_size) / entry_price
            exit_vol = (account.active_bal * trailing_exit_size)

        elif(((account.usd_bal / entry_price) * balance_threshold) > (account.active_bal)): # Hi USD, Low AVAX - in a short position OR successful longs
                                        # this needs to be somehow generalized as an argument, (ticker and weights)
            if(account.is_short):       # presumably, there are open buys - so cancel them before placing a new one
                account.cancel_all()    # maybe cancel_buys(ticker), cancel_long(ticker) or switch_side() ?
                time.sleep(2)                  # 1?
                entry_vol = (account.usd_bal * entry_size) / entry_price
                exit_vol = entry_vol * limit_exit_size                              
            entry_vol = (account.usd_bal * entry_size) / entry_price
            exit_vol = entry_vol * limit_exit_size      
        else:                                                           # The ratio of AVAX:USD or USD:AVAX is less than 5:1 (80/20)
            entry_vol = (account.usd_bal * entry_size) / entry_price
            exit_vol = entry_vol * limit_exit_size

        account.send_order(_pair = ticker, _type = "buy", _ordertype = "market", 
                       _price = entry_price, _volume = round(entry_vol,2))
        # Await?
        time.sleep(2)
        account.send_order(_pair = ticker, _type = "sell", _ordertype = "limit", 
                            _price = round(exit_price,2), _volume = round(exit_vol,2))
        print("Long Order Sent!")
        balance = str(round(account.usd_bal + (account.active_bal * entry_price),2))
        log_order_open(last_row['Date'][0],"buy",config.trade_ticker,str(round(last_row['Close'][0],2)),str(entry_vol),balance)

        account.last_entry = entry_price
        # account.is_long = True
        # account.is_short = False
        # _df['is_long'] = entry_price

    elif (last_row['full_close'].iloc[0] == last_row['Close'].iloc[0]): # Close a long order 
        entry_price = last_row['Close'].item()
        account.cancel_all() # there may be open sell orders, so cancel them first
        time.sleep(2)        # 1?
        
        if((account.usd_bal / entry_price) < (balance_threshold * account.active_bal)): # Hi AVAX, Low USD - in a long position OR successful shorts
            if(account.is_long):             
                entry_vol = account.active_bal * sell_size
                entry_vol = account.active_bal * sell_size
        elif(((account.usd_bal / entry_price) * balance_threshold) > (account.active_bal)): # Hi USD, Low AVAX - in a short position OR successful longs
                                        # this needs to be somehow generalized as an argument, (ticker and weights)
            entry_vol = account.active_bal * sell_size
        else:
            entry_vol = account.active_bal * sell_size

        account.send_order(_pair = ticker, _type = "sell", _ordertype = "market", 
                       _price = entry_price, _volume = round(entry_vol,2))

        print("Long Order Closed!")
        balance = str(round(account.usd_bal + (account.active_bal * entry_price),2))
        log_order_open(last_row['Date'][0],"sell",config.trade_ticker,str(round(last_row['Close'][0],2)),str(entry_vol),balance)
    
        # account.is_long = False
        # account.is_short = False

    
    # if(crypto_bal >= long_thresh * total_bal): is_long = True
    if(account.active_bal * last_row['Close'].iloc[0] >= (account.usd_bal + (account.active_bal * last_row['Close'].iloc[0])) * config.long_thresh):
        account.is_long = True
    else:
        account.is_long = False
        
    # if (last_row['is_long'].iloc[0] is last_row['Close'].iloc[0]):
    #     account.is_long = True
    # elif ((account.is_long is not False) and last_row['is_long'].iloc[0] is not last_row['Close'].iloc[0]):
    #     account.is_long = False


    # elif ((last_row['close_long'].iloc[0] == last_row['Close'].iloc[0]) and (account.is_long)): # I don't want to have to use .iloc[-1] in the conditional, it should be part of last_row
    #     entry_price = last_row['Close'].item()
        
    #     if((account.usd_bal / entry_price) < (balance_threshold * account.active_bal)): # Hi AVAX, Low USD - in a long position OR successful shorts
    #         if(last_row['Close'] < (account.last_entry * (2-profit_target))):              # presumably, there are open sells - so cancel them before placing a new one
    #             account.cancel_all()
    #             time.sleep(2)                  # 1?
    #         entry_vol = account.active_bal * trailing_exit_size
    #     elif(((account.usd_bal / entry_price) * balance_threshold) > (account.active_bal)): # Hi USD, Low AVAX - in a short position OR successful longs -- Shouldn't happen here
    #                                     # this needs to be somehow generalized as an argument, (ticker and weights)
    #         entry_vol = account.active_bal * trailing_exit_size
    #     else:
    #         entry_vol = account.active_bal * trailing_exit_size
        

    #     account.send_order(_pair = ticker, _type = "sell", _ordertype = "market", 
    #                    _price = entry_price, _volume = round(entry_vol,2))
    #     print("Short Order Sent!")
    #     balance = str(round(account.usd_bal + (account.active_bal * entry_price),2))
    #     log_order_open(last_row['Date'][0],"sell",config.trade_ticker,str(round(last_row['Close'][0],2)),str(entry_vol),balance) # Maybe make a log_order_close()
    
    #     # account.last_entry = entry_price
    #     account.is_long = False
    #     account.is_short = False
    #     # _df['is_short'] = entry_price

    
    return _df
