
import MetaTrader5 as mt5
import pandas as pd 
import threading as th
import time
import datetime

import math
import pytz
import numpy as np


tehran_timezone = pytz.timezone('Asia/Tehran')

df_pross = pd.DataFrame(columns= ['time' ,  'pros' , 'sum_trade' , 'balance'])

def round_up(number, precision):

  return math.ceil(number * (10**precision)) / (10**precision)


def init():
    # mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 real\terminal64.exe")
    # mt5.login(6910350 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Live')
    mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 2\terminal64.exe")
    mt5.login(89373537 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Demo')


def info():

    account_info=mt5.account_info()

    balance = account_info.balance
    equity  = account_info.equity
    profit  = account_info.profit
    
    return balance , equity , profit
    

def symbol_info(symbol):
    dic_symbol_info = {}
    group_symbols=mt5.symbols_get(group='*USD*')
    for s in group_symbols:
        if s.name == symbol : 
            dic_symbol_info[s.name] =  s.ask , s.bid
            
    return dic_symbol_info  # برمیگرداند یک دیکشنری که کلدی ها نماد و در ولیو ها اسک و بید به صورت تاپل 


def get_data(symbol, timeframe, n=110):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert(tehran_timezone)
    df['time'] = df['time'].dt.tz_localize(None)
    df.set_index('time', inplace=True)
    return df

# Function to calculate Bollinger Bands
def bollinger_bands(price, window=20, num_of_std=2):
    rolling_mean = price.rolling(window).mean()
    rolling_std = price.rolling(window).std()
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)
    return upper_band, rolling_mean, lower_band

# Function to calculate RSI
def RSI(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to calculate MACD
def MACD(price, slow=26, fast=12, signal=9):
    exp1 = price.ewm(span=fast, adjust=False).mean()
    exp2 = price.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist

# Function to calculate indicators
def calculate_indicators(df):
    df['upper_band'], df['middle_band'], df['lower_band'] = bollinger_bands(df['close'])
    df['rsi'] = RSI(df['close'])
    # df['macd'], df['signal'], df['hist'] = MACD(df['close'])
    # df['sma_short'] = df['close'].rolling(window=5).mean()
    # df['sma_long'] = df['close'].rolling(window=20).mean()
    return df


def smooth_rng(x, t, m):
    wper = (t * 2) - 1
    avrng = x.diff().abs().rolling(window=t).mean()
    smoothrng = avrng.ewm(span=wper, adjust=False).mean() * m
    return smoothrng


def rng_filt(x, r):
    rngfilt = np.zeros_like(x)
    rngfilt[0] = x[0]  # Initial condition for the filter
    for i in range(1, len(x)):
        if x[i] > rngfilt[i - 1]:
            rngfilt[i] = rngfilt[i - 1] if (x[i] - r[i]) < rngfilt[i - 1] else (x[i] - r[i])
        else:
            rngfilt[i] = rngfilt[i - 1] if (x[i] + r[i]) > rngfilt[i - 1] else (x[i] + r[i])
    return rngfilt


def calculate_indicators_(df, per, mult):
    src = df['close']
    smrng = smooth_rng(src, per, mult)
    filt = rng_filt(src, smrng)

    df['smooth_rng'] = smrng
    df['filt'] = filt

    upward = np.zeros(len(filt))
    downward = np.zeros(len(filt))

    for i in range(1, len(filt)):
        if filt[i] > filt[i - 1]:
            upward[i] = upward[i - 1] + 1
            downward[i] = 0
        elif filt[i] < filt[i - 1]:
            downward[i] = downward[i - 1] + 1
            upward[i] = 0
        else:
            upward[i] = upward[i - 1]
            downward[i] = downward[i - 1]

    df['upward'] = upward
    df['downward'] = downward

    hband = filt + smrng
    lband = filt - smrng

    df['hband'] = hband
    df['lband'] = lband

    df['buy_signal'] = (((df['close'] > df['filt']) & (df['close'] > df['close'].shift(1)) & (df['upward'] > 0)) |
                        ((df['close'] > df['filt']) & (df['close'] < df['close'].shift(1)) & (df['upward'] > 0)))

    df['sell_signal'] = (((df['close'] < df['filt']) & (df['close'] < df['close'].shift(1)) & (df['downward'] > 0)) |
                         ((df['close'] < df['filt']) & (df['close'] > df['close'].shift(1)) & (df['downward'] > 0)))

    df['long_condition'] = df['buy_signal'] & (~df['buy_signal'].shift(1).fillna(False))
    df['short_condition'] = df['sell_signal'] & (~df['sell_signal'].shift(1).fillna(False))

    return df


def buy(symbol , lot , tp_ , sl_ ):

    
    
    tp = abs(mt5.symbol_info_tick(symbol).bid + tp_ ) 
    sl = abs(mt5.symbol_info_tick(symbol).ask - sl_ ) 
    pos = mt5.ORDER_TYPE_BUY



    lot = round_up(lot, 2)
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).ask
    deviation = 100
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type":  pos ,
        "price": price,
        "sl": sl ,
        "tp": tp ,
        "deviation": deviation,
        "magic": 234002,
        "comment": "Gu",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK ,
    }
     
    # send a trading request
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return ("failed . order_send failed, retcode={} {}".format(result.retcode ,request )) , False
        
    if result.retcode == 10009 :
        return ("Done . position #{} closed".format(result)) , True
    # if result:
    #     if result.retcode != mt5.TRADE_RETCODE_DONE:
    #         print("2. order_send failed, retcode={}".format(result.retcode))
    #         # request the result as a dictionary and display it element by element
    #         result_dict=result._asdict()
    #         for field in result_dict.keys():
    #             print("   {}={}".format(field,result_dict[field]))
    #             # if this is a trading request structure, display it element by element as well
    #             if field=="request":
    #                 traderequest_dict=result_dict[field]._asdict()
    #                 for tradereq_filed in traderequest_dict:
    #                     print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))


