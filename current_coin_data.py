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
from tkinter import*



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

	#threading.Timer(18.0, DataGrabber_NoCSV).start()
	global CoinList
	global coin_data_copy
	global color
	while True:
		list_of_coin_data = []
		for coin in coin_type:
			text = GetCur_NoCSV(coin)
			list_of_coin_data.append(text)
		print('API Call Executed!')
		CoinList = list_of_coin_data
		# return (list_of_coin_data)

		for x in range(len(list_of_coin_data)):
			text = list_of_coin_data[x]
			text = str(text['RAW'][coin_type[x]]['USD']['PRICE'])
			compare_list[x][1] = compare_list[x][0]
			compare_list[x][0] = float(text)
		#	text2 = ' ' + coin_type[x] + ' :' + ' $' + text + '    '

			if compare_list[x][0] > compare_list[x][1]:
				display_number_green[x].set(" ")
				display_number_red[x].set(" ")
				display_number_white[x].set(" ")
				display_number_green[x].set("  " + coin_type[x] + ' :' + ' $' + text)

			if compare_list[x][0] < compare_list[x][1]:
				display_number_green[x].set(" ")
				display_number_red[x].set(" ")
				display_number_white[x].set(" ")
				display_number_red[x].set("  "  + coin_type[x] + ' :' + ' $' + text)

			if compare_list[x][0] == compare_list[x][1]:
				display_number_green[x].set(" ")
				display_number_red[x].set(" ")
				display_number_white[x].set(" ")
				display_number_white[x].set("  " + coin_type[x] + ' :' + ' $' + text)


		print(compare_list)

		sleep(10)






def WriteToDB():
	'''records data for each coin in its own table for local SQL database'''
	threading.Timer(150.0, WriteToDB).start()

	print('writing to database!')
	db = sqlite3.connect('CoinData.db')
	c = db.cursor()

	for x in range(len(CoinList)):
		dbList = CoinList[x]
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
		print('wrote to ', [coin_type[x]], ' database!')

	db.close()
	print('done writing to database!')





	# sleep(1.0)
	# CoinList = DataGrabber_NoCSV()



# Below block is for GUI Ticker
# display_text = variable for text
# msg = label that holds text
# master = main tkinter window




#root.geometry('1920x20+0+0')
'''
# if linux
if platform.system() is 'Linux':
	root.wm_attributes('-type', 'splash', '-topmost', 1)

# if windows
if platform.system() is 'Windows':
	root.wm_attributes('-topmost', 1)
	root.overrideredirect(1)



'''

root=Tk()





coin_type = ['LTC', 'ETH', 'XMR', 'XVG', 'XLM', 'ZEC', 'XRP', 'REQ', 'BCH', 'LINK', 'NXT', 'BTC']
datPath = 'CurDat/'
if not os.path.exists(datPath):
	os.mkdir(datPath)


#root.wm_attributes('-type', 'splash', '-topmost', 1)



display_number_white = []
display_number_green = []
display_number_red = []


for i in range (len(coin_type)):
	display_number_white.append(i)
	display_number_white[i] = StringVar()
	Label(root, textvariable=display_number_white[i], bg='black', font=('times', 12), fg ='white').grid(row=0, column=i, sticky=tk.W, padx=4)



for i in range (len(coin_type)):
	display_number_green.append(i)
	display_number_green[i] = StringVar()
	Label(root, textvariable=display_number_green[i], bg='black', font=('times', 12), fg ='green').grid(row=0, column=i, sticky=tk.W, padx=4)


for i in range (len(coin_type)):
	display_number_red.append(i)
	display_number_red[i] = StringVar()
	Label(root, textvariable=display_number_red[i], bg='black', font=('times', 12), fg ='red').grid(row=0, column=i, sticky=tk.W, padx=4)


root.config(bg='black')






#2D array for comparing current value to previous value for each coin
compare_list = [[float(0.0) for x in range(2)] for y in range(len(coin_type))]

CoinList = []
coin_data_copy = []

#wait to grab initial data
#if coin_data_copy == []:
	#display_number_white[0].set("Grabbing Data...Please Wait")




thread = threading.Thread(target=DataGrabber_NoCSV)
thread.start()




while CoinList == []:
	display_number_white[0].set("grabbing data...please wait")
	root.lift()
	root.focus()
	root.update()
	sleep(0.05)


WriteToDB()

display_number_white[0].set(" ")
root.lift()
root.focus()
root.update()





root.mainloop()



