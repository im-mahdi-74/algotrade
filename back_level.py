import MetaTrader5 as mt5
import pandas as pd 
import threading as th
import time
from datetime import datetime, timedelta
import math
import pytz
import numpy as np

tehran_timezone = pytz.timezone('Asia/Tehran')
df_pross = pd.DataFrame(columns=['time', 'pros', 'sum_trade', 'balance'])
df_history = pd.DataFrame(columns=['time_open', 'time'])

class main:
    def __init__(self):
        pass

    def comission(self, lot, comission):
        return (lot * 100) * comission

    def round_up(self, number, precision):
        return math.ceil(number * (10**precision)) / (10**precision)

    def init_(self):
        mt5.initialize(path=r"C:\Program Files\LiteFinance MT5 3\terminal64.exe")
        mt5.login(89373537, password='Mahdi1400@', server='LiteFinance-MT5-Demo')

    def info(self):
        account_info = mt5.account_info()
        balance = account_info.balance
        equity = account_info.equity
        profit = account_info.profit
        return balance, equity, profit

    def symbol_info(self, symbol):
        dic_symbol_info = {}
        group_symbols = mt5.symbols_get(group='*USD*')
        for s in group_symbols:
            if s.name == symbol:
                dic_symbol_info[s.name] = s.ask, s.bid
        return dic_symbol_info

    def get_tick_data(self, symbol):
        utc_from = datetime(2024, 6, 1, hour=3, tzinfo=tehran_timezone)
        utc_to = datetime(2024, 6, 13, hour=23, tzinfo=tehran_timezone)
        ticks = mt5.copy_ticks_range(symbol, utc_from, utc_to, mt5.COPY_TICKS_ALL)
        ticks_frame = pd.DataFrame(ticks)
        ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert(tehran_timezone)
        ticks_frame['time'] = ticks_frame['time'].dt.tz_localize(None)
        return ticks_frame

    def get_data(self, symbol, timeframe):
        utc_from = datetime(2024, 6, 12, hour=3, tzinfo=tehran_timezone)
        utc_to = datetime(2024, 6, 13, hour=23, tzinfo=tehran_timezone)
        rates = mt5.copy_rates_range(symbol, timeframe, utc_from, utc_to)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert(tehran_timezone)
        df['time'] = df['time'].dt.tz_localize(None)
        return df

    def noise(self, df):
        had = 0.00025
        noise = 0




        if df.empty:
            return noise, 0

        movement = 0
        min_price = df['bid'].iloc[0]
        max_price = df['bid'].iloc[0]
        start_price = df['bid'].iloc[0]
        for index, row in df.iterrows():
            if abs(row['bid'] - start_price) > had:
                noise += 1
                start_price = row['bid']
            if row['bid'] > max_price:
                max_price = row['bid']
            if row['bid'] < min_price:
                min_price = row['bid']
        movement = max_price - min_price

        return noise, movement

back = main()
back.init_()
df = back.get_tick_data('GBPUSD_o')
print(back.noise(df))
