import json
import os
import pandas as pd
import urllib.request
import datetime
import tkinter as tk
from time import sleep


def JSONDictToDF(d):
    '''
    Converts a dictionary created from json.loads to a pandas dataframe
    d:      The dictionary
    '''
    length = len(d)
    cols = []
    if length > 0:  # Place the column in sorted order
        cols = sorted(list(d[0].keys()))
    df = pd.DataFrame(columns=cols, index=range(length))
    for i in range(length):
        for coli in cols:
            df.set_value(i, coli, d[i][coli])
    return df


def GetAPIUrl(cur):
    '''
    Makes a URL for querying historical prices of a cyrpto from Poloniex
    cur:    3 letter abbreviation for cryptocurrency (BTC, LTC, etc)
    '''
    url = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms=' + cur + '&tsyms=USD'
    return url


def GetCurDF(cur, fp):
    '''
    cur:    3 letter abbreviation for cryptocurrency (BTC, LTC, etc)
    fp:     File path (to save price data to CSV)
    '''
    openUrl = urllib.request.urlopen(GetAPIUrl(cur))
    web_data = openUrl.read()
    openUrl.close()
    json_web_data = json.loads(web_data)
    timestamp = str(datetime.datetime.fromtimestamp(json_web_data["RAW"][cur]["USD"]['LASTUPDATE']))
    json_web_data["RAW"][cur]["USD"]['LASTUPDATE'] = timestamp
    string_json_web_data = str(json_web_data["RAW"][cur]["USD"])
    string_json_web_data = '[' + string_json_web_data + ']'
    print(string_json_web_data)
    modified_json_web_data = json.loads(string_json_web_data.replace("\'", "\""))
    dict_json_web_data = JSONDictToDF(modified_json_web_data)
    dict_json_web_data.to_csv(fp, sep=',')
    return dict_json_web_data  # %%Path to store cached currency data

def shift(text):
	sleep(1)
	text = text[1:] + text[0]
	display_text.set(text)
	master.after(100,shift(text))

#Below block is for GUI Ticker
#display_text = variable for text
#msg = label that holds text
#master = main tkinter window
master = tk.Tk()
#master.wm_attributes('-type', 'splash','-topmost',1) uncomment for linux
master.geometry('1920x20+0+0')

master.wm_attributes('-topmost',1)
master.overrideredirect(1) #comment out if using linux

text = "hello fagget"
display_text = tk.StringVar()
msg = tk.Label(master, textvariable = display_text,height='20',width='1920')
msg.config(bg='black', font=('times', 12),fg='white')
msg.pack()
master.lift()
display_text.set(text)

while True:
    sleep(1)
    text = text[1:]+text[0]
    display_text.set(text)
    master.lift()
    master.focus()
    master.overrideredirect(1)
    master.update()





datPath = 'CurDat/'
if not os.path.exists(datPath):
    os.mkdir(datPath)
# Different cryptocurrency types

coin_type = ['ADA', 'LTC', 'ETH', 'XMR', 'XVG', 'XLM', 'ZEC', 'TRX']

# Store data frames for each of above types
D = []
for coin in coin_type:
    dfp = os.path.join(datPath, coin + '.csv')
    df = GetCurDF(coin, dfp)
    D.append(df)

print(D)


'''
    try:
        df = pd.read_csv(dfp, sep=',')
    except FileNotFoundError:
        df = GetCurDF(ci, dfp)
    D.append(df)
# %%Only keep range of data that is common to all currency types
cr = min(Di.shape[0] for Di in D)
for i in range(len(cl)):
    D[i] = D[i][(D[i].shape[0] - cr):]

'''