def sell(symbol , lot , tp_ , sl_ ):

    
    
    tp = abs(mt5.symbol_info_tick(symbol).ask - tp_  ) 
    sl = abs(mt5.symbol_info_tick(symbol).bid + sl_   ) 
    # tp = abs(mt5.symbol_info_tick(symbol).ask - tp_ -  (tp_ / 2 ) ) 
    # sl = abs(mt5.symbol_info_tick(symbol).bid + sl_ - ( tp_ / 2) ) 
    pos = mt5.ORDER_TYPE_SELL



    lot = round_up(lot, 2)
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).ask
    deviation = 100
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type":  pos ,
        "price": price,
        "sl": sl ,
        "tp": tp ,
        "deviation": deviation,
        "magic": 234002,
        "comment": "Gu",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK ,
    }
     
    # send a trading request
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return ("failed . order_send failed, retcode={} {}".format(result.retcode ,request )) , False
        
    if result.retcode == 10009 :
        return ("Done . position #{} closed".format(result)) , True
    # if result:
    #     if result.retcode != mt5.TRADE_RETCODE_DONE:
    #         print("2. order_send failed, retcode={}".format(result.retcode))
    #         # request the result as a dictionary and display it element by element
    #         result_dict=result._asdict()
    #         for field in result_dict.keys():
    #             print("   {}={}".format(field,result_dict[field]))
    #             # if this is a trading request structure, display it element by element as well
    #             if field=="request":
    #                 traderequest_dict=result_dict[field]._asdict()
    #                 for tradereq_filed in traderequest_dict:
    #                     print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))


