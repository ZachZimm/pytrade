# Import WebSocket client library (and others)
import websocket
import _thread
import time
import json
import secret # Websocket API token
from datetime import datetime
import util.kraken as kraken

class Account:
    def __init__(self, tickers): # 'Tickers' is a list of strings
        self.is_connected = False
        self.btc_bal = 0.0
        self.eth_bal = 0.0
        self.tickers = tickers
        secret.WS_Key = kraken.get_ws_key(secret.API_Key, secret.API_Sign)
        self.get_balances()
        # self.token = WS_Key # Websocket API token
        _thread.start_new_thread(self.ws_thread, ())
        

    # def connect(self, ws):
    #     self.is_connected = True
    #     self.ws = ws

    def ws_thread(self, *args):
        self.ws = websocket.WebSocketApp("wss://ws-auth.kraken.com/", on_open = self.ws_open, on_message = self.ws_message, on_close = self.ws_close)
        self.ws.run_forever()

    def ws_message(self, ws, message):
        obj = json.loads(message)
        # print(message)
        # if(obj[0] != 'heartbeat'):
        if('heartbeat' not in message):
            print(message + '\n')
        # print("Account Message:\n%s" % message)
        # if ((len(obj) == 4) and ('connectionID' not in obj)): # I don't think this does anything useful here
        #     print(obj[2] + " : " + obj[1][0][0]) # And neither does this
        #     if(obj[1] == 'openOrders'):
        #         # global BTCUSD
        #         # BTCUSD.new_data(float(obj[1][0][0]))
        #         print('Open Orders Message Recieved')
        #     if(obj[1] == 'ownTrades'):
        #         # global ETHBTC
        #         # ETHBTC.new_data(float(obj[1][0][0]))
        #         print('Own Trades Message Recieved')
        # global order_sent
        # if(self.is_connected and not order_sent):
        #     print("Sending order..")
        #     # send_order(ws)
        #     self.cancel_order(ws, "OBKJWD-7BDTZ-Z6ADET")

    # if(is_connected == False):
        # is_connected = True

        # [[{"OTAJHK-A2MKA-TPL7OY":{"avg_price":"0.000000","cost":"0.000000","descr":{"close":null,"leverage":null,
            # "order":"buy 0.13196954 ETH/XBT @ limit 0.079530","ordertype":"limit","pair":"ETH/XBT","price":"0.079530",
            # "price2":"0.000000","type":"buy"},"expiretm":null,"fee":"0.000000","limitprice":"0.000000","misc":"",
            # "oflags":"fciq","opentm":"1638668222.895850","refid":null,"starttm":null,"status":"pending",
            # "stopprice":"0.000000","timeinforce":"GTC","userref":0,"vol":"0.13196954","vol_exec":"0.00000000"}}],"openOrders",{"sequence":2}] - Trade Manually Placed Message
        # [[{"OTAJHK-A2MKA-TPL7OY":{"status":"open","userref":0}}],"openOrders",{"sequence":3}] - Trade status becomes open message

    def ws_open(self, ws):
        self.ws.send('{"event":"subscribe", "subscription":{"name":"openOrders", "token":"%s"}}' % secret.WS_Key)
        # self.ws.send('{"event":"subscribe", "subscription":{"name":"ownTrades", "token":"%s"}}' % secret.WS_Key) # I'm not sure I need this because addOrder sends responses

    def ws_close(self, ws, arg2, arg3): # I don't think the arguments are very important here
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print('Disconnected from Kraken account at %s' % current_time)
        reconnect_delay = 5
        print("Attempting reconnect..")
        while True: # and internet_connected() ?
            time.sleep(reconnect_delay)
            try:
                secret.WS_Key = kraken.get_ws_key(secret.API_Key, secret.API_Sign)
                self.ws = websocket.WebSocketApp("wss://ws-auth.kraken.com/", on_open = self.ws_open, on_close=self.ws_close, on_message = self.ws_message)
                self.ws.run_forever()
                break
            except:
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print('Failed to reconnect')
                print("Attempting reconnect in %s seconds.." % current_time)

    def send_order(self, _pair, _type, _ordertype, _price, _volume):
        self.ws.send('{"event":"addOrder", "token":"%s", "pair":"%s", "type":"%s", "ordertype":"%s", "price": "%s", "volume":"%s"}' % (secret.WS_Key, _pair, _type, _ordertype, _price, _volume))

        # {"descr":"sell 0.00500000 XBTUSD @ limit 70000.0","event":"addOrderStatus","status":"ok","txid":"OBKJWD-7BDTZ-Z6ADET"} - Order sent
        # [[{"OBKJWD-7BDTZ-Z6ADET":{"avg_price":"0.00000","cost":"0.00000","descr":{"close":null,"leverage":null,"order":"
            # sell 0.00500000 XBT/USD @ limit 70000.00000","ordertype":"limit","pair":"XBT/USD","price":"70000.00000",
            # "price2":"0.00000","type":"sell"},"expiretm":null,"fee":"0.00000","limitprice":"0.00000","misc":"",
            # "oflags":"fciq","opentm":"1638670254.904810","refid":null,"starttm":null,"status":"pending","stopprice":"0.00000",
            # "timeinforce":"GTC","userref":0,"vol":"0.00500000","vol_exec":"0.00000000"}}],"openOrders",{"sequence":2}] - Order Pending
        # [[{"OBKJWD-7BDTZ-Z6ADET":{"status":"open","userref":0}}],"openOrders",{"sequence":3}] - Order Open

    def cancel_order(self, txid):
        _txid = txid
        self.send('{"event": "cancelOrder","token": "%s","txid": ["%s"]}' % (secret.WS_Key, _txid))

        # {"event":"cancelOrderStatus","status":"ok"} - Cancel Order Sent
        # [[{"OBKJWD-7BDTZ-Z6ADET":{"lastupdated":"1638670886.658310","status":"canceled",
            # "vol_exec":"0.00000000","cost":"0.00000","fee":"0.00000","avg_price":"0.00000",
            # "userref":0,"cancel_reason":"User requested"}}],"openOrders",{"sequence":2}] - Order Canceled
        
    def get_balances(self):
        self.btc_bal = float(kraken.get_bal(secret.API_Key, secret.API_Sign)['result']['XXBT'])
        self.eth_bal = float(kraken.get_bal(secret.API_Key, secret.API_Sign)['result']['XETH'])
