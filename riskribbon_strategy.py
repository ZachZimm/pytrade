import numpy as np
import ta
import mplfinance as mpf

def WMA(s, period):
       return s.rolling(period).apply(lambda x: ((np.arange(period)+1)*x).sum()/(np.arange(period)+1).sum(), raw=True)

def HMA(s, period):
       return WMA(WMA(s, period//2).multiply(2).sub(WMA(s, period)), int(np.sqrt(period)))


def define_hull(df):
    df['hma9'] = HMA(df['Close'],9)
    df['hma140'] = HMA(df['Close'],140)
    df['hma200'] = HMA(df['Close'],200)
    df['hma500'] = HMA(df['Close'],500)

    return df

def define_risk(df):
    df['sma50'] = ta.trend.sma_indicator(close=df["Close"], window=50)
    df['sma350'] = ta.trend.sma_indicator(close=df["Close"], window=350)
    df['risk'] = df['sma50']/df['sma350'] # 'risk' 

    # df['hma50'] = HMA(df['Close'],50)
    # df['hma350'] = HMA(df['Close'],350)
    # df['hrisk'] = df['hma50']/df['sma350']   
    return df

def define_risk_ribbon(_df):
    _length = 200
    _risk_ma_length = 200
    risk_std_dev = _df['risk'].rolling(_risk_ma_length).std()
    rband1 = ta.volatility.BollingerBands(close=_df['risk'], window=_length, window_dev=1)
    rband175 = ta.volatility.BollingerBands(close=_df['risk'], window=_length, window_dev=1.75)
    rband25 = ta.volatility.BollingerBands(close=_df['risk'], window=_length, window_dev=2.5)
    rband29 = ta.volatility.BollingerBands(close=_df['risk'], window=_length, window_dev=2.9)
    _df['riskma'] = rband1.bollinger_mavg()
    # _df['1rdevlower'] = _df['riskma'] - (1 * risk_std_dev)
    # _df['175rdevlower'] = _df['riskma'] - (1.75 * risk_std_dev)
    # _df['25rdevlower'] = _df['riskma'] - (2.5 * risk_std_dev)
    _df['1rdevlower'] = rband1.bollinger_lband()
    _df['175rdevlower'] = rband175.bollinger_lband()
    _df['25rdevlower'] = rband25.bollinger_lband()

    _df['1rdevupper'] = rband1.bollinger_hband()
    _df['25rdevupper'] = rband25.bollinger_hband()
    _df['29rdevupper'] = rband29.bollinger_hband()

    _df['riskbuycrossover1'] = np.where((_df['risk'] > _df['25rdevlower']) & (_df['risk'].shift(1) <= _df['25rdevlower'].shift(1)), _df['Close'] * 1, np.nan)
    _df['risksellcrossunder1'] = np.where((_df['risk'] < _df['29rdevupper']) & (_df['risk'].shift(1) >= _df['29rdevupper'].shift(1)), _df['Close'] * 1, np.nan)
    # _df['1rdevupper'] = _df['riskma'] + (1 * risk_std_dev)
    # _df['25rdevupper'] = _df['riskma'] + (2.5 * risk_std_dev)
    
    # _df['29rdevupper'] = _df['hrisk'] + (2.9 * _df['risk'].rolling(_length).std())        # This is kind of interesting, maybe I should look into it
    # _df['25rdevlower'] = _df['hrisk'] - (2.5 * _df['risk'].rolling(_length).std())
    return _df

def intersection(lst1, lst2): # Returns the intersection of two lists
    return list(set(lst1) & set(lst2))

def define_indicators(_ticker, _df, _indicators, is_backtest = False): # This should proably accept a bool for backtesting 
    max_lookback = 2000 # This should probably be determined on a per-strategy basis
    if(is_backtest):    # Maybe set a maximum where I call this function in chart.py as well
        max_lookback = 2000
    # _df = define_hull(_df)
    _df = define_risk(_df)
    _df = define_risk_ribbon(_df)
    return _df

def add_indicators(_ticker, _df, _indicators):
    panels = 1
    _adps = [] # Indicators: risk riskscatter riskdif sma ext hull

    if(_df['risk'].isnull().all() == False):
        _adps.append(mpf.make_addplot(_df['risk'], color='#f3ff35', panel=panels)) # while high values represent high instantaneous risk. The
        # _adps.append(mpf.make_addplot(_df['hrisk'], color='#adff2f',panel=panels)) # directionality of the risk plot (its derivative) is likewise
        _adps.append(mpf.make_addplot(_df['1rdevlower'], color='#bcbcbc', panel=panels))
        _adps.append(mpf.make_addplot(_df['175rdevlower'], color='#2191EB', panel=panels))
        _adps.append(mpf.make_addplot(_df['25rdevlower'], color='#2191EB', panel=panels))        
        _adps.append(mpf.make_addplot(_df['riskma'], color='#acbcbc', panel=panels))
        _adps.append(mpf.make_addplot(_df['1rdevupper'], color='#bcbcbc', panel=panels))
        _adps.append(mpf.make_addplot(_df['25rdevupper'], color='#2191EB', panel=panels))
        _adps.append(mpf.make_addplot(_df['29rdevupper'], color='#2191EB', panel=panels))

        if(_df['riskbuycrossover1'].isnull().all() == False):
            _df['buyline'] = _df['riskbuycrossover1'].dropna().mean()
            _adps.append(mpf.make_addplot(_df['buyline'], color='#febf01', panel=0))
            _adps.append(mpf.make_addplot(_df['riskbuycrossover1'], color='#febf01',type="scatter", panel=0))
        if(_df['risksellcrossunder1'].isnull().all() == False):
            _df['sellline'] = _df['risksellcrossunder1'].dropna().mean()
            _adps.append(mpf.make_addplot(_df['sellline'], color='#adff2f', panel=0))
            _adps.append(mpf.make_addplot(_df['risksellcrossunder1'], color='#adff2f',type="scatter", panel=0))
    
    return _adps

def generate_signals(_df, account): # TODO run define_indicators() every 5 minutes and pass the result to generate_signals() i.e. generate_signals(define_indicators(df)) - Maybe use a maximum length to load
    last_row = _df[-1:]
    if (last_row['riskbuycrossover1'] == last_row['Close']):
        volume = account.btc_bal * 0.5
        account.send_order(_pair = "ETH/XBT", _type = "buy", _ordertype = "limit", 
                           _price = str(last_row['Close']), _volume = volume)
        print('Buy %s at %s' % (volume, last_row['Close']))
        
    if (last_row['risksellcrossunder1'] == last_row['Close']):
        volume = account.eth_bal * 0.75
        print('Sell %s at %s' % (volume, last_row['Close']))