
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
df_pross = pd.DataFrame(columns= ['time' ,  'pros' , 'sum_trade' , 'balance'])
df_history = pd.DataFrame(columns= ['time_open' , 'time'])



def comission(lot , comission):
    return     (lot * 100) * comission


def round_up(number, precision):

  return math.ceil(number * (10**precision)) / (10**precision)


def init():
    # mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 real\terminal64.exe")
    # mt5.login(6910350 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Live')
    init = mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 3\terminal64.exe")
    mt5.login(89373537 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Demo')
    return init

def info():

    account_info=mt5.account_info()

    balance = account_info.balance
    equity  = account_info.equity
    profit  = account_info.profit
    
    return balance , equity , profit



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


def sell_stop(symbol , lot , tp_ , sl_ , reward , price_):
    

    # tp = abs(mt5.symbol_info_tick(symbol).ask - tp_ - reward ) 
    tp = tp_
    sl = abs(mt5.symbol_info_tick(symbol).bid  ) 
    pos = mt5.ORDER_TYPE_SELL_STOP







    lot = round_up(lot, 2)
    point = mt5.symbol_info(symbol).point
    # price = mt5.symbol_info_tick(symbol).ask - ( sl_)
    price = price_
    deviation = 100
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot,
        "type":  pos ,
        "price": price,
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
        return result
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


def buy_stop(symbol , lot , tp_ , sl_  , reward , price_):
    
    # tp = abs(mt5.symbol_info_tick(symbol).ask + tp_ + reward ) 
    tp = tp_
    sl = abs(mt5.symbol_info_tick(symbol).bid  ) 
    pos = mt5.ORDER_TYPE_BUY_STOP
    







    lot = round_up(lot, 2)
    point = mt5.symbol_info(symbol).point
    # price = mt5.symbol_info_tick(symbol).ask + ( sl_)
    price = price_
    deviation = 100
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot,
        "type":  pos ,
        "price": price,
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
        return result
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


def sell_limit(symbol , lot , tp_ , sl_  , reward , price_):
    

    # tp = abs(mt5.symbol_info_tick(symbol).ask - tp_ - reward ) 
    tp = tp_
    sl = abs(mt5.symbol_info_tick(symbol).bid  ) 
    pos = mt5.ORDER_TYPE_SELL_LIMIT







    lot = round_up(lot, 2)
    point = mt5.symbol_info(symbol).point
    # price = mt5.symbol_info_tick(symbol).ask - ( sl_)
    price = price_
    deviation = 100
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot,
        "type":  pos ,
        "price": price,
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
        return result
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


def buy_limit(symbol , lot , tp_ , sl_  , reward , price_):
    
    # tp = abs(mt5.symbol_info_tick(symbol).ask + tp_ + reward ) 
    tp = tp_
    sl = abs(mt5.symbol_info_tick(symbol).bid  ) 
    pos = mt5.ORDER_TYPE_BUY_LIMIT
    







    lot = round_up(lot, 2)
    point = mt5.symbol_info(symbol).point
    # price = mt5.symbol_info_tick(symbol).ask + ( sl_)
    price = price_
    deviation = 100
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot,
        "type":  pos ,
        "price": price,
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
        return result
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


def trade(symbol , pip , vol):

    dic_level_up = {}
    dic_level_up_ = {}
    dic_level_down = {}
    dic_level_down_ = {}
    dic_level = {}
    main_level = mt5.symbol_info_tick(symbol).bid

    for i in range(1, 50):

        one = buy_stop(symbol ,vol , (main_level + i * pip ) +  pip , 0 , 0 , main_level + i * pip  )  
        dic_level_up[one.order]    =  one
        tow =  buy_limit(symbol , vol , (main_level - i * pip ) +  pip , 0 , 0 , main_level - i * pip  )
        dic_level_up_[tow.order]   =  tow
        tree = sell_stop(symbol , vol , (main_level - i * pip) - pip , 0 , 0 , main_level - i * pip   ) 
        dic_level_down[tree.order]  =  tree
        four = sell_limit(symbol , vol , (main_level + i * pip) - pip , 0 , 0 , main_level + i * pip  )       
        dic_level_down_[four.order] = four
        
        
        
        


    dic_level.update(dic_level_up)
    dic_level.update(dic_level_up_)
    dic_level.update(dic_level_down)
    dic_level.update(dic_level_down_)

    while True:
        time.sleep(0.1)
        order_init   = []
        order_active = []
        order_pos    = []

       

        for i in dic_level:
            order_init.append(dic_level[i].order)

        result = mt5.orders_get()
        for i in result:
            order_active.append(i.ticket)
        
        pos = mt5.positions_get()
        for i in pos :
            order_pos.append(i.ticket)


        print(len(order_active) + len(order_pos) , len(order_init))
        if  len(order_active) + len(order_pos) != len(order_init):
            new_pos = list(set(order_init) - set(order_active) - set(order_pos))
            for i in new_pos:
                
                print(i , dic_level[i].request.price)
                if dic_level[i].request.type == 3 or dic_level[i].request.type == 4:
        
                    if mt5.symbol_info_tick(symbol).ask < dic_level[i].request.price :
                        if dic_level[i].request.type == 3:
                            pos = sell_limit(symbol , vol , dic_level[i].request.tp ,0 ,0 , dic_level[i].request.price)
                            dic_level[pos.order] = pos
                            dic_level.pop(i , 'none')
                            break
                        elif dic_level[i].request.type == 4:
                            pos = buy_stop(symbol , vol , dic_level[i].request.tp ,0 ,0 , dic_level[i].request.price)
                            dic_level[pos.order] = pos
                            dic_level.pop(i , 'none')
                            break

                        else:
                            print('error in line 436')

                    elif mt5.symbol_info_tick(symbol).ask > dic_level[i].request.price :
                        if dic_level[i].request.type == 3:
                            pos = sell_stop(symbol , vol , dic_level[i].request.tp ,0 ,0 , dic_level[i].request.price)
                            dic_level[pos.order] = pos
                            dic_level.pop(i , 'none')
                            break
                        elif dic_level[i].request.type == 4:
                            pos = buy_limit(symbol , vol , dic_level[i].request.tp ,0 ,0 , dic_level[i].request.price)
                            dic_level[pos.order] = pos
                            dic_level.pop(i , 'none')
                            break

                        else:
                            print('error in line 445')

                elif dic_level[i].request.type == 2 or dic_level[i].request.type == 5 :
                    if mt5.symbol_info_tick(symbol).ask < dic_level[i].request.price :
                        if dic_level[i].request.type == 2:
                            pos = buy_stop(symbol , vol , dic_level[i].request.tp ,0 ,0 , dic_level[i].request.price)
                            dic_level[pos.order] = pos
                            dic_level.pop(i , 'none')
                            break
                        elif dic_level[i].request.type == 5:
                            pos = sell_limit(symbol , vol , dic_level[i].request.tp ,0 ,0 , dic_level[i].request.price)
                            dic_level[pos.order] = pos
                            dic_level.pop(i , 'none')
                            break

                        else:
                            print('error in line 455')

                    elif mt5.symbol_info_tick(symbol).ask > dic_level[i].request.price :
                        if dic_level[i].request.type == 2:
                            pos = buy_limit(symbol , vol , dic_level[i].request.tp ,0 ,0 , dic_level[i].request.price)
                            dic_level[pos.order] = pos
                            dic_level.pop(i , 'none')
                            break
                        elif dic_level[i].request.type == 5:
                            pos = sell_stop(symbol , vol , dic_level[i].request.tp ,0 ,0 , dic_level[i].request.price)
                            dic_level[pos.order] = pos
                            dic_level.pop(i , 'none')
                            break

                        else:
                            print('error in line 464')

               

        





init()

trade('GBPUSD_o' , 0.00025 , 0.1)

            
                



