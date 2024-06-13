
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



def buy(symbol , lot , tp_ , sl_ , comment ):

    
    
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
        "deviation": deviation,
        "magic": 234002,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK ,
    }
     
    # send a trading request
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return ("failed . order_send failed, retcode={} {}".format(result.retcode ,request )) , False
        
    if result.retcode == 10009 :
        return result
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


def sell(symbol , lot , tp_ , sl_, comment ):

    
    
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
        "deviation": deviation,
        "magic": 234002,
        "comment":  comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK ,
    }
     
    # send a trading request
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return ("failed . order_send failed, retcode={} {}".format(result.retcode ,request )) , False
        
    if result.retcode == 10009 :
        return result
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


def write_to_csv(filename, data):
    df = pd.DataFrame(data, columns=[ 'prof'])
    try:
        existing_df = pd.read_csv(filename)
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_csv('trade_data.csv', index=False)


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


def close(ticket):
    
    
    
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
        
        if position.ticket == ticket :
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


# def sod_sang(tickit_one_one , tickit_one_tow , tickit_tow_one , tickit_tow_tow ):
#     # while True:
#     init_balance_one = True
#     init_balance_tow = True
#     init = False
#     while True:
        
#         time.sleep(0.5)
#         if init_balance_one :
#             balance_one = mt5.positions_get( ticket =  tickit_one_one.order )[0].profit + mt5.positions_get( ticket =  tickit_one_tow.order )[0].profit
            

#             if balance_one > 100 :
#                 print(balance_one )
#             if balance_one > 140 and init_balance_tow and init_balance_one :
#                 close(tickit_one_one.order)
#                 close(tickit_one_tow.order)
#                 init_balance_one = False
#                 continue
#             if balance_one >= 0 and not init_balance_tow and init_balance_one :

#                 tickit_one_one , tickit_one_tow = run_one()
#                 init_balance_one = True
#                 init = True
#                 time.sleep(2)

#         if init_balance_tow:
#             balance_tow = mt5.positions_get( ticket =  tickit_tow_one.order )[0].profit + mt5.positions_get( ticket =  tickit_tow_tow.order )[0].profit
#             if balance_tow > 100 :
#                 print( balance_tow )
#             if balance_tow > 140 and init_balance_tow and init_balance_one :
#                 close(tickit_tow_one.order)
#                 close(tickit_tow_tow.order)
#                 init_balance_tow = False
#                 continue
#             if balance_tow >= 0 and init_balance_tow and not init_balance_one :

#                 tickit_tow_one , tickit_tow_tow = run_tow()
#                 init_balance_tow = True
#                 init = True
#                 time.sleep(2)

#         # if init :
#         #     sod_jam =  mt5.positions_get( ticket =  tickit_one_one.order )[0].profit + mt5.positions_get( ticket =  tickit_one_tow.order )[0].profit + mt5.positions_get( ticket =  tickit_tow_one.order )[0].profit + mt5.positions_get( ticket =  tickit_tow_tow.order )[0].profit
#         #     if sod_jam > 100 :
#         #         close(tickit_one_one.order)
#         #         close(tickit_one_tow.order)
#         #         close(tickit_tow_one.order)
#         #         close(tickit_tow_tow.order)
#         #         time.sleep(2)
#         #         run()
        
# # حجم معامله GBPUSD: 0.00334 لات
# # حجم معامله EURUSD: 0.00457 لات
# def run_one():

#     tickit_one_one =  buy('GBPUSD_o', 3.61 , 0 , 0 , 'one')
#     tickit_one_tow =  sell('EURUSD_o', 5 , 0 , 0 , 'one')

#     return tickit_one_one , tickit_one_tow 


# def run_tow():
    
#     tickit_tow_one =  sell('GBPUSD_o', 3.61 , 0 , 0 , 'tow')
#     tickit_tow_tow =  buy('EURUSD_o', 5 , 0 , 0 , 'tow')

#     return  tickit_tow_one , tickit_tow_tow

# def run():
#     init()
#     while True:
#         now = datetime.datetime.now(tehran_timezone)
#         if 0 < now.hour < 24  :
#             try:

#                 if len(mt5.positions_get(symbol='GBPUSD_o')) == 0 and len(mt5.positions_get(symbol='EURUSD_o')) == 0:
#                     tickit_one_one =  buy('GBPUSD_o', 3.61 , 0 , 0 , 'one')
#                     tickit_one_tow =  sell('EURUSD_o', 5 , 0 , 0 , 'one')
#                     tickit_tow_one =  sell('GBPUSD_o', 3.61 , 0 , 0 , 'tow')
#                     tickit_tow_tow =  buy('EURUSD_o', 5 , 0 , 0 , 'tow')

