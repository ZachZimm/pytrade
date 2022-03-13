import time
import os
import requests
import urllib.parse,urllib.request
import hashlib
import hmac
import base64
import json

def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


# Read Kraken API key and secret stored in environment variables
# api_key = os.environ['API_KEY_KRAKEN']
# api_sign = os.environ['API_SEC_KRAKEN']

# Attaches auth headers and returns results of a POST request
def kraken_request(uri_path, data, api_key, api_sign):
    api_url = "https://api.kraken.com"
    headers = {}
    headers['API-Key'] = api_key
    # get_kraken_signature() as defined in the 'Authentication' section
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sign)             
    req = requests.post((api_url + uri_path), headers=headers, data=data)
    return req

def get_bal(api_key, api_sign):
    # Construct the request and print the result
    resp = kraken_request('/0/private/Balance', {
        "nonce": str(int(1000*time.time()))
    }, api_key, api_sign)

    return resp.json()

def cancel_all(api_key, api_sign):
    resp = kraken_request('/0/private/CancelAll', {
        "nonce": str(int(1000*time.time()))
    }, api_key, api_sign)

def get_ws_key(api_key, api_sign):
    api_nonce = bytes(str(int(time.time()*1000)), "utf-8")
    api_request = urllib.request.Request("https://api.kraken.com/0/private/GetWebSocketsToken", b"nonce=%s" % api_nonce)
    api_request.add_header("API-Key", api_key)
    api_request.add_header("API-Sign", base64.b64encode(hmac.new(base64.b64decode(api_sign), b"/0/private/GetWebSocketsToken" + hashlib.sha256(api_nonce + b"nonce=%s" % api_nonce).digest(), hashlib.sha512).digest()))

    return json.loads(urllib.request.urlopen(api_request).read())['result']['token']