def sell_stop(symbol , lot , tp_ , sl_ , reward):
    

    tp = abs(mt5.symbol_info_tick(symbol).ask - tp_ - reward ) 
    sl = abs(mt5.symbol_info_tick(symbol).bid  ) 
    pos = mt5.ORDER_TYPE_SELL_STOP







    lot = round_up(lot, 2)
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).ask - ( sl_)
    deviation = 100
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot,
        "type":  pos ,
        "price": price,
        "sl": sl ,
        "tp": tp ,
        "deviation": deviation,
        "magic": 234002,
        "comment": "Gu",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK ,
    }
        
    # send a trading request
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return ("failed . order_send failed, retcode={} {}".format(result.retcode ,request )) , False
        
    if result.retcode == 10009 :
        return ("Done . position #{} closed".format(result)) , True
        # request the result as a dictionary and display it element by element
        
    # if result:
    #     if result.retcode != mt5.TRADE_RETCODE_DONE:
    #         print("2. order_send failed, retcode={}".format(result.retcode))
    #         # request the result as a dictionary and display it element by element
    #         result_dict=result._asdict()
    #         for field in result_dict.keys():
    #             print("   {}={}".format(field,result_dict[field]))
    #             # if this is a trading request structure, display it element by element as well
    #             if field=="request":
    #                 traderequest_dict=result_dict[field]._asdict()
    #                 for tradereq_filed in traderequest_dict:
    #                     print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))


def buy_stop(symbol , lot , tp_ , sl_  , reward):
    
    tp = abs(mt5.symbol_info_tick(symbol).ask + tp_ + reward ) 
    sl = abs(mt5.symbol_info_tick(symbol).bid  ) 
    pos = mt5.ORDER_TYPE_BUY_STOP
    







    lot = round_up(lot, 2)
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).ask + ( sl_)
    deviation = 100
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot,
        "type":  pos ,
        "price": price,
        "sl": sl ,
        "tp": tp ,
        "deviation": deviation,
        "magic": 234002,
        "comment": "Gu",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK ,
    }
        
    # send a trading request
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return ("failed . order_send failed, retcode={} {}".format(result.retcode ,request )) , False
        
    if result.retcode == 10009 :
        return ("Done . position #{} closed".format(result)) , True
        # request the result as a dictionary and display it element by element
        
    # if result:
    #     if result.retcode != mt5.TRADE_RETCODE_DONE:
    #         print("2. order_send failed, retcode={}".format(result.retcode))
    #         # request the result as a dictionary and display it element by element
    #         result_dict=result._asdict()
    #         for field in result_dict.keys():
    #             print("   {}={}".format(field,result_dict[field]))
    #             # if this is a trading request structure, display it element by element as well
    #             if field=="request":
    #                 traderequest_dict=result_dict[field]._asdict()
    #                 for tradereq_filed in traderequest_dict:
    #                     print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))


def trade_up(symbol , lot , tp , sl , reward ):
    zareb = 0.5
    numtrade = 0
    # up_numtrade = 0
    sl = sl 
    level_buy  = None   # price level buy
    level_sell = None   # price level sell
    
    level_buy_count  = 0
    level_sell_count = 0
    
    level_vol_buy   = 0
    level_vol_sell  = 0
    
    position_count = 0
    

    
    sum_volum = []

    pross = 0

    init_position = True
    init_sell = False
    init_sell_close = False
    init_buy = False


            
    sell_init = False
    buy_init = False    
    
    while True:
        
        

        positions_total=len(mt5.positions_get(symbol=symbol))
        
        if positions_total == 0:
            position_count = 0
            
        
    
            
            
        
        if   len(mt5.positions_get(symbol=symbol)) == 0 and init_position  :
            
            
            log , doit = buy( symbol, lot ,  tp ,  sl )
            sell_init  = True
            level_buy_count += 1
            position_count += 1
            level_vol_buy = lot
            level_sell_count = 0
            sum_volum = []
            sum_volum.append(lot)
            init_position = False
            init_sell = True
            print('Buy', doit , log)
            init_buy = True
            time.sleep(0.5)
            continue



        if   len(mt5.positions_get(symbol=symbol)) == 1   :
            if mt5.positions_get(symbol=symbol)[0].type == 0 and sell_init : 
                sell_init = False
                buy_init = True
                lot = lot + (lot * zareb)
                log , doit = sell_stop( symbol, lot ,  tp ,  sl , sl  )   
                while True : 
                    if not doit:
                        log , doit = sell_stop( symbol, lot ,  tp ,  sl , sl  ) 
                        continue
                    else : 
                        time.sleep(0.1)
                        break
                


                


                

            if mt5.positions_get(symbol=symbol)[0].type == 1 and buy_init :
                buy_init = False
                sell_init = True
                lot = lot + (lot * zareb)
                log , doit = buy_stop( symbol, lot ,  tp ,  sl , sl  )
                while True : 
                    if not doit:
                        log , doit = buy_stop( symbol, lot ,  tp ,  sl , sl  ) 
                        continue
                    else : 
                        time.sleep(0.1)
                        break



            

        if  len(mt5.positions_get(symbol=symbol)) == 0 and init_buy   :
            time.sleep(0.1)
            if  len(mt5.positions_get(symbol=symbol)) == 0 :
                order_close(symbol)
                break
            


        time.sleep(0.1)


