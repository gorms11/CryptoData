# Pandas is the only library not in standard lib: pip install pandas
# Works on linux/windows
import json
import os
import pandas as pd
import urllib.request
import datetime
import tkinter as tk
from time import sleep
import platform
import threading
import sqlite3




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
	# print(string_json_web_data)
	modified_json_web_data = json.loads(string_json_web_data.replace("\'", "\""))
	dict_json_web_data = JSONDictToDF(modified_json_web_data)
	dict_json_web_data.to_csv(fp, sep=',')
	return dict_json_web_data
    # return dict_json_web_data  # %%Path to store cached currency data



def GetCur_NoCSV(cur):
	'''returns API data without using Panda Dataframes or making .csv files'''
	openUrl = urllib.request.urlopen(GetAPIUrl(cur))
	web_data = openUrl.read()
	openUrl.close()
	json_web_data = json.loads(web_data)
	#timestamp = str(datetime.datetime.fromtimestamp(json_web_data["RAW"][cur]["USD"]['LASTUPDATE']))
	#json_web_data["RAW"][cur]["USD"]['LASTUPDATE'] = timestamp
	return json_web_data


def DataGrabber():
	'''Grabs and returns all coin data from API AND makes .CSV files'''
	list_of_coin_data = []
	for coin in coin_type:
		dfp = os.path.join(datPath, coin + '.csv')
		text = GetCurDF(coin, dfp)
		list_of_coin_data.append(text)
	return(list_of_coin_data)


def DataGrabber_NoCSV():
	'''Grabs all coin data from API WITHOUT making .CSV files. Runs every 18 seconds
	   Updates the string displayed in the user interface
	   Stores current and previous values of all coins in 2D array for easy comparison'''
	threading.Timer(18.0, DataGrabber_NoCSV).start()
	global CoinList
	global coin_data_copy
	list_of_coin_data = []
	for coin in coin_type:
		text = GetCur_NoCSV(coin)
		list_of_coin_data.append(text)
	print('API Call Executed!')
	CoinList = list_of_coin_data
	#return (list_of_coin_data)

	coin_fiat_data = []
	for x in range(len(list_of_coin_data)):
		text = list_of_coin_data[x]
		text = str(text['RAW'][coin_type[x]]['USD']['PRICE'])
		compare_list[x][1] = compare_list[x][0]
		compare_list[x][0] = float(text)
		text = coin_type[x] + ' :' + ' $' + text + '    '
		coin_fiat_data.append(text)
	coin_data_copy = coin_fiat_data
	print(compare_list)


def WriteToDB():
	'''records data for each coin in its own table for local SQL database'''
	threading.Timer(150.0, WriteToDB).start()
	print('writing to database!')
	db = sqlite3.connect('CoinData.db')
	c = db.cursor()

	for x in range(len(CoinList)):
		dbList= CoinList[x]
		timestamp = str(datetime.datetime.fromtimestamp(dbList["RAW"][coin_type[x]]["USD"]['LASTUPDATE']))
		dbList["RAW"][coin_type[x]]["USD"]["LASTUPDATE"] = timestamp

		c.execute('''CREATE TABLE IF NOT EXISTS {tn}(`PRICE`          INTEGER,
													`LASTVOLUME`      INTEGER,
													`LASTVOLUMETO`	  INTEGER,
													`VOLUMEDAY`	      INTEGER,
													`VOLUMEDAYTO`	  INTEGER,
													`VOLUME24HOUR`	  INTEGER,
													`VOLUME24HOURTO`  INTEGER,
													`HIGH24HOUR`	  INTEGER,
													`LOW24HOUR`	      INTEGER,
													`MKTCAP`	      INTEGER,
													`SUPPLY`	      INTEGER,
													`TOTALVOLUME24H`  INTEGER,
													`TOTALVOLUME24HTO`INTEGER,
													`LASTUPDATE`	  INTEGER)'''.format(tn=coin_type[x]))

		c.execute('''INSERT INTO {tn}(PRICE, LASTVOLUME, LASTVOLUMETO, VOLUMEDAY, VOLUMEDAYTO, VOLUME24HOUR, VOLUME24HOURTO,
		                             HIGH24HOUR, LOW24HOUR, MKTCAP, SUPPLY, TOTALVOLUME24H, TOTALVOLUME24HTO, LASTUPDATE)
		             VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(tn=coin_type[x]),
				  (str(dbList["RAW"][coin_type[x]]["USD"]["PRICE"]),
				   str(dbList["RAW"][coin_type[x]]["USD"]["LASTVOLUME"]),
				   str(dbList["RAW"][coin_type[x]]["USD"]["LASTVOLUMETO"]),
				   str(dbList["RAW"][coin_type[x]]["USD"]["VOLUMEDAY"]),
				   str(dbList["RAW"][coin_type[x]]["USD"]["VOLUMEDAYTO"]),
				   str(dbList["RAW"][coin_type[x]]["USD"]["VOLUME24HOUR"]),
				   str(dbList["RAW"][coin_type[x]]["USD"]["VOLUME24HOURTO"]),
				   str(dbList["RAW"][coin_type[x]]["USD"]["HIGH24HOUR"]),
				   str(dbList["RAW"][coin_type[x]]["USD"]["LOW24HOUR"]),
				   str(dbList["RAW"][coin_type[x]]["USD"]["MKTCAP"]),
				   str(dbList["RAW"][coin_type[x]]["USD"]["SUPPLY"]),
				   str(dbList["RAW"][coin_type[x]]["USD"]["TOTALVOLUME24H"]),
				   str(dbList["RAW"][coin_type[x]]["USD"]["TOTALVOLUME24HTO"]),
				   str(dbList["RAW"][coin_type[x]]["USD"]["LASTUPDATE"])))
		db.commit()
		print('wrote to ', [coin_type[x]] , ' database!')

	db.close()
	print('done writing to database!')



# Below block is for GUI Ticker
# display_text = variable for text
# msg = label that holds text
# master = main tkinter window

master = tk.Tk()
master.geometry('1920x20+0+0')

# if linux
if platform.system() is 'Linux':
	master.wm_attributes('-type', 'splash', '-topmost', 1)

# if windows
if platform.system() is 'Windows':
	master.wm_attributes('-topmost', 1)
	master.overrideredirect(1)

display_text = tk.StringVar()
msg = tk.Label(master, textvariable=display_text, height='20', width='1920', anchor='w')
msg.config(bg='black', font=('times', 12), fg='white')
msg.pack()
master.lift()


coin_type = ['LTC', 'ETH', 'XMR', 'XVG', 'XLM', 'ZEC', 'XRP', 'REQ', 'BCH', 'LINK', 'NXT', 'BTC']
datPath = 'CurDat/'
if not os.path.exists(datPath):
	os.mkdir(datPath)


#provides something to display when program first starts
display_text.set('grabbing data...please wait')
master.lift()
master.focus()
master.update()

#2D array for comparing current value to previous value for each coin
compare_list = [[None for x in range(2)] for y in range(len(coin_type))]

CoinList = []
coin_data_copy = []

#Initializes Datagrabber_NoCSV and WriteToDB threads
DataGrabber_NoCSV()
WriteToDB()


while True:
	#print('display updated')
	display_text.set(' '.join(coin_data_copy))
	# text = text[1:]+text[0]
	master.lift()
	master.focus()
	master.update()
	sleep(1.0)
	#CoinList = DataGrabber_NoCSV()

