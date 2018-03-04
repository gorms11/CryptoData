# Pandas is the only library not in standard lib: pip install pandas
# Works on linux/windows
import json
import os
# import pandas as pd
import urllib.request
import datetime
import tkinter as tk
from time import sleep
import platform
import threading
import sqlite3
from tkinter import *
import time
import sys
from threading import Lock

'''
def JSONDictToDF(d):

	#Converts a dictionary created from json.loads to a pandas dataframe
#	d:      The dictionary

	length = len(d)
	cols = []
	if length > 0:  # Place the column in sorted order
		cols = sorted(list(d[0].keys()))
	df = pd.DataFrame(columns=cols, index=range(length))
	for i in range(length):
		for coli in cols:
			df.set_value(i, coli, d[i][coli])
	return df

'''


def GetAPIUrl(cur):
    openUrl = urllib.request.urlopen(
        'https://min-api.cryptocompare.com/data/pricemultifull?fsyms=' + cur + '&tsyms=USD')
    web_data = openUrl.read()
    openUrl.close()
    json_web_data = json.loads(web_data)
    return json_web_data


'''
def GetCurDF(cur, fp):

   # cur:    3 letter abbreviation for cryptocurrency (BTC, LTC, etc)
    #fp:     File path (to save price data to CSV)

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
    '''


def compare_and_set_display(json_web_data, x, dbwrite1, cur):
    ''' Compares previous fiat values to current values and sets its associated tkinter textvariable'''

    print("starting thread: ", x)
    text = str(json_web_data['RAW'][cur]['USD']['PRICE'])

    compare_list[x][1] = compare_list[x][0]
    compare_list[x][0] = float(text)



    if compare_list[x][0] > compare_list[x][1]:
        mutex.acquire()
        display_number_green[x].set(" ")
        display_number_red[x].set(" ")
        display_number_white[x].set("   ")
        display_number_green[x].set("  " + cur + ' :' + ' $' + text)

    elif compare_list[x][0] < compare_list[x][1]:
        mutex.acquire()
        display_number_green[x].set("  ")
        display_number_red[x].set(" ")
        display_number_white[x].set("   ")
        display_number_red[x].set(" " + cur + ' :' + ' $' + text)

    else:
        mutex.acquire()
        display_number_green[x].set("  ")
        display_number_red[x].set(" ")
        display_number_white[x].set(" ")
        display_number_white[x].set("   " + cur + ' :' + ' $' + text)

    mutex.release()

    if dbwrite1 is True:
        WriteToDB(json_web_data, cur)


'''
def DataGrabber():
    #Grabs and returns all coin data from API AND makes .CSV files
    list_of_coin_data = []
    for coin in coin_type:
        dfp = os.path.join(datPath, coin + '.csv')
        text = GetCurDF(coin, dfp)
        list_of_coin_data.append(text)
    return (list_of_coin_data)
'''


def WriteToDB(dbList, cur):
    '''records data for each coin in its own table for local SQL database'''

    db = sqlite3.connect('CoinData.db')
    c = db.cursor()

    timestamp = str(datetime.datetime.fromtimestamp(dbList["RAW"][cur]["USD"]['LASTUPDATE']))
    dbList["RAW"][cur]["USD"]["LASTUPDATE"] = timestamp

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
			    													`LASTUPDATE`	  INTEGER)'''.format(
        tn=cur))

    c.execute('''INSERT INTO {tn}(PRICE, LASTVOLUME, LASTVOLUMETO, VOLUMEDAY, VOLUMEDAYTO, VOLUME24HOUR, VOLUME24HOURTO,
			    		                             HIGH24HOUR, LOW24HOUR, MKTCAP, SUPPLY, TOTALVOLUME24H, TOTALVOLUME24HTO, LASTUPDATE)
			    		             VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(tn=cur),
              (str(dbList["RAW"][cur]["USD"]["PRICE"]),
               str(dbList["RAW"][cur]["USD"]["LASTVOLUME"]),
               str(dbList["RAW"][cur]["USD"]["LASTVOLUMETO"]),
               str(dbList["RAW"][cur]["USD"]["VOLUMEDAY"]),
               str(dbList["RAW"][cur]["USD"]["VOLUMEDAYTO"]),
               str(dbList["RAW"][cur]["USD"]["VOLUME24HOUR"]),
               str(dbList["RAW"][cur]["USD"]["VOLUME24HOURTO"]),
               str(dbList["RAW"][cur]["USD"]["HIGH24HOUR"]),
               str(dbList["RAW"][cur]["USD"]["LOW24HOUR"]),
               str(dbList["RAW"][cur]["USD"]["MKTCAP"]),
               str(dbList["RAW"][cur]["USD"]["SUPPLY"]),
               str(dbList["RAW"][cur]["USD"]["TOTALVOLUME24H"]),
               str(dbList["RAW"][cur]["USD"]["TOTALVOLUME24HTO"]),
               str(dbList["RAW"][cur]["USD"]["LASTUPDATE"])))
    db.commit()
    print('wrote to ', cur, ' database!')

    db.close()