def trade_down(symbol , lot , tp , sl , reward):
    zareb = 0.5
    numtrade = 0
    # up_numtrade = 0
    sl = sl 
    level_buy  = None   # price level buy
    level_sell = None   # price level sell
    
    level_buy_count  = 0
    level_sell_count = 0
    
    level_vol_buy   = 0
    level_vol_sell  = 0
    
    position_count = 0
    

    
    sum_volum = []

    pross = 0

    init_position = True
    init_sell = False
    init_sell_close = False
    init_buy = False
    init_sell = False

            
    sell_init = False
    buy_init = False    
    
    while True:
        
        

        positions_total=len(mt5.positions_get(symbol=symbol))
        
        if positions_total == 0:
            position_count = 0
            
        
    
            
            
        
        if   len(mt5.positions_get(symbol=symbol)) == 0 and init_position  :
            
            
            log , doit = sell( symbol, lot ,  tp ,  sl )
            sell_init  = True
            level_buy_count += 1
            position_count += 1
            level_vol_buy = lot
            level_sell_count = 0

            init_position = False
            init_sell = True

            init_buy = True
            time.sleep(0.5)

            continue



        if   len(mt5.positions_get(symbol=symbol)) == 1   :
            if mt5.positions_get(symbol=symbol)[0].type == 1 and sell_init : 
                sell_init = False
                buy_init = True
                lot = lot + (lot * zareb)
                log , doit = buy_stop( symbol, lot ,  tp ,  sl , sl  )   
                while True : 
                    if not doit:
                        log , doit = buy_stop( symbol, lot ,  tp ,  sl , sl  ) 
                        continue
                    else : 
                        time.sleep(0.1)
                        break 
                continue
                


                


                

            if mt5.positions_get(symbol=symbol)[0].type == 0 and buy_init :
                buy_init = False
                sell_init = True
                lot = lot + (lot * zareb)
                log , doit = sell_stop( symbol, lot ,  tp ,  sl , sl  )
                while True : 
                    if not doit:
                        log , doit = sell_stop( symbol, lot ,  tp ,  sl , sl  ) 
                        continue
                    else : 
                        time.sleep(0.1)
                        break



            

        if  len(mt5.positions_get(symbol=symbol)) == 0 and init_buy   :
            time.sleep(0.1)
            if  len(mt5.positions_get(symbol=symbol)) == 0 :
                order_close(symbol)
                break
            


        time.sleep(0.1)



