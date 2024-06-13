import MetaTrader5 as mt5
import pandas as pd
import threading as th
import time
from datetime import datetime, timedelta
from functools import lru_cache
import math
import pytz
import numpy as np

tehran_timezone = pytz.timezone('Asia/Tehran')
df_pross = pd.DataFrame(columns=['time', 'pros', 'sum_trade', 'balance'])
df_history = pd.DataFrame(columns=['time_open', 'time'])

def comission(lot, comission):
    return (lot * 100) * comission

def round_up(number, precision):
    return math.ceil(number * (10**precision)) / (10**precision)

def init():
    init = mt5.initialize(path=r"C:\Program Files\LiteFinance MT5 3\terminal64.exe")
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
    utc_from = datetime(2024, 5, 3, hour=8, tzinfo=tehran_timezone)
    utc_to = datetime(2024, 5, 6, hour=14, tzinfo=tehran_timezone)
    ticks = mt5.copy_ticks_range(symbol, utc_from, utc_to, mt5.COPY_TICKS_ALL)
    ticks_frame = pd.DataFrame(ticks)
    ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert(tehran_timezone)
    ticks_frame['time'] = ticks_frame['time'].dt.tz_localize(None)
    return ticks_frame

def synchronize_dataframes(df_list):
    # ایجاد یک سری زمانی یکتا برای همه دیتافریم‌ها
    all_times = sorted(set(df_list[0]['time']).union(*[df['time'] for df in df_list[1:]]))
    time_df = pd.DataFrame(all_times, columns=['time'])
    
    # بازنمونه‌گیری و پر کردن مقادیر قیمت برای هر دیتافریم
    synced_dfs = []
    for df in df_list:
        merged_df = pd.merge(time_df, df, on='time', how='left')
        merged_df['ask'].fillna(method='ffill', inplace=True)
        merged_df['bid'].fillna(method='ffill', inplace=True)
        synced_dfs.append(merged_df)
    
    return synced_dfs

def write_to_csv(filename, data):
    df = pd.DataFrame(data, columns=['time_gbp', 'time_eur', 'time_eurgbp', 'one', 'tow'])
    try:
        existing_df = pd.read_csv(filename)
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_csv(filename, index=False)

def trade(df_gbp, df_eur, df_eurgbp):
    balance_one = 10000
    balance_tow = 10000
    base_price_gbp, base_price_eur, base_price_eurgbp = df_gbp.iloc[0]['bid'], df_eur.iloc[0]['ask'], df_eurgbp.iloc[0]['ask']
    for (index_gbp, row_gbp), (index_eur, row_eur), (index_eurgbp, row_eurgbp) in zip(df_gbp.iterrows(), df_eur.iterrows(), df_eurgbp.iterrows()):
        jam_gbp_buy_eur_sell = ((row_gbp['bid'] - base_price_gbp) * (0.85 * 100_000)) + ((base_price_eur - row_eur['ask']) * (1 * 100_000)) + ((row_eurgbp['bid'] - base_price_eurgbp) * (1 * 100_000))
        jam_gbp_sell_eur_buy = ((base_price_gbp - row_gbp['ask']) * (0.85 * 100_000)) + ((row_eur['bid'] - base_price_eur) * (1 * 100_000)) + ((base_price_eurgbp - row_eurgbp['bid']) * (1 * 100_000))
        data = [[row_gbp['time'], row_eur['time'], row_eurgbp['time'], jam_gbp_buy_eur_sell, jam_gbp_sell_eur_buy]]
        write_to_csv('trade_data_arbit_one.csv', data)

def run():
    init()
    df_gbp = get_tick_data('GBPUSD_o')
    df_eur = get_tick_data('EURUSD_o')
    df_eurgbp = get_tick_data('EURGBP_o')

    # همگام‌سازی دیتافریم‌ها
    df_gbp, df_eur, df_eurgbp = synchronize_dataframes([df_gbp, df_eur, df_eurgbp])

    trade(df_gbp, df_eur, df_eurgbp)

run()
