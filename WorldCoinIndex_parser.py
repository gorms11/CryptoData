#example for parsing crypto data from the worldcoinindex API
import requests
import json
import datetime


r = requests.get(url='https://www.worldcoinindex.com/apiservice/ticker?key=1aACv4j5Mj8wuJWthbuAYZiBYCFwVR&label=ethbtc-ltcbtc&fiat=usd')
print(r.json())
print('\n')
data = str(r.json())
data =json.loads(data.replace("\'", "\""))

new_list = list(data['Markets'])

ethereum = dict(new_list[0])
ETH_timestamp = str(datetime.datetime.fromtimestamp(ethereum['Timestamp']))
ethereum['Timestamp'] = ETH_timestamp
litecoin = dict(new_list[1])
LTC_timestamp = str(datetime.datetime.fromtimestamp(litecoin['Timestamp']))
litecoin['Timestamp'] = LTC_timestamp
print("array order: ", 'Name, price, 24hr Volume, Timestamp', '\n')
array_list = [[ethereum['Name'], ethereum['Price'], ethereum['Volume_24h'], ethereum['Timestamp']], [litecoin['Name'], litecoin['Price'], litecoin['Volume_24h'], litecoin['Timestamp']]]
for x in range(0,2):
    for y in range(0,4):
        print(array_list[x][y], end=" ")
    print('\n')
