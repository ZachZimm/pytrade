# Import WebSocket client library (and others)
import websocket
import _thread
import time
from secret import WS_Key
import json

is_connected = False
order_sent = False
# Define WebSocket callback functions
def ws_message(ws, message):
    print("WebSocket thread: %s" % message)
    obj = json.loads(message)
    if ((len(obj) == 4) and ('connectionID' not in obj)): # I don't think this does anything useful here
        print(obj[2] + " : " + obj[1][0][0])
        if(obj[1] == 'openOrders'):
            global BTCUSD
            BTCUSD.new_data(float(obj[1][0][0]))
        if(obj[1] == 'ownTrades'):
            global ETHBTC
            ETHBTC.new_data(float(obj[1][0][0]))
    global is_connected
    global order_sent
    if(is_connected and not order_sent):
        print("Sending order..")
        # send_order(ws)
        cancel_order(ws, "OBKJWD-7BDTZ-Z6ADET")
    # if(is_connected == False):
        # is_connected = True

        # [[{"OTAJHK-A2MKA-TPL7OY":{"avg_price":"0.000000","cost":"0.000000","descr":{"close":null,"leverage":null,
            # "order":"buy 0.13196954 ETH/XBT @ limit 0.079530","ordertype":"limit","pair":"ETH/XBT","price":"0.079530",
            # "price2":"0.000000","type":"buy"},"expiretm":null,"fee":"0.000000","limitprice":"0.000000","misc":"",
            # "oflags":"fciq","opentm":"1638668222.895850","refid":null,"starttm":null,"status":"pending",
            # "stopprice":"0.000000","timeinforce":"GTC","userref":0,"vol":"0.13196954","vol_exec":"0.00000000"}}],"openOrders",{"sequence":2}] - Trade Manually Placed Message
        # [[{"OTAJHK-A2MKA-TPL7OY":{"status":"open","userref":0}}],"openOrders",{"sequence":3}] - Trade status becomes open message

def send_order(ws): # should take a JSON object as second argument, and pretty much just pass that to ws.send
    _pair = "XBT/USD"
    _type = "sell"
    _ordertype = "limit"
    _price = "70000"
    _volume = "0.005"
    ws.send('{"event":"addOrder", "token":"%s", "pair":"%s", "type":"%s", "ordertype":"%s", "price": "%s", "volume":"%s"}' % (WS_Key,_pair, _type, _ordertype, _price, _volume))
    global order_sent
    order_sent = True

    # {"descr":"sell 0.00500000 XBTUSD @ limit 70000.0","event":"addOrderStatus","status":"ok","txid":"OBKJWD-7BDTZ-Z6ADET"} - Order sent
    # [[{"OBKJWD-7BDTZ-Z6ADET":{"avg_price":"0.00000","cost":"0.00000","descr":{"close":null,"leverage":null,"order":"
        # sell 0.00500000 XBT/USD @ limit 70000.00000","ordertype":"limit","pair":"XBT/USD","price":"70000.00000",
        # "price2":"0.00000","type":"sell"},"expiretm":null,"fee":"0.00000","limitprice":"0.00000","misc":"",
        # "oflags":"fciq","opentm":"1638670254.904810","refid":null,"starttm":null,"status":"pending","stopprice":"0.00000",
        # "timeinforce":"GTC","userref":0,"vol":"0.00500000","vol_exec":"0.00000000"}}],"openOrders",{"sequence":2}] - Order Pending
    # [[{"OBKJWD-7BDTZ-Z6ADET":{"status":"open","userref":0}}],"openOrders",{"sequence":3}] - Order Open

def cancel_order(ws, txid):
    _txid = txid
    ws.send('{"event": "cancelOrder","token": "%s","txid": ["%s"]}' % (WS_Key, _txid))
    order_sent = True

    # {"event":"cancelOrderStatus","status":"ok"} - Cancel Order Sent
    # [[{"OBKJWD-7BDTZ-Z6ADET":{"lastupdated":"1638670886.658310","status":"canceled",
        # "vol_exec":"0.00000000","cost":"0.00000","fee":"0.00000","avg_price":"0.00000",
        # "userref":0,"cancel_reason":"User requested"}}],"openOrders",{"sequence":2}] - Order Canceled
    
def ws_open(ws):
    ws.send('{"event":"subscribe", "subscription":{"name":"openOrders", "token":"%s"}}' % WS_Key)
    ws.send('{"event":"subscribe", "subscription":{"name":"ownTrades", "token":"%s"}}' % WS_Key)

def ws_thread(*args):
    ws = websocket.WebSocketApp("wss://ws-auth.kraken.com/", on_open = ws_open, on_message = ws_message)
    ws.run_forever()

# Start a new thread for the WebSocket interface
_thread.start_new_thread(ws_thread, ())

# Continue other (non WebSocket) tasks in the main thread
while True:
    time.sleep(5)
    print("Main thread: %d" % time.time())
    # global is_connected
    is_connected = True
    