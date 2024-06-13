import MetaTrader5 as mt5
import pandas as pd
import threading as th
import time
import datetime
import math
import pytz
import logging

tehran_timezone = pytz.timezone('Asia/Tehran')
df_pross = pd.DataFrame(columns=['time', 'pros', 'sum_trade', 'balance'])

logging.basicConfig(level=logging.INFO)

def round_up(number, precision):
    return math.ceil(number * (10**precision)) / (10**precision)

def init():
    if not mt5.initialize(path=r"C:\Program Files\LiteFinance MT5 3\terminal64.exe"):
        logging.error("Initialize() failed, error code =", mt5.last_error())
        quit()
    if not mt5.login(89373537, password='Mahdi1400@', server='LiteFinance-MT5-Demo'):
        logging.error("Login() failed, error code =", mt5.last_error())
        quit()

def info():
    account_info = mt5.account_info()
    return account_info.balance, account_info.equity, account_info.profit

def symbol_info(symbol):
    dic_symbol_info = {}
    group_symbols = mt5.symbols_get(group='*USD*')
    for s in group_symbols:
        if s.name == symbol:
            dic_symbol_info[s.name] = s.ask, s.bid
    return dic_symbol_info

def std(symbol, period):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, period * 2)
    rates_frame = pd.DataFrame(rates)
    rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame['valu'] = rates_frame['high'] - rates_frame['low']
    rates_frame['std'] = rates_frame['valu'].rolling(window=period).std()
    rates_frame['mean'] = rates_frame['valu'].rolling(window=period).mean()
    rates_frame['mean_price'] = (rates_frame['high'] + rates_frame['low']) / 2
    rates_frame['std_'] = (rates_frame['valu'].rolling(window=period).std() * 100) / rates_frame['mean_price'].rolling(window=period).mean()
    rates_frame['std_high'] = rates_frame['high'].rolling(window=period).std()
    rates_frame['std_low'] = rates_frame['low'].rolling(window=period).std()
    rates_frame['std_high_'] = (rates_frame['high'].rolling(window=period).std() * 100) / rates_frame['mean_price'].rolling(window=period).mean()
    rates_frame['std_low_'] = (rates_frame['low'].rolling(window=period).std() * 100) / rates_frame['mean_price'].rolling(window=period).mean()
    return rates_frame['std_'].iloc[-1], rates_frame['std_high_'].iloc[-1], rates_frame['std_low_'].iloc[-1]

def place_order(symbol, lot, tp, sl, order_type):
    price = mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
    tp = abs(price + tp) if order_type == mt5.ORDER_TYPE_BUY else abs(price - tp)
    sl = abs(price - sl) if order_type == mt5.ORDER_TYPE_BUY else abs(price + sl)

    lot = round_up(lot, 2)
    deviation = 100
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 234002,
        "comment": "Strategy",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logging.error(f"Order send failed: {result.retcode}")
    else:
        logging.info(f"Order send success: {result}")

def trade(symbol, lot, tp, sl):
    numtrade = 0
    sl = sl * 10
    level_buy = level_sell = None
    level_buy_count = level_sell_count = 0
    position_count = 0
    pros = 0
    sum_volum = []
    init_position = True

    while True:
        try:
            positions_total = len(mt5.positions_get(symbol=symbol))
            if positions_total == 0:
                position_count = 0

            if positions_total > 0 and positions_total < position_count:
                position_count = 0
                df_pross.loc[pros - 1, 'sum_trade'] = len(mt5.positions_get(symbol=symbol))
                close(symbol)
                break

            if positions_total == 0 and init_position:
                place_order(symbol, lot, tp, sl, mt5.ORDER_TYPE_BUY)
                level_buy = mt5.symbol_info_tick(symbol).bid
                level_sell = abs(mt5.symbol_info_tick(symbol).ask - (tp / 2))

                level_buy_count += 1
                position_count += 1
                sum_volum = [lot]
                numtrade += 1
                pros += 1
                init_position = False
                continue

            if mt5.symbol_info_tick(symbol).ask <= level_sell and level_sell_count < level_buy_count and numtrade == 1:
                sod_main = 0.01 if positions_total == 1 else 0.00
                level_sell_count = level_buy_count + 1
                position_count += 1
                level_vol_sell = sum_volum[0] * 2.5 + sod_main
                place_order(symbol, level_vol_sell, tp, sl, mt5.ORDER_TYPE_SELL)
                numtrade += 1
                sum_volum.append(level_vol_sell)

            if mt5.symbol_info_tick(symbol).ask >= level_buy and level_buy_count < level_sell_count and numtrade == 2:
                position_count = 0
                close(symbol)
                break

            time.sleep(0.01)
        except Exception as e:
            logging.error(f"Error in trade loop: {e}")

def close(symbol):
    positions = mt5.positions_get()
    def close_position(position):
        tick = mt5.symbol_info_tick(position.symbol)
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": position.ticket,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
            "price": tick.ask if position.type == 1 else tick.bid,
            "deviation": 100,
            "magic": 234002,
            "comment": "Strategy",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logging.error(f"Order close failed: {result.retcode}")
        else:
            logging.info(f"Order close success: {result}")

    for position in positions:
        if position.symbol == symbol:
            close_position(position)
            time.sleep(0.01)

def main():
    init()
    logging.info(info())
    pairs = ['GBPUSD_o', 'AUDUSD_o', 'NZDUSD_o', 'EURUSD_o', 'USDJPY_o']
    for pair in pairs:
        th.Thread(target=trade, args=(pair, 0.3, 0.0005, 0.01)).start()
        time.sleep(0.1)

def run():
    std_high_gbp = std_high_aud = std_high_nzd = 0.0225
    std_high_jpy = 0.015
    std_gbp = std_nzd = 0.02
    std_aud = 0.025
    std_jpy = std_high_jpy

    while True:
        try:
            init()
            logging.info(info())
            logging.info(f"Run at {datetime.datetime.now(tehran_timezone)}")

            stding_gbp, stding_high_gbp, stding_low_gbp = std('GBPUSD_o', 3)
            if stding_gbp >= std_gbp or stding_high_gbp >= std_high_gbp or stding_low_gbp >= std_high_gbp:
                th.Thread(target=trade, args=('GBPUSD_o', 0.3, 0.0005, 0.01)).start()

            time.sleep(1)

            stding_aud, stding_high_aud, stding_low_aud = std('AUDUSD_o', 3)
            if stding_aud >= std_aud or stding_high_aud >= std_high_aud or stding_low_aud >= std_high_aud:
                th.Thread(target=trade, args=('AUDUSD_o', 0.3, 0.0005, 0.01)).start()

            time.sleep(1)

            stding_nzd, stding_high_nzd, stding_low_nzd = std('NZDUSD_o', 3)
            if stding_nzd >= std_nzd or stding_high_nzd >= std_high_nzd or stding_low_nzd >= std_high_nzd:
                th.Thread(target=trade, args=('NZDUSD_o', 0.3, 0.0005, 0.01)).start()

            time.sleep(1)

            stding_jpy, stding_high_jpy, stding_low_jpy = std('USDJPY_o', 3)
            if stding_jpy >= std_jpy or stding_high_jpy >= std_high_jpy or stding_low_jpy >= std_high_jpy:
                th.Thread(target=trade, args=('USDJPY_o', 0.3, 0.05, 0.05)).start()

            time.sleep(1)
        except Exception as e:
            logging.error(f"Error in run loop: {e}")

# run()
