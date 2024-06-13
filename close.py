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
    mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 3\terminal64.exe")
    mt5.login(89373537 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Demo')
    # mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 real 2\terminal64.exe")
    # mt5.login(6920086 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Live')



def close_():
    
    
    
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
        
        
        try:
            
            doit =  close_position(position)
            time.sleep(0.1)

        except Exception as e:
            print(f'Clsoe : Eror for Clsoe {e}')
        time.sleep(0.05)


def close(ticket , volume):
    
    
    
    def close_position(position , volume):
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
                
                doit =  close_position(position , volume)
                time.sleep(0.1)

            except Exception as e:
                print(f'Clsoe : Eror for Clsoe {e}')
            time.sleep(0.05)

def sod_sang():

    while True:
        init()
        time.sleep(0.5)
        
        dic_tick = {}
        jam = 0
        
        positions = mt5.positions_get()
        for position in positions:
            # print(position)
            
            dic_tick[position.ticket] = position.profit
            jam = jam + position.profit
        print(jam)
        if jam >= 0 :
            for i in dic_tick:
                time.sleep(0.2)
                close(i)
                break

def sod_sang_():
    

    while True:
        init()
        time.sleep(0.2)
        
        dic_tick = {}
        
        
        # positions = mt5.positions_get()
        # for position in positions:
        #     # print(position)
            
        #     dic_tick[position.ticket] = position.profit
        #     jam = jam + position.profit
        # los = []
        # for tic in mt5.positions_get():
        #     los.append(tic.ticket)
        
        las = [5120201175 , 5120202270]
        if len(los) > 0 : 
            jom = mt5.positions_get(ticket = 5120277670)[0].profit + mt5.positions_get(ticket = 5120277674)[0].profit
            print(';           ')
            
        #     print(jom)            
        # print(mt5.account_info().equity - mt5.account_info().balance )
        # if mt5.account_info().equity - mt5.account_info().balance < -250 :
            
            # time.sleep(0.2)
            # close()
            # continue
        # if mt5.positions_get(ticket = 5120201175) != None:
        #     jon = mt5.positions_get(ticket = 5120201175)[0].profit + mt5.positions_get(ticket = 5120201170)[0].profit
        #     print(jon)
        #     if jon >= 200 :
        #         for i in las:
        #             time.sleep(0.2)
        #             close(i)
        #             continue


def close_nith():
    level_sod = 0
    level_zar = 0
    while True:
        time.sleep(0.2)
        try :
            dic_tick = {}
            jam = 0
            dic_sod = {}
            
            positions = mt5.positions_get()
            for position in positions:
                # print(position)
                
                dic_tick[position.ticket] = position.profit , position.volume

                if position.profit > (position.volume * 15) :

                        level_sod = position.profit / 10
                        close(position.ticket , round_up(position.volume / 10 , 2) ) 


                if position.profit < (position.volume * -10) :

                    if  abs(position.profit / 10) >= level_sod:
                        level_zar = position.profit / 10
                        close(position.ticket , round_up(position.volume / 10 , 2) )
                        
                

            
            print('nith close' ,level_sod)




                # jam = jam + position.profit\
        #     if jam >= 10 :
        #         for i in dic_tick:
        #             time.sleep(0.2)
        #             close(i)
        #             break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)       





        
        

init()

close_nith()