#                     return tickit_one_one , tickit_one_tow , tickit_tow_one , tickit_tow_tow

#                 # if len(mt5.positions_get(symbol='GBPUSD_o')) == 0 and len(mt5.positions_get(symbol='EURUSD_o')) == 0:

#                 #     tickit_tow_one =  th.Thread(target=buy  , args=('GBPUSD_o', 1, 0 , 0 , 'tow')).start()
#                 #     tickit_tow_tow =  th.Thread(target=sell , args=('EURUSD_o', 1, 0 , 0 , 'tow' )).start()






#             except Exception as e:
#                 print(f"Error: {e}")
#                 time.sleep(60)  # Wait for 1 minute before retrying

#         time.sleep(60)  # Wait for 1 minute before retrying






# print(datetime.datetime.now(tehran_timezone))
# tickit_one_one , tickit_one_tow , tickit_tow_one , tickit_tow_tow = run()

# if tickit_one_one and tickit_one_tow and tickit_tow_one and tickit_tow_tow :
    

#     sod_sang(tickit_one_one , tickit_one_tow , tickit_tow_one , tickit_tow_tow)



def sod_sang(tickit_one_one, tickit_one_tow, tickit_tow_one, tickit_tow_tow):
    init_balance_one = True
    init_balance_tow = True
    init = False
    while True:
        time.sleep(0.3)
        if init_balance_one:
            positions_one_one = mt5.positions_get(ticket=tickit_one_one.order)
            positions_one_tow = mt5.positions_get(ticket=tickit_one_tow.order)
            if positions_one_one and positions_one_tow:
                balance_one = positions_one_one[0].profit + positions_one_tow[0].profit
                if balance_one > 90 :
                    print(balance_one)
                if balance_one > 100 and init_balance_tow and init_balance_one:
                    close(tickit_one_one.order)
                    close(tickit_one_tow.order)
                    init_balance_one = False
                    continue
                if balance_one >= 0 and not init_balance_tow and init_balance_one:
                    tickit_tow_one, tickit_tow_tow = run_tow()
                    init_balance_tow = True
                    init = True
                    time.sleep(2)

        if init_balance_tow:
            positions_tow_one = mt5.positions_get(ticket=tickit_tow_one.order)
            positions_tow_tow = mt5.positions_get(ticket=tickit_tow_tow.order)
            if positions_tow_one and positions_tow_tow:
                balance_tow = positions_tow_one[0].profit + positions_tow_tow[0].profit
                if balance_tow > 90 :
                    print(balance_tow)
                if balance_tow > 100 and init_balance_tow and init_balance_one:
                    close(tickit_tow_one.order)
                    close(tickit_tow_tow.order)
                    init_balance_tow = False
                    continue
                if balance_tow >= 0 and init_balance_tow and not init_balance_one:
                    tickit_one_one, tickit_one_tow = run_one()
                    init_balance_one = True
                    init = True
                    time.sleep(2)


def run_one():

    tickit_one_one =  buy('GBPUSD_o', 2.6 , 0 , 0 , 'one')
    tickit_one_tow =  sell('EURUSD_o',  3 , 0 , 0 , 'one')

    return tickit_one_one , tickit_one_tow 


def run_tow():
    
    tickit_tow_one =  sell('GBPUSD_o', 2.6 , 0 , 0 , 'tow')
    tickit_tow_tow =  buy('EURUSD_o',  3 , 0 , 0 , 'tow')

    return  tickit_tow_one , tickit_tow_tow

def run():
    init()
    while True:
        now = datetime.datetime.now(tehran_timezone)
        if 9 < now.hour < 24  :
            try:

                if len(mt5.positions_get(symbol='GBPUSD_o')) == 0 and len(mt5.positions_get(symbol='EURUSD_o')) == 0:
                    tickit_one_one =  buy('GBPUSD_o', 2.6 , 0 , 0 , 'one')
                    tickit_one_tow =  sell('EURUSD_o', 3 , 0 , 0 , 'one')
                    tickit_tow_one =  sell('GBPUSD_o', 2.6 , 0 , 0 , 'tow')
                    tickit_tow_tow =  buy('EURUSD_o', 3 , 0 , 0 , 'tow')

                    return tickit_one_one , tickit_one_tow , tickit_tow_one , tickit_tow_tow
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)  # Wait for 1 minute before retrying
        time.sleep(60)  # Wait for 1 minute before retrying

print(datetime.datetime.now(tehran_timezone))
tickit_one_one, tickit_one_tow, tickit_tow_one, tickit_tow_tow = run()

if tickit_one_one and tickit_one_tow and tickit_tow_one and tickit_tow_tow:
    sod_sang(tickit_one_one, tickit_one_tow, tickit_tow_one, tickit_tow_tow)