def main():
    # دریافت زمان فعلی


    init()



    # if len(mt5.positions_get( symbol = 'USDJPY_o' )) == 0:
    #     th.Thread(target= trade , args= ( 'USDJPY_o' ,  0.6 , 0.05   , 0.05 )).start()
    # time.sleep(0.3)    

    # if len(mt5.positions_get( symbol = 'GBPUSD_o' )) == 0:
    #     th.Thread(target= trade , args= ( 'GBPUSD_o' ,  0.3 , 0.0005, 0.01 )).start()
    # time.sleep(0.3)

    # if len(mt5.positions_get( symbol = 'AUDUSD_o' )) == 0:
    #     th.Thread(target= trade , args= ( 'AUDUSD_o' ,  0.1 , 0.0005 , 0.01 )).start()
    # time.sleep(0.3)

    # if len(mt5.positions_get( symbol = 'NZDUSD_o' )) == 0:
    #     th.Thread(target= trade , args= ( 'NZDUSD_o' ,  0.1 , 0.0005 , 0.01 )).start()
    # time.sleep(0.3)

    # if len(mt5.positions_get( symbol = 'EURUSD_o' )) == 0:
    #     th.Thread(target= trade , args= ( 'EURUSD_o' ,  0.3 , 0.0005 , 0.01 )).start()
    # time.sleep(0.3)

    # if len(mt5.positions_get( symbol = 'USDCAD_o' )) == 0:
    #     th.Thread(target= trade , args= ( 'USDCAD_o' ,  0.3 , 0.0005 , 0.01)).start()
    # time.sleep(0.3)

    # if len(mt5.positions_get( symbol = 'USDCHF_o' )) == 0:
    #     th.Thread(target= trade , args= ( 'USDCHF_o' ,  0.5 , 0.0005 , 0.0006 )).start()



    # trade(symbol='USDJPY_o' , lot= 0.1 ,tp= 0.009 ,sl= 0.006)
    # trade(symbol='GBPUSD_o' , lot= 0.5 ,tp= 0.0006 ,sl= 0.004)
    # trade(symbol='NZDUSD_o' , lot= 0.1 ,tp= 0.00009 ,sl= 0.0006)
    # trade(symbol='USDCAD_o' , lot= 0.1 ,tp= 0.00009 ,sl= 0.0006)
    # trade(symbol='USDCHF_o' , lot= 0.1 ,tp= 0.00009 ,sl= 0.0006)
    # trade(symbol='EURUSD_o' , lot= 0.2 ,tp= 0.0004 ,sl= 0.01)
    # trade(symbol='XAUUSD_o' , lot= 0.02  ,tp= 1,sl= 1)


def close(symbol):
    
    
    
    def close_position(position):
        try:
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
                "comment": "Gu",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK ,
            }

            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                result ("Close failed . order_send failed, retcode={} {}".format(result.retcode ,request ))
                return False
            if result.retcode == 10009 :
                return True  
        except Exception as e:
            print(f'Close : Eror in def close {e}')

    positions = mt5.positions_get()
    for position in positions:
        # print(position)
        
        if position.symbol == symbol :
            try:
                
                doit =  close_position(position)
                time.sleep(0.1)

            except Exception as e:
                print(f'Clsoe : Eror for Clsoe {e}')
            time.sleep(0.05)


def order_close(symbol):
    orders=mt5.orders_get(symbol = symbol)
    

    if orders :
        request = {

            'action' : mt5.TRADE_ACTION_REMOVE , 
            'order'  : mt5.orders_get(symbol = symbol)[0].ticket

        }
        
        result =  mt5.order_send(request)
        if result is None:
            print("No orders with group=\"*GBP*\", error code={}".format(mt5.last_error()))
        else:

            if result.retcode == 10009 :

                return  True


import random

def scalping_strategy(symbol,  per, mult):
    df = get_data(symbol, mt5.TIMEFRAME_M1)
    # df = calculate_indicators(df)
    df = calculate_indicators_(df ,  per, mult)

    for i in range(1, len(df)):
        if i == len(df) -1 :
        # buy_signal = (df['close'][i] > df['lower_band'][i]) and (df['rsi'][i] > 30) and (df['macd'][i] > df['signal'][i]) and (df['sma_short'][i] > df['sma_long'][i])
        # sell_signal = (df['close'][i] < df['upper_band'][i]) and (df['rsi'][i] < 70) and (df['macd'][i] < df['signal'][i]) and (df['sma_short'][i] < df['sma_long'][i])

            # buy_signal = (df['close'][i] < df['lower_band'][i]) and (df['rsi'][i] < 30) 
            # sell_signal = (df['close'][i] > df['upper_band'][i]) and (df['rsi'][i] > 70) 

            # buy_signal = (df['rsi'][i] < 30) 
            # sell_signal =  (df['rsi'][i] > 70) 


            buy_signal = df['long_condition'][i]
            sell_signal = df['short_condition'][i]





            if buy_signal:
                return 'buy'
                # Place a buy order here
            else :
                print(f'not buy segnal for {symbol}')


            if sell_signal:
                return 'sell'
            else:
                print(f'not sell segnal for {symbol}')
        




