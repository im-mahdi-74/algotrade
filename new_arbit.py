
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
    # mt5.login(6910350 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Live')
    # mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 real 2\terminal64.exe")
    # mt5.login(6920086 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Live')
    mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 3\terminal64.exe")
    mt5.login(89373537 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Demo')

def info():

    account_info=mt5.account_info()

    balance = account_info.balance
    equity  = account_info.equity
    profit  = account_info.profit
    
    return balance , equity , profit
    
def round_up(number, precision):

  return math.ceil(number * (10**precision)) / (10**precision)


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
                return doit
                time.sleep(0.1)

            except Exception as e:
                print(f'Clsoe : Eror for Clsoe {e}')
            time.sleep(0.05)


def close_(ticket , volume , comment):
    comment = str(comment)
    volume = round(volume , 2)
    
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
                "type_filling": mt5.ORDER_FILLING_FOK ,
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



def close_pos(tickit_one_one, tickit_one_tow, tickit_tow_one, tickit_tow_tow ):
    sod = 5
    zar = -5

    level_close = 10

    while True:
        time.sleep(0.25)
        
        positions_one_one = mt5.positions_get(ticket=tickit_one_one.order)
        positions_one_tow = mt5.positions_get(ticket=tickit_one_tow.order)
        positions_tow_one = mt5.positions_get(ticket=tickit_tow_one.order)
        positions_tow_tow = mt5.positions_get(ticket=tickit_tow_tow.order)

        if not positions_one_one or not positions_one_tow or not positions_tow_one or not positions_tow_tow:
            return True
            break
        

        balance_kol = positions_one_one[0].profit + positions_one_tow[0].profit + positions_tow_one[0].profit + positions_tow_tow[0].profit
        balance_one = positions_one_one[0].profit + positions_one_tow[0].profit
        balance_tow = positions_tow_one[0].profit + positions_tow_tow[0].profit

        print(balance_kol , balance_one , balance_tow)

        if positions_one_one[0].volume <= 0.1 : 
            pass



        if balance_kol >= 0:
            for i in [tickit_one_one.order, tickit_one_tow.order, tickit_tow_one.order, tickit_tow_tow.order]:
                time.sleep(0.2)
                close(i)
                break
            break



        if balance_one >= sod :
            
                
            doit = close_( tickit_one_one.order, round_up(positions_one_one[0].volume / level_close , 2) , level_close)
             
            doit = close_( tickit_one_tow.order , round_up(positions_one_tow[0].volume / level_close , 2) , level_close)
             
            if positions_one_tow[0].volume <= 0.1:
                break


            while True:
                positions_tow_one = mt5.positions_get(ticket=tickit_tow_one.order)
                positions_tow_tow = mt5.positions_get(ticket=tickit_tow_tow.order)
                balance_tow_pass = positions_tow_one[0].profit + positions_tow_tow[0].profit

                if balance_tow_pass / level_close >= zar:
                    
                    doit = close_( tickit_tow_one.order, round_up(positions_tow_one[0].volume / level_close , 2) , level_close)
                     
                    doit = close_(tickit_tow_tow.order , round_up(positions_tow_tow[0].volume / level_close , 2) , level_close)
                     
                    level_close = level_close - 1
                    break
                    
            
            
            



        if balance_tow >= sod :
            

            doit = close_( tickit_tow_one.order , round_up(positions_tow_one[0].volume / level_close , 2) , level_close)
             
            doit = close_( tickit_tow_tow.order, round_up(positions_tow_tow[0].volume / level_close , 2) , level_close)
             
            if positions_tow_tow[0].volume <= 0.1:
                break

            while True:
                positions_one_one = mt5.positions_get(ticket=tickit_one_one.order)
                positions_one_tow = mt5.positions_get(ticket=tickit_one_tow.order)
                balance_one_pass = positions_one_one[0].profit + positions_one_tow[0].profit

                if balance_one_pass / level_close >= zar:
                    
                    doit = close_( tickit_one_one.order , round_up(positions_one_one[0].volume / level_close , 2) , level_close)
                     
                    doit = close_( tickit_one_tow.order , round_up(positions_one_tow[0].volume / level_close , 2) , level_close)
                     
                    level_close = level_close - 1
                    break
                    


def sod_sang(tickit_one_one, tickit_one_tow, tickit_tow_one, tickit_tow_tow):
    init_balance_one = True
    init_balance_tow = True
    pos = 'tow'
    init = False
    sum_trade = 0
    while True:
        time.sleep(0.3)
        now = datetime.datetime.now(tehran_timezone)
        if 0 < now.hour < 24  :
              
            if init_balance_one:
                positions_one_one = mt5.positions_get(ticket=tickit_one_one.order)
                positions_one_tow = mt5.positions_get(ticket=tickit_one_tow.order)
                if positions_one_one and positions_one_tow:
                    balance_one = positions_one_one[0].profit + positions_one_tow[0].profit
                    if balance_one > 40  or balance_one < 0 :
                        print(balance_one)
                    if balance_one > 300 and init_balance_one and pos == 'tow':
                        close(tickit_one_one.order)
                        time.sleep(0.1)
                        close(tickit_one_tow.order)
                        init_balance_one = False
                        pos = 'one'
                        tickit_one_one , tickit_one_tow = run_one()
                        close_pos(tickit_one_one, tickit_one_tow, tickit_tow_one, tickit_tow_tow)
                        break

                        


                    # if balance_one >= 0 and not init_balance_tow and init_balance_one:
                    #     tickit_tow_one, tickit_tow_tow = run_tow()
                    #     init_balance_tow = True
                    #     init = True
                    #     time.sleep(2)

            if init_balance_tow:
                positions_tow_one = mt5.positions_get(ticket=tickit_tow_one.order)
                positions_tow_tow = mt5.positions_get(ticket=tickit_tow_tow.order)
                if positions_tow_one and positions_tow_tow:
                    balance_tow = positions_tow_one[0].profit + positions_tow_tow[0].profit
                    if balance_tow > 40 or balance_tow < 0:
                        print(balance_tow)
                    if balance_tow > 300 and init_balance_tow and pos == 'tow' :
                        close(tickit_tow_one.order)
                        time.sleep(0.1)
                        close(tickit_tow_tow.order)
                        init_balance_tow = False
                        pos = 'one'
                        tickit_tow_one, tickit_tow_tow = run_tow()
                        close_pos(tickit_one_one, tickit_one_tow, tickit_tow_one, tickit_tow_tow)
                        break




                    # if balance_tow >= 0 and init_balance_tow and not init_balance_one:
                    #     tickit_one_one, tickit_one_tow = run_one()
                    #     init_balance_one = True
                    #     init = True
                    #     time.sleep(2)
        else:
            
            
            
            dic_tick = {}
            jam = 0
            
            positions = mt5.positions_get()
            for position in positions:
                # print(position)
                
                dic_tick[position.ticket] = position.profit
                jam = jam + position.profit
            print('else' ,  jam)
            if jam >= 0 :
                for i in dic_tick:
                    time.sleep(0.2)
                    close(i)
                    break


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

    
    now = datetime.datetime.now(tehran_timezone)
    if 0 < now.hour < 24   :
        try:

            if len(mt5.positions_get(symbol='GBPUSD_o')) == 0 and len(mt5.positions_get(symbol='EURUSD_o')) == 0 :
                tickit_one_one =  buy('GBPUSD_o', 2.6 , 0 , 0 , 'one')
                tickit_one_tow =  sell('EURUSD_o', 3 , 0 , 0 , 'one')
                tickit_tow_one =  sell('GBPUSD_o', 2.6 , 0 , 0 , 'tow')
                tickit_tow_tow =  buy('EURUSD_o', 3 , 0 , 0 , 'tow')

                return tickit_one_one , tickit_one_tow , tickit_tow_one , tickit_tow_tow
                
                
            # else:
            #     close_nith()
            #     break

            # if len(mt5.positions_get(symbol='GBPUSD_o')) == 0 and len(mt5.positions_get(symbol='EURUSD_o')) == 0:

            #     tickit_tow_one =  th.Thread(target=buy  , args=('GBPUSD_o', 1, 0 , 0 , 'tow')).start()
            #     tickit_tow_tow =  th.Thread(target=sell , args=('EURUSD_o', 1, 0 , 0 , 'tow' )).start()






        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)  # Wait for 1 minute before retrying

        


def main():

    while True:

        print(datetime.datetime.now(tehran_timezone))
        tickit_one_one , tickit_one_tow , tickit_tow_one , tickit_tow_tow = run()

        if tickit_one_one and tickit_one_tow and tickit_tow_one and tickit_tow_tow :
            

            sod_sang(tickit_one_one , tickit_one_tow , tickit_tow_one , tickit_tow_tow)
        time.sleep(60)


main()