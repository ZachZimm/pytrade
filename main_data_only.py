import sys
import io
# import chart
import pytrade
from datetime import date, datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
# I want to refactor the analysis out of pytrade so that I have a write-only module that listens for data and records to csv (hopefully with a shorter date and just one of them)
# and a read-write module that does analysis 
# import account

# Do I need to implement them as objects?
# I should probably add a kill function to each 'module'

# pytrade (or whatever I name that module) should probably emit some sort of event on every new candle

def round_dt_up(dt, delta):
    return dt + (datetime.min - dt) % delta

RESTART_CHART = 'RESTART_CHART'
RESTART_DATA_COLLECTION = 'RESTART_DATA_COLLECTION'
RESTART_ACCOUNT = 'RESTART_ACCOUNT'
SCHEDULER = BackgroundScheduler()

if __name__ == '__main__':
    import chart as chart
    chart.strategy = config.strategy # The strategy can be switched out like this, and probably just the same for the backtester
    # pytrade.run() 
    # account.run()
    # market_listener = pytrade
    # market_listener.run()
    now = datetime.now()
    data_collect_start = round_dt_up(now, timedelta(minutes=5))
    SCHEDULER.add_job(pytrade.run, run_date=data_collect_start) # I should probably use some arguments here such as ticker(s) and interval
    SCHEDULER.start()

    print("Now:\t\t" + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))
    print("Start:\t\t" + str(data_collect_start.hour) + ":" + str(data_collect_start.minute) + ":" + str(data_collect_start.second))
    print("First Candle:\t" + str(data_collect_start.hour) + ":" + str(data_collect_start.minute + 5) + ":" + str(data_collect_start.second))
    while True: # Will having an infinte loop here wreck performance? Doesn't seem like it. But this still may not be a long-term feature
        keyboard_input = input("Enter Command:\n")
        # if(keyboard_input == RESTART_CHART): # How do I want to do commands? Should I just replace/duplicate the existing command interface?
        #     chart.kill()
        #     chart.run()
        if(keyboard_input == RESTART_DATA_COLLECTION):
            # pytrade.kill() # Do I really need a 'restart' feature? 
            # Is it possible to re-import code and replace what was already in memory? This seems like what I want to do with strategies
            pytrade.run()
        # if(keyboard_input == RESTART_ACCOUNT):
        #     account.kill()
        #     account.run()
        if(keyboard_input == 'quit' or keyboard_input == 'exit'):
            break

# TODO
# No need to store a dataframe in the OHLCTV class. It's probably a huge waste of resources (not that it matters much at this point).
    # Just append the new data, maybe run an intial check to be sure of the column formatting
# Refactor OHLC(TV) class into another file
# Record volume - which one is it in the trade message?
# Test with charts, maybe I'll follow Derek and use Plotly
# Get derivitaves with numpy.gradient()
# Get indicators / signals working
# Connect to Kraken with credentials
# Monitor positions, keep track of changes and whether they were made manually - maybe even keep a csv of account values
# Send trades, keep track of all trades sent, and further monitor those positions - maybe use limit orders
# Pat myself on the back
# Do up some nicer UI, chart portfolio changes, buys/sells, # of trades, and the like

# Insert data function?
# Trailing stop?