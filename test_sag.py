import MetaTrader5 as mt5
import pandas as pd
import threading as th
import time
from datetime import datetime, timedelta
from functools import lru_cache
import math
import pytz
import numpy as np

print('Start...')

hist = pd.DataFrame(columns=['time', 'profit', 'balance'])


tehran_timezone = pytz.timezone('Asia/Tehran')

def comission(lot, comission):
    return (lot * 100) * comission

def round_up(number, precision):
    return math.ceil(number * (10**precision)) / (10**precision)

def init():
    init = mt5.initialize(path=r"C:\Program Files\LiteFinance MT5 2\terminal64.exe")
    mt5.login(89373537, password='Mahdi1400@', server='LiteFinance-MT5-Demo')
    return init

def info():
    account_info = mt5.account_info()
    balance = account_info.balance
    equity = account_info.equity
    profit = account_info.profit
    return balance, equity, profit

def symbol_info(symbol):
    dic_symbol_info = {}
    group_symbols = mt5.symbols_get(group='*USD*')
    for s in group_symbols:
        if s.name == symbol:
            dic_symbol_info[s.name] = s.ask, s.bid
    return dic_symbol_info

def get_tick_data(symbol):
    utc_from = datetime(2024, 6, 24, hour=9, tzinfo=tehran_timezone)
    utc_to = datetime(2024, 6, 25, hour=21, tzinfo=tehran_timezone)
    ticks = mt5.copy_ticks_range(symbol, utc_from, utc_to, mt5.COPY_TICKS_ALL)
    ticks_frame = pd.DataFrame(ticks)
    ticks_frame['time'] = pd.to_datetime(ticks_frame['time_msc'] , unit= 'ms' ).dt.tz_localize('UTC').dt.tz_convert(tehran_timezone)
    ticks_frame['time'] = ticks_frame['time'].dt.tz_localize(None)


    return ticks_frame



def get_candel(symbol):


    utc_from = datetime(2024, 6, 24, tzinfo=tehran_timezone)
    utc_to = datetime(2024, 6, 25, tzinfo=tehran_timezone)
    ticks = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5 , utc_from, utc_to)
    ticks_frame = pd.DataFrame(ticks)
    ticks_frame['time'] = pd.to_datetime(ticks_frame['time'] , unit= 'ms' ).dt.tz_localize('UTC').dt.tz_convert(tehran_timezone)
    ticks_frame['time'] = ticks_frame['time'].dt.tz_localize(None)


    return ticks_frame



init()



def simolate(df):

    #['time', 'opneprice' , 'close_price' , 'sl'  ,  'profit', 'balance']

    cand = None
    balance = 1000
    profit = 0
    lot = 0.1
    init = True
    opne_price = None
    close_price = None
    sl = None

    for row , index in df.iterrows():

        if init:

            color = row['opne'] - row['close']
            if color > 0:
                cand = 'red'
                sl = row['open']
            else:
                cand = 'green'
                sl = row['open']
            init = False
            continue

        else :

            if cand == 'red':
                price_open = row['open']
                
                
                




            
                
        

    







