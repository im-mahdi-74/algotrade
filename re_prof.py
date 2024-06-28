import MetaTrader5 as mt5
import pandas as pd 
import threading as th
import time
import datetime

import math
import pytz
import numpy as np

import subprocess
import json
import os


import MetaTrader5 as mt5
import pandas as pd 
import threading as th
import time
import datetime

import math
import pytz
import numpy as np

import subprocess
import json
import os





tehran_timezone = pytz.timezone('Asia/Tehran')

class Main():

    df_pross = pd.DataFrame(columns= ['time' ,  'pros' , 'sum_trade' , 'balance'])

    def __init__(self):

        self.init()

        self.symbol = {}


    def round_up( self , number, precision):

        return math.ceil(number * (10**precision)) / (10**precision)


    def init( self  ):
        # mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 real\terminal64.exe")
        # mt5.login(6910350 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Live')
        mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 3\terminal64.exe")
        mt5.login(89373537 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Demo')


    def info( self  ):

        account_info=mt5.account_info()

        balance = account_info.balance
        equity  = account_info.equity
        profit  = account_info.profit
        
        return balance , equity , profit
        

    def symbol_info( self , symbol):
        dic_symbol_info = {}
        group_symbols=mt5.symbols_get(group='*USD*')
        for s in group_symbols:
            if s.name == symbol : 
                dic_symbol_info[s.name] =  s.ask , s.bid
                
        return dic_symbol_info  # برمیگرداند یک دیکشنری که کلدی ها نماد و در ولیو ها اسک و بید به صورت تاپل 


    def get_data( self , symbol, timeframe, n=110):
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert(tehran_timezone)
        df['time'] = df['time'].dt.tz_localize(None)
        df.set_index('time', inplace=True)
        return df


    def buy( self , symbol , lot , tp_ , sl_  , price):

        
        
        tp = abs(  mt5.symbol_info_tick(symbol).ask + tp_ ) 
        sl = abs(  mt5.symbol_info_tick(symbol).ask  - sl_ ) 
        pos = mt5.ORDER_TYPE_BUY



        lot = self.round_up(lot, 2)
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
            self.symbol[symbol] = result.price
            return result.order , True
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


    def sell( self , symbol , lot , tp_ , sl_  , price):

        
        
        tp = abs(  mt5.symbol_info_tick(symbol).ask  - tp_  ) 
        sl = abs(  mt5.symbol_info_tick(symbol).ask  + sl_   ) 
        # tp = abs(mt5.symbol_info_tick(symbol).ask - tp_ -  (tp_ / 2 ) ) 
        # sl = abs(mt5.symbol_info_tick(symbol).bid + sl_ - ( tp_ / 2) ) 
        pos = mt5.ORDER_TYPE_SELL



        lot = self.round_up(lot, 2)
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
            self.symbol[symbol] = result.price
            return result.order , True
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


    def sell_stop( self , symbol , lot , tp_ , sl_ , reward , price):
        
        
        tp = abs(  self.symbol[symbol]  - tp_ - reward ) 
        sl = abs(  self.symbol[symbol]  ) 
        pos = mt5.ORDER_TYPE_SELL_STOP







        lot = self.round_up(lot, 2)
        point = mt5.symbol_info(symbol).point
        price =   self.symbol[symbol]  - ( sl_)
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


    def buy_stop( self , symbol , lot , tp_ , sl_  , reward , price):
        
        tp = abs(  self.symbol[symbol]  + tp_ + reward) 
        sl = abs(  self.symbol[symbol]   ) 
        pos = mt5.ORDER_TYPE_BUY_STOP
        







        lot = self.round_up(lot, 2)
        point = mt5.symbol_info(symbol).point
        price =   self.symbol[symbol]  + ( sl_)
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


    def trade( self , symbol , lot , tp , sl , reward , price  ):

        order_buy , buy = self.buy(symbol , lot , tp , sl , price)
        order_sell , sell = self.sell(symbol , lot , tp , sl , price)

        while True:
            time.sleep(0.1)
            try: 

                if buy and sell :
                    if mt5.positions_get(ticket = order_buy)[0].profit < -10 :
                        self.close(order_buy)
                        while True:
                            if mt5.positions_get(ticket = order_sell)[0].profit >= 25 or mt5.positions_get(ticket = order_sell)[0].profit <= 0 :
                                self.close(order_sell)
                                break
                            time.sleep(0.1)
                        

                    if mt5.positions_get(ticket = order_sell)[0].profit < -10 :
                        self.close(order_sell)
                        while True:
                            if mt5.positions_get(ticket = order_buy)[0].profit >= 25 or mt5.positions_get(ticket = order_buy)[0].profit <= 0 :
                                self.close(order_buy)
                                break
                            time.sleep(0.1)

                    if len(mt5.positions_get()) == 0 :
                        break






                else:
                    break

            except Exception as e:
                print(f'Error in trade {e}')           
                break


    def close( self , order):
        
        
        
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
            
            if position.ticket == order :
                try:
                    
                    doit =  close_position(position)
                    time.sleep(0.1)

                except Exception as e:
                    print(f'Clsoe : Eror for Clsoe {e}')
                time.sleep(0.05)


    def order_close( self , symbol):
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


    def run(self):
        while True:
            

            if len(mt5.positions_get(symbol = 'GBPUSD_o')) == 0 :
                th.Thread(target = self.trade , args = ('GBPUSD_o' , 1 , 0.0050 , 0.0050 , 0.001 , 1.39)).start()
                continue

            time.sleep(5)
            

            if len(mt5.positions_get(symbol = 'USDJPY_o')) == 0 :
                th.Thread(target = self.trade , args = ('USDJPY_o' , 1 , 0.50 , 0.50 , 0.001 , 109.5)).start()
                continue




            
if __name__ == "__main__":

    go = Main()
    go.run()
    