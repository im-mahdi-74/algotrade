

import MetaTrader5 as mt5
import pandas as pd 
import threading as th
import time
import datetime

import math
import pytz
import numpy as np

print('run')


tehran_timezone = pytz.timezone('Asia/Tehran')

df_pross = pd.DataFrame(columns= ['time' ,  'pros' , 'sum_trade' , 'balance'])

def round_up(number, precision):

  return math.ceil(number * (10**precision)) / (10**precision)


def init():
    # mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 real\terminal64.exe")
    # mt5.login(6920086 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Live')

    init = mt5.initialize(path=r"C:\Program Files\Propridge Capital Markets MT5 Terminal\terminal64.exe")
    mt5.login(149613, password='@Dtj$67F' ,  server='PropridgeCapitalMarkets-Server')


def info():

    account_info=mt5.account_info()

    balance = account_info.balance
    equity  = account_info.equity
    profit  = account_info.profit
    
    return balance , equity , profit
    

def round_up(number, precision):

  return math.ceil(number * (10**precision)) / (10**precision)


def buy(symbol , lot , tp_ , sl_ , comment ):

    
    # point = mt5.symbol_info(symbol).point
    # tp = abs(mt5.symbol_info_tick(symbol).ask + (tp_  * point) ) 
    # sl = abs(mt5.symbol_info_tick(symbol).bid - sl_ ) 
    pos = mt5.ORDER_TYPE_BUY



    lot = round_up(lot, 2)
    
    price = mt5.symbol_info_tick(symbol).bid
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
        "type_filling": mt5.ORDER_FILLING_IOC ,
    }
     
    # send a trading request
    result = mt5.order_send(request)
    print(result)
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

    
    # point = mt5.symbol_info(symbol).point
    # tp = abs(mt5.symbol_info_tick(symbol).bid - (tp_ * point)  ) 
    sl = abs(mt5.symbol_info_tick(symbol).bid + sl_   ) 
    # tp = abs(mt5.symbol_info_tick(symbol).ask - tp_ -  (tp_ / 2 ) ) 
    # sl = abs(mt5.symbol_info_tick(symbol).bid + sl_ - ( tp_ / 2) ) 
    pos = mt5.ORDER_TYPE_SELL



    lot = round_up(lot, 2)
    
    price = mt5.symbol_info_tick(symbol).bid
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
        "type_filling": mt5.ORDER_FILLING_IOC ,
    }
     
    # send a trading request
    result = mt5.order_send(request)
    print(result)
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
                "type_filling": mt5.ORDER_FILLING_IOC ,
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
                return doit

            except Exception as e:
                print(f'Clsoe : Eror for Clsoe {e}')


def close_(ticket , volume , comment):
    comment = str(comment)
    # volume = round(volume , 2)
    
    def close_position(position , volume , comment):
        try:
            tick = mt5.symbol_info_tick(position.symbol)

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": position.ticket,
                "symbol": position.symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
                "price": tick.ask if position.type == 1 else tick.bid,  
                "deviation": 100,
                "magic": 234002,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC ,
            }

            result = mt5.order_send(request)
            # if result.retcode != mt5.TRADE_RETCODE_DONE:
            #     result ("Close failed . order_send failed, retcode={} {}".format(result.retcode ,request ))
            #     return False
            print(result , request)
        except Exception as e:
            print(f'Close : Eror in def close 219 {e}')

    positions = mt5.positions_get()
    for position in positions:
        # print(position)
        
        if position.ticket == ticket :
            try:
                
                close_position(position , volume , comment)
                return 'clsoe'
                time.sleep(0.1)

            except Exception as e:
                print(f'Clsoe : Eror for Clsoe 233 {e}')
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


def close_nith():
    while True:
        time.sleep(0.2)
        try :
            dic_tick = {}
            jam = 0
            
            positions = mt5.positions_get()
            for position in positions:
                # print(position)
                
                dic_tick[position.ticket] = position.profit
                jam = jam + position.profit
            print('nith close' , jam)
            if jam >= 0 :
                for i in dic_tick:
                    time.sleep(0.2)
                    close(i)
                    break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


def sod_sang(buy , sell):


    bar = 1
    sod = 2.5
    exit = False

    print(291)
    while True:
        time.sleep(0.2)
        sod = sod / bar
        try :

            if mt5.positions_get(ticket = buy.order)[0].profit >= sod :
                close_(buy.order , 0.2 , 'SERVER ALI TEST')
                while True :
                    time.sleep(0.02)

                    if mt5.positions_get(ticket = sell.order) == None :
                        exit = True
                        break

                    if mt5.positions_get(ticket = sell.order)[0].profit >= 0 :
                        close_(sell.order , 0.2 , 'SERVER ALI TEST')
                        bar += 1
                        break





            if exit :
                break
            
            if mt5.positions_get(ticket = sell.order)[0].profit >= sod :
                close_(sell.order , 0.2 , 'SERVER ALI TEST')
                while True :
                    time.sleep(0.02)


                    if mt5.positions_get(ticket = buy.order) == None :
                        exit = True
                        break

                    if mt5.positions_get(ticket = buy.order)[0].profit >= 0 :
                        close_(buy.order , 0.2 , 'SERVER ALI TEST')
                        bar += 1
                        break




            if exit :
                break



        

        except Exception as e :
            print(e , '333')


def sod_sang_(buy , sell):


    bar = 1
    sod = -2.5
    exit = False

    print(291)
    while True:
        time.sleep(0.2)
        sod = sod / bar
        try :

            if mt5.account_info().profit >= 20 :
                break

            if mt5.positions_get(ticket = buy.order)[0].profit <= sod :
                close_(buy.order , 0.2 , 'SERVER ALI TEST')
                while True :
                    time.sleep(0.02)
                    if mt5.positions_get(ticket = sell.order) == None :
                        close(sell.order )
                        exit = True
                        break

                    if mt5.positions_get(ticket = sell.order)[0].profit >= 2.5 :
                        close_(sell.order , 0.2 , 'SERVER ALI TEST')
                        bar += 1
                        break
                if exit :
                    break
            
            if mt5.positions_get(ticket = sell.order)[0].profit <= sod :
                close_(sell.order , 0.2 , 'SERVER ALI TEST')
                while True :
                    time.sleep(0.02)
                    if mt5.positions_get(ticket = buy.order) == None :
                        close(buy.order )
                        exit = True
                        break

                    if mt5.positions_get(ticket = buy.order)[0].profit >= 2.5 :
                        close_(buy.order , 0.2 , 'SERVER ALI TEST')
                        bar += 1
                        break
                if exit :
                    break



        

        except Exception as e :
            print(e , '333')


def trade():

    # buy_ = buy('US30' , 0.1 , 100 , 100 , 'TEST SERVER ALI')
    # sell_ = sell('US30' , 0.1 , 0 , 0 , 'TEST SERVER ALI')
    # th.Thread(target = sod_sang , args=(buy_ , sell_))
    # sod_sang(buy_ , sell_)
    # time.sleep(5)

    while True:

        if len(mt5.positions_get()) < 25 :
            print(len(mt5.positions_get()) )
        
            buy_ = buy('US30' , 1 , 100 , 100 , 'TEST SERVER ALI')
            sell_ = sell('US30' , 1 , 0 , 0 , 'TEST SERVER ALI')
            th.Thread(target = sod_sang , args=(buy_ , sell_)).start()
            time.sleep(60)

init()

trade()






