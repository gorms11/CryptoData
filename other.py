# Pandas is the only library not in standard lib: pip install pandas
# Works on linux/windows
import json
import os
import urllib.request
from urllib.error import  URLError
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

global_label = [] 
number_of_coins =  None

def GetAPIUrl(cur):
    openUrl = urllib.request.urlopen(
        'https://min-api.cryptocompare.com/data/pricemultifull?fsyms=' + cur + '&tsyms=USD')
    web_data = openUrl.read()
    openUrl.close()
    json_web_data = json.loads(web_data)
    return json_web_data

def compare_and_set_display(json_web_data, x, dbwrite1, cur):
    global global_label
    global red_color_counter
    global green_color_counter
    ''' Compares previous fiat values to current values and sets its associated tkinter textvariable'''

    print("starting thread: ", x)


    try: #potential exceptions if an invalid dictionary is passed into this method
        text = str(json_web_data['RAW'][cur]['USD']['PRICE'])
    except KeyError or Exception:
        print("bad data, check internet connection")
        return
   

    mutex.acquire()
    compare_list[x][1] = compare_list[x][0]
    compare_list[x][0] = float(text)

    # Change to two decimal places
    text = "%.2f" % float(text)

    if compare_list[x][0] > compare_list[x][1]:
        display_number_white[x].set('   ')
        display_number_white[x].set('    ' + cur + ' : $' + text)
        if green_color_counter[x] == 0:
            red_color_counter[x] = 0
            global_label[x].config(fg="green4")
        elif green_color_counter[x] == 1:
            global_label[x].config(fg="green3")
        elif green_color_counter[x] == 2:
            global_label[x].config(fg="green2")
        else:
            global_label[x].config(fg="green1")
        green_color_counter[x] += 1
    elif compare_list[x][0] < compare_list[x][1]:
        display_number_white[x].set('   ')
        display_number_white[x].set('    ' + cur + ' : $' + text)
        if red_color_counter[x] == 0:
            green_color_counter[x] = 0 
            global_label[x].config(fg="red4")
        elif red_color_counter[x] == 1:
            global_label[x].config(fg="red3")
        elif red_color_counter[x] == 2:
            global_label[x].config(fg="red2")
        else:
            global_label[x].config(fg="red")
        red_color_counter[x] += 1
    else:
        display_number_white[x].set('   ')
        display_number_white[x].set('    ' + cur + ' : $' + text)
        global_label[x].config(fg="white")
        red_color_counter[x] = 0
        green_color_counter[x] = 0




    if dbwrite1 is True:
        thread_database = threading.Thread(target=WriteToDB, args=(json_web_data, cur))
        thread_database.start()
       # WriteToDB(json_web_data, cur)

    mutex.release()

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
    global root
    global windows_end
    bool_end = False
    os._exit(0)

def reduced_API_latency_loop(start_time):
    global bool_end
    global bool_loading
    global windows_end

    while bool_end:
        dbwrite = False
        list_of_coin_data = []

        try:
            for coin in coin_type:
                print("grabbing ", coin)
                openUrl = urllib.request.urlopen(
                    'https://min-api.cryptocompare.com/data/pricemultifull?fsyms=' + coin + '&tsyms=USD')
                web_data = openUrl.read()
                openUrl.close()
                text = json.loads(web_data)
                list_of_coin_data.append(text)
                if bool_end is False:
                    sys.exit(0)
                sleep(.2)  # delay to not overload the API with requests

        except URLError as e: #error handling for network connectivity issues

            if hasattr(e, 'reason'):
                print('failed to reach API, check internet connection.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('The API couldn\'t fulfill the request.')
                print('Error code: ', e.code)

        mutex2.acquire()
        bool_loading = False #end loading display message when data is ready to be displayed
        mutex2.release()
        sleep(.1) # give "grabbing data" loop time to end


        current_time = time.time()
        elapsed_time = current_time - start_time #computes time since last database write
        if elapsed_time >= 120:
            dbwrite = True
            start_time = current_time

        number_coins = len(list_of_coin_data)
     #   print('starting threads!')
        for x in range(number_coins):
            coin_data = list_of_coin_data[x]
            thread_api = threading.Thread(target=compare_and_set_display, args=(coin_data, x, dbwrite, coin_type[x]))
            thread_api.start()
        sleep(.15)
        windows_end = True
        for i in range(17):  # delay put in a forloop so program and exit faster
            if bool_end is False:
                sys.exit(0)
            sleep(1)
        windows_end = False

def add_frame(bool_frame, anchor, layer):
    global toggle_frame
    global root
    global toggle_layer

    set_anchor = str(root.wm_geometry())
   # print(set_anchor)
    root.destroy()
    root.quit()
    root = Tk()
    root.resizable(width=True, height=False)


    if layer == 1:
        toggle_layer = not toggle_layer #toggles forcing top of display on and off

        toggle_frame = not bool_frame #if this is not inverted, then a window will switch to an anchor
                                      #and an anchor will switch to a window. We don't want that.


    if toggle_layer is True:
        layer = 1 #if 1, display is forced to top of screen
    else:
        layer = 0 #if 0, other window layers (such as a web browser) can stack on top of GUI

    # if linux
    if anchor == 2:  #anchor bottom
        if platform.system() == 'Linux':
            root.wm_attributes('-type', 'splash', '-topmost', layer)
            if height == 1440:
                root.geometry('2560x25+0+1420')
            else:
                root.geometry('1920x25+0+1060') #only 2 resolution options for now

        if platform.system() == 'Windows':
            root.wm_attributes('-topmost', layer)
            root.overrideredirect(1)
            root.geometry('1920x25+0+1015') # Was 1020




    if toggle_frame is False:
        if anchor == 1:     #anchor current position with no window frame
            root.geometry(set_anchor)
            if platform.system() == 'Linux':
                root.wm_attributes('-type', 'splash', '-topmost', layer)
            else:
                root.wm_attributes('-topmost', layer)
                root.overrideredirect(1)

    else:   #set window ~middle of screen at start (with window frame)
        if anchor == 0:
            root.wm_attributes('-topmost', layer)

            #overly complicated way for computing central position
            w = root.winfo_screenwidth()
            h = root.winfo_screenheight()
            size = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))
            x = str((w / 2 - size[0] / 2) - 640)
            if x.__contains__('.'):
                x = x[:x.index(".")]
            y = str(h / 2 - size[1] / 2)
            if y.__contains__('.'):
                y = y[:y.index(".")]

            root.geometry('1280x25+'+ x +'+' + y)

        else: # switch from anchored to window frame at the current position
            if anchor == 1:
                root.wm_attributes('-topmost', layer)
                root.geometry(set_anchor)

    padding = 3
    toggle_frame = not toggle_frame



