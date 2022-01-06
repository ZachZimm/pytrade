import pandas as pd

def read_to_df(ticker):
    try:
        df = pd.read_csv('./data/' + ticker + '.csv')
    except FileNotFoundError:
        print('File does not exist')
    else:
        df = df.dropna(subset=['Close'])
        return df