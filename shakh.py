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
    mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 3\terminal64.exe")
    mt5.login(89373537 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Demo')


def info():

    account_info=mt5.account_info()

    balance = account_info.balance
    equity  = account_info.equity
    profit  = account_info.profit
    
    return balance , equity , profit
    


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


def sod_sang(tickit_one, tickit_tow, tickit_tree , tickit_for , tickit_five , tickit_one_ , tickit_tow_ , tickit_tree_ , tickit_for_ , tickit_five_):

    while True:
        time.sleep(0.1)
        now = datetime.datetime.now(tehran_timezone)
        if 8 < now.hour < 21  or len(mt5.positions_get())  > 0 :
            
            list_one = [tickit_one , tickit_tow , tickit_tree , tickit_for , tickit_five]
            list_tow = [tickit_one_ , tickit_tow_ , tickit_tree_ , tickit_for_ , tickit_five_]
            
            positions_one_one = mt5.positions_get(ticket=tickit_one.order)
            positions_one_tow = mt5.positions_get(ticket=tickit_tow.order)
            positions_one_tree = mt5.positions_get(ticket=tickit_tree.order)
            positions_one_for = mt5.positions_get(ticket=tickit_for.order)
            positions_one_five = mt5.positions_get(ticket=tickit_five.order)

            positions_one_one_ = mt5.positions_get(ticket=tickit_one_.order)
            positions_one_tow_ = mt5.positions_get(ticket=tickit_tow_.order)
            positions_one_tree_ = mt5.positions_get(ticket=tickit_tree_.order)
            positions_one_for_ = mt5.positions_get(ticket=tickit_for_.order)
            positions_one_five_ = mt5.positions_get(ticket=tickit_five_.order)


            if positions_one_one and positions_one_tow and positions_one_tree and positions_one_for and positions_one_five and positions_one_one_ and positions_one_tow_ and positions_one_tree_ and positions_one_for_ and positions_one_five_:
                balance_one = positions_one_one[0].profit + positions_one_tow[0].profit + positions_one_tree[0].profit + positions_one_for[0].profit + positions_one_five[0].profit 
                balance_tow = positions_one_one_[0].profit + positions_one_tow_[0].profit + positions_one_tree_[0].profit + positions_one_for_[0].profit + positions_one_five_[0].profit
                if balance_one > 0 :
                    print(balance_one)
                if balance_one > 20 :
                    for i in list_one:
                        close(i.order)
                        time.sleep(0.1)
                    tickit_one ,  tickit_tow , tickit_tree , tickit_for , tickit_five = run_one()
                    continue


                if balance_tow > 0 :
                    print(balance_tow)
                if balance_tow > 20 :
                    for i in list_tow:
                        close(i.order)
                        time.sleep(0.1)
                    tickit_one ,  tickit_tow , tickit_tree , tickit_for , tickit_five = run_tow()
                    continue



def run_one():

    tickit_one =  buy('GBPUSD_o', 0.78 , 0 , 0 , 'one')
    tickit_tow =  buy('EURUSD_o', 0.92 , 0 , 0 , 'one')
    tickit_tree =  sell('USDJPY_o', 1 , 0 , 0 , 'tow')
    tickit_for =  sell('USDCAD_o', 1.25 , 0 , 0 , 'one')
    tickit_five =  sell('USDCHF_o', 0.92 , 0 , 0 , 'one')

    return tickit_one , tickit_tow , tickit_tree , tickit_for , tickit_five


def run_tow():
    
    tickit_one_ =  sell('GBPUSD_o', 0.78 , 0 , 0 , 'one')
    tickit_tow_ =  sell('EURUSD_o', 0.92 , 0 , 0 , 'one')
    tickit_tree_ =  buy('USDJPY_o', 1 , 0 , 0 , 'tow')
    tickit_for_ =  buy('USDCAD_o', 1.25 , 0 , 0 , 'one')
    tickit_five_ =  buy('USDCHF_o', 0.92 , 0 , 0 , 'one')


    return  tickit_one_ , tickit_tow_ , tickit_tree_ , tickit_for_ , tickit_five_


def run():
    init()
    while True:
        now = datetime.datetime.now(tehran_timezone)
        if 8 < now.hour < 24  :
            try:

                if len(mt5.positions_get(symbol='GBPUSD_o')) == 0 and len(mt5.positions_get(symbol='EURUSD_o')) == 0:
                    tickit_one =  buy('GBPUSD_o', 0.78 , 0 , 0 , 'one')
                    tickit_one_ =  sell('GBPUSD_o', 0.78 , 0 , 0 , 'one')
                    # time.sleep(0.1)
                    tickit_tow =  buy('EURUSD_o', 0.92 , 0 , 0 , 'one')
                    tickit_tow_ =  sell('EURUSD_o', 0.92 , 0 , 0 , 'one')
                    # time.sleep(0.1)
                    tickit_tree =  sell('USDJPY_o', 1 , 0 , 0 , 'tow')
                    tickit_tree_ =  buy('USDJPY_o', 1 , 0 , 0 , 'tow')
                    # time.sleep(0.1)
                    tickit_for =  sell('USDCAD_o', 1.25 , 0 , 0 , 'one')
                    tickit_for_ =  buy('USDCAD_o', 1.25 , 0 , 0 , 'one')
                    # time.sleep(0.1)
                    tickit_five =  sell('USDCHF_o', 0.92 , 0 , 0 , 'one')
                    tickit_five_ =  buy('USDCHF_o', 0.92 , 0 , 0 , 'one')



                    return tickit_one , tickit_tow , tickit_tree , tickit_for , tickit_five , tickit_one_ , tickit_tow_ , tickit_tree_ , tickit_for_ , tickit_five_
                else:
                    pass

                # if len(mt5.positions_get(symbol='GBPUSD_o')) == 0 and len(mt5.positions_get(symbol='EURUSD_o')) == 0:

                #     tickit_tow_one =  th.Thread(target=buy  , args=('GBPUSD_o', 1, 0 , 0 , 'tow')).start()
                #     tickit_tow_tow =  th.Thread(target=sell , args=('EURUSD_o', 1, 0 , 0 , 'tow' )).start()






            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)  # Wait for 1 minute before retrying

        time.sleep(60)  # Wait for 1 minute before retrying






print(datetime.datetime.now(tehran_timezone))
tickit_one , tickit_tow , tickit_tree , tickit_for , tickit_five , tickit_one_ ,  tickit_tow_ , tickit_tree_ , tickit_for_ , tickit_five_ = run()

if tickit_one and tickit_tow and tickit_tree and tickit_for and tickit_five and tickit_one_ and tickit_tow_ and tickit_tree_ and tickit_for_ and tickit_five_:
    sod_sang(tickit_one , tickit_tow , tickit_tree , tickit_for , tickit_five , tickit_one_ , tickit_tow_ , tickit_tree_ , tickit_for_ , tickit_five_) 