#here we make all the necessary columns for all 3 colors
    global global_label
    global_label = []
    for i in range(len(coin_type)):
        root.grid_columnconfigure(i, weight=1) #assign weight to every column so GUI spacing scales
        display_number_white.append(i)
        display_number_white[i] = StringVar()
        global_label.append(Label(root, textvariable=display_number_white[i], bg='black', font=('arial', 12), fg='white'))
        global_label[i].grid(row=0,column=i)

    #button to open up options menue. For some reason it works differently on windows compared to linux....
    if platform.system() == 'Windows':

        exit_button_column = (len(coin_type) + 1)
        Button(root, text='^  ', bg='black', font=('arial', 12), bd=0, fg='white', activeforeground='black', anchor=tk.E,
               highlightbackground='red', command=lambda: ticker_options()).grid(row=0, column=exit_button_column,
                                                                                 padx=0)

    if platform.system() == 'Linux':
        root.grid_columnconfigure(len(coin_type) + 1, weight=1)  # assign weight to every column so GUI spacing scales
        root.grid_rowfigure(len(coin_type) + 1, weight=1)  # assign weight to every column so GUI spacing scales
        exit_button_column = (len(coin_type) + 1)
        Button(root, text='^', bg='black', font=('arial', 12), bd=0, fg='black', activeforeground='black', anchor=tk.E,
               highlightbackground='black', command=lambda: ticker_options()).grid(row=0, column=exit_button_column,
                                                                                   padx=0)

    root.config(bg='black')

    #starts the loading screen while json data is fetched
    thread_loading_message = threading.Thread(target=loading_message)
    thread_loading_message.start()

    root.mainloop()



def loading_message():
    #displays a loading message while json data is being fetched
    global bool_loading
    global bool_end
    load_val = " grabbing_data...please wait"

    #memory safety because we're writing a global values that another loop also writes to
    mutex2.acquire()
    bool_loading = True
    mutex2.release()
    #different mutex here

    mutex.acquire()
    while bool_loading is True and bool_end is True:
        display_number_white[0].set(load_val)
       # root.update()
        sleep(.05)
        load_val = (" " + load_val)
    display_number_white[0].set("")
    mutex.release()


def ticker_options():
    #buttons in the options window

    root2 = Tk()
    root2.grid_rowconfigure(0, weight=1)
    root2.grid_rowconfigure(1, weight=1)
    root2.grid_columnconfigure(0, weight=1)

    Button(root2, text="                 quit                   ", bg='white', font=("Helvetica", 12, "bold"), bd=0, fg='black', activeforeground='black',
           highlightbackground='black', command=lambda: root.protocol('WM_DELETE_WINDOW', quit())).grid(row=0, column=0, padx=0)

    Button(root2, text='toggle window/anchor', bg='white', font=("Helvetica", 12, "bold"), bd=0, fg='black', activeforeground='black',
           highlightbackground='black', command=lambda: add_frame(toggle_frame, 1, 0)).grid(row=1, column=0, padx=0)

    Button(root2, text="      togge force top       ", bg='white', font=("Helvetica", 12, "bold"), bd=0, fg='black', activeforeground='black',
           highlightbackground='black', command=lambda: add_frame(toggle_frame, 1, 1)).grid(row=2, column=0, padx=0)

    Button(root2, text="       anchor bottom        ", bg='white', font=("Helvetica", 12, "bold"), bd=0, fg='black', activeforeground='black',
           highlightbackground='black', command=lambda: add_frame(toggle_frame, 2, 0)).grid(row=3, column=0, padx=0)

    root.resizable(width=False, height=False)
    root2.mainloop()


mutex = Lock()
mutex2 = Lock()
bool_end = True   #ends while loops if false, sorry for reverse logic
root = Tk()
height = root.winfo_screenheight()
#update_display = True
toggle_frame = True
bool_loading = True
toggle_layer = True
windows_end = False


#reads coins from coins.config file
with open('coins.config', "r") as ins:
    coin_type = []
    for line in ins:
        coin_type.append(line[0:((len(line)) - 1)])


red_color_counter = [0]*len(coin_type)
green_color_counter = [0]*len(coin_type)

# 2D array for comparing current value to previous value for each coin
compare_list = [[float(0.0) for x in range(2)] for y in range(len(coin_type))]

#makes a directory path for something that will be implemented later
datPath = 'CurDat/'
if not os.path.exists(datPath):
    os.mkdir(datPath)

#arrays used as tkinter TextVariables
display_number_white = []
display_number_green = []
display_number_red = []

#starts the loop that grabs json data from api and keeps track of elapsed time
start = time.time()
thread = threading.Thread(target=reduced_API_latency_loop, args=(start,))
thread.start()

#starts the GUI method
add_frame(toggle_frame, 0, 0)
