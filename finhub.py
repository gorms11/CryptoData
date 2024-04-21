# API Used is Finnhub
import websocket
import finnhub

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    pass
    #ws.send('{"type":"subscribe","symbol":"AAPL"}')
    #ws.send('{"type":"subscribe","symbol":"AMZN"}')
    ws.send('{"type":"subscribe","symbol":"KRAKEN:XETHZUSD"}')
    ws.send('{"type":"subscribe","symbol":"KRAKEN:SOLUSD"}')
    #ws.send('{"type":"subscribe","symbol":"KRAKEN:ETHUSD"}')
    #ws.send('{"type":"subscribe","symbol":"BINANCE:SOLUSDT"}')

if __name__ == "__main__":
    # Below two lines is for getting all symbols supported by exchange.
    #finnhub_client = finnhub.Client(api_key="coi3j99r01qpcmnisi9gcoi3j99r01qpcmnisia0")
    #print(finnhub_client.crypto_symbols('KRAKEN'))
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://ws.finnhub.io?token=coi3j99r01qpcmnisi9gcoi3j99r01qpcmnisia0",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()