def run():
    init()
    while True:
        now = datetime.datetime.now(tehran_timezone)
        if 9 < now.hour < 22 :
            try:
                gbp_per, gbp_mult = 50, 1
                gbp_signal = scalping_strategy('GBPUSD_o' , gbp_per, gbp_mult)
                if gbp_signal == 'buy' and len(mt5.positions_get(symbol='GBPUSD_o')) == 0:
                    th.Thread(target=trade_up, args=('GBPUSD_o', 0.2, 0.0006, 0.0002 , 3)).start()
                if gbp_signal == 'sell' and len(mt5.positions_get(symbol='GBPUSD_o')) == 0:
                    th.Thread(target=trade_down, args=('GBPUSD_o', 0.2, 0.0006, 0.0002 , 3)).start()
                time.sleep(3)

                gbp_per, gbp_mult = 50, 1
                jpy_signal = scalping_strategy('USDJPY_o' ,  gbp_per, gbp_mult)
                if jpy_signal == 'buy' and len(mt5.positions_get(symbol='USDJPY_o')) == 0:
                    th.Thread(target=trade_up, args=('USDJPY_o', 0.3, 0.06, 0.02 , 3)).start()
                if jpy_signal == 'sell' and len(mt5.positions_get(symbol='USDJPY_o')) == 0:
                    th.Thread(target=trade_down, args=('USDJPY_o', 0.3, 0.06, 0.02 , 3)).start()
                time.sleep(1)

                gbp_per, gbp_mult = 50, 1
                chf_signal = scalping_strategy('USDCHF_o' , gbp_per, gbp_mult)
                if chf_signal == 'buy' and len(mt5.positions_get(symbol='USDCHF_o')) == 0:
                    th.Thread(target=trade_up, args=('USDCHF_o', 0.2, 0.0006, 0.0002 , 3)).start()
                if chf_signal == 'sell' and len(mt5.positions_get(symbol='USDCHF_o')) == 0:
                    th.Thread(target=trade_down, args=('USDCHF_o', 0.2, 0.0006, 0.0002 , 3)).start()
                time.sleep(3)

                # aud_signal = scalping_strategy('AUDUSD_o')
                # if aud_signal == 'buy' and len(mt5.positions_get(symbol='AUDUSD_o')) == 0:
                #     th.Thread(target=trade_up, args=('AUDUSD_o', 0.01, 0.0005, 0.0006)).start()
                # if aud_signal == 'sell' and len(mt5.positions_get(symbol='AUDUSD_o')) == 0:
                #     th.Thread(target=trade_down, args=('AUDUSD_o', 0.01, 0.0005, 0.0006)).start()
                # time.sleep(1)

                # nzd_signal = scalping_strategy('NZDUSD_o')
                # if nzd_signal == 'buy' and len(mt5.positions_get(symbol='NZDUSD_o')) == 0:
                #     th.Thread(target=trade_up, args=('NZDUSD_o', 0.01, 0.0005, 0.0006)).start()
                # if nzd_signal == 'sell' and len(mt5.positions_get(symbol='NZDUSD_o')) == 0:
                #     th.Thread(target=trade_down, args=('NZDUSD_o', 0.01, 0.0005, 0.0006)).start()
                # time.sleep(1)

                # gbp_per, gbp_mult = 50, 1
                # cad_signal = scalping_strategy('USDCAD_o'  , gbp_per, gbp_mult)
                # if cad_signal == 'buy' and len(mt5.positions_get(symbol='USDCAD_o')) == 0:
                #     th.Thread(target=trade_up, args=('USDCAD_o', 0.01, 0.00025, 0.0001 , 3)).start()
                # if cad_signal == 'sell' and len(mt5.positions_get(symbol='USDCAD_o')) == 0:
                #     th.Thread(target=trade_down, args=('USDCAD_o', 0.01, 0.00025, 0.0001 , 3)).start()
                # time.sleep(1)



            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)  # Wait for 1 minute before retrying


print(datetime.datetime.now(tehran_timezone))
run()
