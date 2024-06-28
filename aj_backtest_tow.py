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


tehran_timezone = pytz.timezone('Asia/Tehran')
df_pross = pd.DataFrame(columns=['time', 'pros', 'sum_trade', 'balance'])
df_history = pd.DataFrame(columns=['time_open', 'time'])

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




def fix_time(df_gbp, df_eur, df_eurgbp):
    # time_gbp = df_gbp['time']
    # time_eur = df_eur['time']
    # time_eurgbp = df_eurgbp['time']
    # main_time = pd.concat([time_gbp, time_eur, time_eurgbp], ignore_index=True , axis=0).sort_values().reset_index(drop=True)

    df_main = pd.DataFrame()
    df_main['time'] = pd.concat([df_gbp['time'], df_eur['time'], df_eurgbp['time']]).sort_values().reset_index(drop=True)
    
    # ادغام دیتافریم‌ها بر اساس ستون زمان
    df_gbp_merged = pd.merge(df_main, df_gbp, on='time', how='left')
    df_eur_merged = pd.merge(df_main, df_eur, on='time', how='left')
    df_eurgbp_merged = pd.merge(df_main, df_eurgbp, on='time', how='left')
    
    # پر کردن سطرهای مفقود با مقادیر سطر قبلی
    df_gbp_merged.fillna(method='ffill', inplace=True)
    df_eur_merged.fillna(method='ffill', inplace=True)
    df_eurgbp_merged.fillna(method='ffill', inplace=True)

    # print(df_gbp_merged)
    # print(df_eur_merged)
    # print(df_eurgbp_merged)

    return df_gbp_merged, df_eur_merged, df_eurgbp_merged


def trade(df_gbp, df_eur, df_eurgbp):
    balance_one = 10000
    balance_tow = 10000
    df_gbp.fillna(method='bfill', inplace=True)
    df_eur.fillna(method='bfill', inplace=True)
    df_eurgbp.fillna(method='bfill', inplace=True)

    base_price_gbp = df_gbp.iloc[0]['bid']
    base_price_eur = df_eur.iloc[0]['ask']
    base_price_eurgbp = df_eurgbp.iloc[0]['ask']

    # برداری کردن محاسبات
    jam_gbp_buy_eur_sell = ((df_gbp['bid'] - base_price_gbp) * (0.85 * 100_000)) + \
                           ((base_price_eur - df_eur['ask']) * (1 * 100_000)) + \
                           ((df_eurgbp['bid'] - base_price_eurgbp) * (1 * 100_000))
    
    jam_gbp_sell_eur_buy = ((base_price_gbp - df_gbp['ask']) * (0.85 * 100_000)) + \
                           ((df_eur['bid'] - base_price_eur) * (1 * 100_000)) + \
                           ((base_price_eurgbp - df_eurgbp['ask']) * (1 * 100_000))

    # ایجاد دیتافریم برای ذخیره نتایج
    result_df = pd.DataFrame({
        'time_gbp': df_gbp['time'],
        'time_eur': df_eur['time'],
        'time_eurgbp': df_eurgbp['time'],
        'one': jam_gbp_buy_eur_sell,
        'tow': jam_gbp_sell_eur_buy
    })

    # ذخیره نتایج در فایل CSV
    write_to_csv('trade_data_arbit.csv', result_df.values)

def write_to_csv(filename, data):
    df = pd.DataFrame(data, columns=['time_gbp', 'time_eur', 'time_eurgbp', 'one', 'tow'])
    try:
        existing_df = pd.read_csv(filename)
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_csv(filename, index=False)





def run():
    init()
    print('run')
    df_gbp = get_tick_data('GBPUSD_o')
    df_eur = get_tick_data('EURUSD_o')
    df_eurgbp = get_tick_data('EURGBP_o')

    # همگام‌سازی دیتافریم‌ها

    df_gbp, df_eur, df_eurgbp = fix_time(df_gbp, df_eur, df_eurgbp)    
    print(df_gbp , df_eur, df_eurgbp)
    trade(df_gbp, df_eur, df_eurgbp)


    # df_gbp.to_csv('df_gbp_.csv', index=False)
    # df_eur.to_csv('df_eur_.csv', index=False)
    # df_eurgbp.to_csv('df_eurgbp.csv', index=False)

run()



