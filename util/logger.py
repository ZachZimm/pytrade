import datetime as dt

def ws_log(message):
    now = dt.datetime.now()
    time = str(now.year)+'-'+str(now.month)+'-'+str(now.day)+' '+str(now.hour)+':'+str(now.minute)+':'+str(now.second)
    try:
        open('data/'+'ws_messages'+'.log','r')
        with open('data/' + 'ws_messages' + '.log', 'a') as f:
            f.write(time + ',' + message + '\n')
            f.close()
    except:
        with open('data/' + 'ws_messages' + '.log', 'w') as f:
            f.write('date,message\n')
            f.write(time + ',' + message + '\n')
            f.close()
