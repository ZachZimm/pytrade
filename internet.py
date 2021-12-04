import socket
import time
from apscheduler.schedulers.background import BackgroundScheduler
import csv
from datetime import datetime, tzinfo
import pytz

def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    is_connected = 0
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))   
        is_connected = 1
    except socket.error as ex:
        print(ex)
        print('Internet connection lost!')
        time.sleep(4) # To better keep the schedule after a timeout
    with open('stat/' + 'is_connected' + '.csv', 'a') as data:
        while True:
            newtime = datetime.now(tz=pytz.UTC)
            # start_interval_minutes = 1
            # if((newtime.minute % start_interval_minutes) == 0 and (newtime.second % 5) == 0 and newtime.microsecond <= 1000): # use this when start_interval > 1
            if(newtime.second % 5 == 0) and (newtime.microsecond <= 1000):
                date_time = newtime.strftime("%Y-%m-%d %H:%M:%S.%f")
                data.write(date_time + ',' + str(is_connected) + ',\n')
                break
        if(is_connected == 1):
            print(date_time + ' - Connected!')
        data.close()

def start():
    loop = True
    start_interval_minutes = 1 # Testing will begin at (currenttime % start_interval_minutes), so if it is set to 5, testing start will be at hh:05:0,0 hh:10:00, hh:15:00, etc...
    test_interval_seconds=20 # How often to check the connection
    scheduler = BackgroundScheduler() # Set this before the start loop so as to minimize time between the end of the loop and the beginning of data collection
    scheduler.add_job(internet, 'interval', seconds=test_interval_seconds) # call new_candle every x seconds
    # print('Internet tester is starting, waiting for the next ' + str(start_interval_minutes) + ' interval to begin data collection')
    while loop == True:
        newtime = datetime.now(tz=pytz.UTC)
        # if((newtime.minute % start_interval == 0) and newtime.second == 0 and newtime.microsecond == 0) # use this when start_interval > 1
        # if(newtime.second == 0 and newtime.microsecond <= 1000):
        # print(millis)
        if((newtime.second % 20 == 0) and (newtime.microsecond <= 1000)):
            loop = False
            break
    
    scheduler.start()
    date_time = newtime.strftime("%Y-%m-%d %H:%M:%S.%f")
    print(date_time + ' - Testing started!')
    while True:
        time.sleep(5)
   
if (__name__ == '__main__'):
    try:
        with open(('stat/' + 'is_connected' + '.csv'), 'r') as data:
            is_data = str(data.readline()) == 'Date,is_connected,\n'
            if (is_data == False):
                raise ValueError('Found the wrong data in is_connected.csv stat file, overwriting..')
            data.close()
    except:                                                                 
        print('Failed to find old data in is_connected.csv, starting a new database instead and potentially overwriting')
        with open(('stat/' + 'is_connected' + '.csv'), 'w') as data:
                data.write('Date,is_connected,\n')
                data.close()
    start()

    
    