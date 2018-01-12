# TESTING PUSH AND COMMIT

import json
import os
import pandas as pd
import urllib.request


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
	string_json_web_data = str(json_web_data["RAW"][cur]["USD"])
	string_json_web_data = '[' + string_json_web_data + ']'


	modified_json_web_data = json.loads(string_json_web_data.replace("\'", "\""))
	dict_json_web_data = JSONDictToDF(modified_json_web_data)
	dict_json_web_data.to_csv(fp, sep=',')
	return dict_json_web_data  # %%Path to store cached currency data


datPath = 'CurDat/'
if not os.path.exists(datPath):
	os.mkdir(datPath)
# Different cryptocurrency types
cl = ['ADA', 'LTC', 'ETH', 'XMR', 'XVG', 'XLM', 'ZEC']

# Store data frames for each of above types
D = []
for ci in cl:
	dfp = os.path.join(datPath, ci + '.csv')
	df = GetCurDF(ci, dfp)
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
