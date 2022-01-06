import numpy as np
import ta
import mplfinance as mpf

def normalize(data):
    max_value = data.max()
    min_value = data.min()
    # data = (data - min_value) / (max_value - min_value)
    if(min_value > 0):
        data = ((data - min_value) / (max_value - min_value))
    elif(min_value < 0):
        data = ((data + min_value) / (max_value - min_value))
    else:
        data = (data / max_value)
    return data

def WMA(s, period):
       return s.rolling(period).apply(lambda x: ((np.arange(period)+1)*x).sum()/(np.arange(period)+1).sum(), raw=True)

def HMA(s, period):
       return WMA(WMA(s, period//2).multiply(2).sub(WMA(s, period)), int(np.sqrt(period)))

def SMA(s, period): # This causes errors for some reason
    return s.rolling(window=140, min_periods=1).mean()

def define_hull(df):
    df['hma9'] = HMA(df['Close'],9)
    df['hma140'] = HMA(df['Close'],140)
    df['hma200'] = HMA(df['Close'],200)
    df['hma500'] = HMA(df['Close'],500)

    return df

def define_risk(df):
    df['sma50_'] = df['Close'].rolling(window=50, min_periods=1).mean()
    df['sma350_'] = df['Close'].rolling(window=350, min_periods=1).mean()
    # indicator_50sma = ta.trend.sma_indicator(close=df["Close"], window=50)
    # indicator_350sma = ta.trend.sma_indicator(close=df["Close"], window=350)
    # df['risk'] = normalize(df['risk'])    # NOT normalized for now
    df['sma50'] = ta.trend.sma_indicator(close=df["Close"], window=50)
    df['sma350'] = ta.trend.sma_indicator(close=df["Close"], window=350)
    df['risk'] = df['sma50']/df['sma350'] # 'risk' 


    df['hma50'] = HMA(df['Close'],50)
    df['hma350'] = HMA(df['Close'],350)
    df['hrisk'] = df['hma50']/df['sma350']   
    # df['hrisk'] = normalize(df['hrisk'])  # NOT normalized for now
    return df

def define_risk_dif(df): # Is this a measure of momentum?
    df['riskdif'] = df['risk'] - df['hrisk']
    df['0'] = (df['riskdif'] * 0)
    df['difcrossover'] = np.where((df['riskdif'] > 0) & (df['riskdif'].shift(1) <= 0), df['Close'] * 1, np.nan)
    df['difcrossunder'] = np.where((df['riskdif'] < 0) & (df['riskdif'].shift(1) >= 0), df['Close'] * 1, np.nan)
    return df

def define_risk_ribbon(_df):
    _length = 200
    _risk_ma_length = 200
    # _df['riskma'] = _df['risk'].rolling(_risk_ma_length).mean()
    risk_std_dev = _df['risk'].rolling(_risk_ma_length).std()
    rband1 = ta.volatility.BollingerBands(close=_df['risk'], window=_length, window_dev=1)
    rband175 = ta.volatility.BollingerBands(close=_df['risk'], window=_length, window_dev=1.75)
    rband25 = ta.volatility.BollingerBands(close=_df['risk'], window=_length, window_dev=2.5)
    rband29 = ta.volatility.BollingerBands(close=_df['risk'], window=_length, window_dev=2.9)
    # _df['riskma'] = ta.trend.sma_indicator(close=_df['risk'], window=_risk_ma_length)
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

def define_risk_scatter(df,ticker):
    if(ticker == 'SPY'):
        bbound1 = 0.7
        bbound2 = 0.6
        sbound1 = 0.8
        sbound2 = 0.91
        hbbound1 = 0.5
        hsbound1 = 0.9
    elif(ticker == 'BTC-USD'):
        bbound1 = 0.35
        bbound2 = 0.24
        sbound1 = 0.75
        sbound2 = 0.8

        hbbound1 = 0.2
        hsbound1 = 0.6
    else:
        bbound1 = 0.4
        bbound2 = 0.3
        sbound1 = 0.90
        sbound2 = 0.8
        hbbound1 = 0.3
        hsbound1 = 0.85
    df['BuySignal1'] = np.where(df['risk'] < bbound1, df['Close'] * 1, np.nan)
    df['BuySignal2'] = np.where(df['risk'] < bbound2, df['Close'] * 1, np.nan)
    df['SellSignal1'] = np.where(df['risk'] > sbound1, df['Close'] * 1, np.nan)
    df['SellSignal2'] = np.where(df['risk'] > sbound2, df['Close'] * 1, np.nan)

    df['HBuySignal1'] = np.where(df['hrisk'] < hbbound1, df['Close'] * 1, np.nan)
    df['HSellSignal1'] = np.where(df['hrisk'] > hsbound1, df['Close'] * 1, np.nan)
    return df

def define_sma(df):
    df['sma20'] = df['Close'].rolling(window=20, min_periods=1).mean()
    df['sma140'] = df['Close'].rolling(window=140, min_periods=1).mean()
    df['sma200'] = df['Close'].rolling(window=200, min_periods=1).mean()
    return df

def define_ma_ext(df):
    df['sma140'] = SMA(df['Close'], 140)
    df['ext'] = ((df['Close'] - df['sma140']) / df['sma140']) * 100
    df['E0'] = (df['Close'] * 0)
    df['ext'] = normalize(df['ext'])
    return df

def intersection(lst1, lst2): # Returns the intersection of two lists
    return list(set(lst1) & set(lst2))

def define_indicators(_ticker, _df, _indicators):
    reqSMA = ['sma', 'ext', 'risk', 'riskscatter', 'riskdif', 'riskribbon'] # SMA (simple moving average)
    if(len(intersection(reqSMA, _indicators)) > 0): # Check to see if the two lists have any shared members
        _df = define_sma(_df)
    reqHULL = ['hull', 'risk', 'riskscatter', 'riskdif', 'riskribbon']
    if(len(intersection(reqHULL, _indicators)) > 0):
        _df = define_hull(_df)
    reqEXT = ['ext']
    if(len(intersection(reqEXT, _indicators)) > 0):
        _df = define_ma_ext(_df)
    reqRISK = ['risk', 'riskscatter', 'riskdif', 'riskribbon'] # risk - plots two lines each derrived from the quotient of (short term MA / long term MA)
    if(len(intersection(reqRISK, _indicators)) > 0): # The quoteients are normalized to a scale of 0-1, low values represent low instantaneous risk
        _df = define_risk(_df)
        if(('riskscatter' in _indicators)):
            _df = define_risk_scatter(_df, _ticker)
        if('riskdif' in _indicators):
            _df = define_risk_dif(_df)
        if('riskribbon' in _indicators):
            _df = define_risk_ribbon(_df)
    return _df

def add_indicators(_ticker, _df, _indicators):
    panels = 1
    _adps = [] # Indicators: risk riskscatter riskdif sma ext hull
               # Eventually I should make them customizable, ie sma:9, hull:500 riskscatter:0.2,0.9
    if('sma' in _indicators): # Check to see if reqSMA (str list) and _indicators (string) have any shared members
        _adps.append(mpf.make_addplot(_df['sma20']))
        _adps.append(mpf.make_addplot(_df['sma140']))
        _adps.append(mpf.make_addplot(_df['sma200']))
    if('hull' in _indicators):
        _df = define_hull(_df)
        # _adps.append(mpf.make_addplot(_df['hma9'],color='#adff2f'))
        _adps.append(mpf.make_addplot(_df['hma140'],color='#adff2f'))
        _adps.append(mpf.make_addplot(_df['hma200'],color='#adff2f'))
        # _adps.append(mpf.make_addplot(_df['hma500'],color='#adff2f')) For some reason, HMA() only uses df_sub. I think it has something to do with
    if('ext' in _indicators):                                                                                                       #df[].rolling()
        _adps.append(mpf.make_addplot(_df['ext'],color='#adff2f', panel=panels))
        # _adps.append(mpf.make_addplot(_df['E0'], panel=panels))
        # _adps.append(mpf.make_addplot(_df['0'], color='#0000ff',panel=panels))
        panels = panels + 1
    if('risk' in _indicators):
        _adps.append(mpf.make_addplot(_df['risk'], color='#ff5500', panel=panels)) # while high values represent high instantaneous risk. The
        _adps.append(mpf.make_addplot(_df['hrisk'], color='#adff2f',panel=panels)) # directionality of the risk plot (its derivative) is likewise
        _adps.append(mpf.make_addplot(_df['sma50'], color='#adff2f',panel=0))
        _adps.append(mpf.make_addplot(_df['sma350'], color='#ff5500', panel=0))

        panels = panels + 1
    if('riskribbon' in _indicators):
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

    if(('riskscatter' in _indicators)): # Buy/Sell scatter plot
        # SMA calculated risk signals
        # _adps.append(mpf.make_addplot(_df['BuySignal1'] * 0.96,type="scatter", color=['#00aa00']))
        # _adps.append(mpf.make_addplot(_df['BuySignal2'] * 0.96,type="scatter", color=['#005500']))
        # _adps.append(mpf.make_addplot(_df['SellSignal1'] * 1.04,type="scatter", color=['#ff0000']))
        # _adps.append(mpf.make_addplot(_df['SellSignal2'] * 1.04,type="scatter", color=['#8a0000']))
        # HMA calculated risk signals
        if(_df['HBuySignal1'].isnull().all() == False):
            _adps.append(mpf.make_addplot(_df['HBuySignal1'] * 0.96,type="scatter", color=['#00aa00']))
        if(_df['HSellSignal1'].isnull().all() == False):
            _adps.append(mpf.make_addplot(_df['HSellSignal1'] * 1.04,type="scatter", color=['#ff0000']))
    if('riskdif' in _indicators):
        _adps.append(mpf.make_addplot(_df['riskdif'], color='#febf01',panel=panels)) # Riskdif plots a point whenver the two different risk 
        if(_df['difcrossover'].isnull().all() == False):
            _adps.append(mpf.make_addplot(_df['difcrossover'],type="scatter", color=['#febf01'])) # measurments cross (on their individually
            _adps.append(mpf.make_addplot(_df['0'], panel=panels))
        if(_df['difcrossunder'].isnull().all() == False):
            _adps.append(mpf.make_addplot(_df['difcrossunder'],type="scatter", color=['#adff2f'])) # normalized scales)
        panels = panels + 1
    
    return _adps