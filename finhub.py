# API Used is Finnhub
import websocket
import finnhub
from time import sleep
import json

def on_message(ws, message):
    #print(message)
    text = json.loads(message)
    print("="*40)
    for coin in text['data']:
        print(coin['s'])
        print(coin['p'])
    print("="*40)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    #ws.send('{"type":"subscribe","symbol":"AAPL"}')
    #ws.send('{"type":"subscribe","symbol":"AMZN"}')
    ws.send('{"type":"subscribe","symbol":"KRAKEN:XETHZUSD"}')
    #ws.send('{"type":"subscribe","symbol":"KRAKEN:SOLUSD"}')
    #ws.send('{"type":"subscribe","symbol":"KRAKEN:ETHUSD"}')
    #ws.send('{"type":"subscribe","symbol":"BINANCE:SOLUSDT"}')
    #ws.send('{"type":"subscribe","symbol":"COINBASE:BTC-USD"}')
    #ws.send('{"type":"subscribe","symbol":"COINBASE:ETH-USD"}')
    #ws.send('{"type":"subscribe","symbol":"COINBASE:SOL-USD"}')

if __name__ == "__main__":
#def SetupFinnhubApi():
    # Below two lines is for getting all symbols supported by exchange.
    #finnhub_client = finnhub.Client(api_key="coi3j99r01qpcmnisi9gcoi3j99r01qpcmnisia0")
    #print(finnhub_client.crypto_symbols('KRAKEN'))
    #print(finnhub_client.price_target('KRAKEN:XETHZUSD'))
    #print(finnhub_client.stock_symbols("UKRAKEN:XETHZUSD")[0:5])
    #sleep(10)
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=coi3j99r01qpcmnisi9gcoi3j99r01qpcmnisia0",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