def quit():
    '''ends while loop and exits program'''
    global bool_end
    bool_end = False
    sys.exit(0)


def reduced_API_latency_loop(start_time):
    global bool_end
    display_number_white[0].set("  grabbing data...please wait")
    while bool_end:
        dbwrite = False
        list_of_coin_data = []

        for coin in coin_type:
            text = GetAPIUrl(coin)
            list_of_coin_data.append(text)
            sleep(.2)

        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time >= 120:
            dbwrite = True
            start_time = current_time

        number_coins = len(list_of_coin_data)
     #   print('starting threads!')
        for x in range(number_coins):
            coin_data = list_of_coin_data[x]
            thread_api = threading.Thread(target=compare_and_set_display, args=(coin_data, x, dbwrite, coin_type[x]))
            thread_api.start()

        for i in range(20):  # delay put in a forloop so program and exit faster
            if bool_end is False:
                break
            sleep(1)



mutex = Lock()
bool_end = True   #ends while loops if false
root = Tk()
height = root.winfo_screenheight()
update_display = True



# if linux
if platform.system() == 'Linux':
    root.wm_attributes('-type', 'splash', '-topmost', 1)
    if height == 1440:
        root.geometry('2560x25+0+1420')
        padding = 38
    elif height == 1080:
        root.geometry('1920x25+0+1060')
        padding = 7

    else:
        padding = 4

# if windows
if platform.system() == 'Windows':
    root.wm_attributes('-topmost', 1)
    root.overrideredirect(1)
    root.geometry('1920x25+0+800')
    padding = 7

'''
cwd = os.getcwd()  # Get the current working directory (cwd)
files = os.listdir(cwd)  # Get all the files in that directory
print("Files in '%s': %s" % (cwd, files))
'''

with open('coins.config', "r") as ins:
    coin_type = []
    for line in ins:
        coin_type.append(line[0:((len(line)) - 1)])

# 2D array for comparing current value to previous value for each coin
compare_list = [[float(0.0) for x in range(2)] for y in range(len(coin_type))]


datPath = 'CurDat/'
if not os.path.exists(datPath):
    os.mkdir(datPath)


display_number_white = []
display_number_green = []
display_number_red = []

# three seperate colors for GUI
for i in range(len(coin_type)):
    display_number_white.append(i)
    display_number_white[i] = StringVar()
    Label(root, textvariable=display_number_white[i], bg='black', font=('times', 12), fg='white').grid(row=0, column=i,
                                                                                                       sticky=tk.W,
                                                                                                       padx=padding)  # default padx = 4

for i in range(len(coin_type)):
    display_number_green.append(i)
    display_number_green[i] = StringVar()
    Label(root, textvariable=display_number_green[i], bg='black', font=('times', 12), fg='green').grid(row=0, column=i,
                                                                                                       sticky=tk.W,
                                                                                                       padx=padding)  # default padx = 4

for i in range(len(coin_type)):
    display_number_red.append(i)
    display_number_red[i] = StringVar()
    Label(root, textvariable=display_number_red[i], bg='black', font=('times', 12), fg='red').grid(row=0, column=i,
                                                                                                   sticky=tk.W,
                                                                                                   padx=padding)  # default padx = 4

exit_button_column = (len(coin_type) + 2)
Button(root, text='x', bg='black', font=('times', 12), bd=0, fg='black', activeforeground='black', anchor=tk.E,
       highlightbackground='black', command=lambda: quit()).grid(row=0, column=exit_button_column, padx=28)

root.config(bg='black')



start = time.time()
thread = threading.Thread(target=reduced_API_latency_loop, args=(start,))
thread.start()


root.mainloop()


'''
while bool_end:
	if update_display is True:  #This allows all coins to be updated at once while keeping the exit button working
		#root.update_idletasks()    #might be useful for future update
		root.update()
		sleep(.3)
	else:
	sleep(.1)
'''