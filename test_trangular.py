

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

    # init = mt5.initialize(path=r"C:\Program Files\LiteFinance MT5 2\terminal64.exe")
    # mt5.login(89373537, password='Mahdi1400@', server='LiteFinance-MT5-Demo')

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

    
    
    tp = abs(mt5.symbol_info_tick(symbol).bid + tp_ ) 
    sl = abs(mt5.symbol_info_tick(symbol).ask - sl_ ) 
    pos = mt5.ORDER_TYPE_BUY



    lot = round_up(lot, 2)
    point = mt5.symbol_info(symbol).point
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
        "type_filling": mt5.ORDER_FILLING_FOK ,
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

    
    
    tp = abs(mt5.symbol_info_tick(symbol).ask - tp_  ) 
    sl = abs(mt5.symbol_info_tick(symbol).bid + sl_   ) 
    # tp = abs(mt5.symbol_info_tick(symbol).ask - tp_ -  (tp_ / 2 ) ) 
    # sl = abs(mt5.symbol_info_tick(symbol).bid + sl_ - ( tp_ / 2) ) 
    pos = mt5.ORDER_TYPE_SELL



    lot = round_up(lot, 2)
    point = mt5.symbol_info(symbol).point
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
        "type_filling": mt5.ORDER_FILLING_FOK ,
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

            except Exception as e:
                print(f'Clsoe : Eror for Clsoe {e}')


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


def tradeone():
    # while True:
        try:
            # if len(mt5.positions_get()) == 0 :

                one_eur = buy('EURGBP_o' , 0.01 , 0.05 , 0.05 , 'one')            
              
                one_gbp = buy('GBPUSD_o' , 0.01 , 0.05 , 0.05 , 'one')

                one_eur_gbp = sell('EURUSD_o' , 0.01 , 0.05 , 0.05 , 'one')




                return one_gbp , one_eur_gbp , one_eur 
        except Exception as e:
            print(f"Error: {e}")


def tradetow():
        try:
            # if len(mt5.positions_get()) == 0 :
       
                tow_eur_gbp = sell('EURGBP_o' , 0.01 , 0.05 , 0.05 , 'tow')
              
                tow_gbp = sell('GBPUSD_o' , 0.01 , 0.05 , 0.05 , 'tow')

                tow_eur = buy('EURUSD_o' , 0.01 , 0.05 , 0.05 , 'tow')




                return  tow_gbp , tow_eur ,  tow_eur_gbp
        except Exception as e:
            print(f"Error: {e}")


def profit(one_gbp , tow_gbp , tow_eur , one_eur_gbp , one_eur , tow_eur_gbp):

    while True:
        try:
            time.sleep(0.01)
            if len(mt5.positions_get(one_gbp.order)) == 0 and len(mt5.positions_get(one_eur.order)) == 0 and len(mt5.positions_get(one_eur_gbp.order)) == 0 :
                one_gbp ,  one_eur_gbp  , one_eur  = tradeone()
            else:
                profit_one = mt5.positions_get( ticket =  one_gbp.order)[0].profit + mt5.positions_get( ticket =  one_eur.order)[0].profit + mt5.positions_get( ticket =  one_eur_gbp.order)[0].profit
                if profit_one >= 4 :
                    close(one_gbp.order)
                    close(one_eur.order)
                    close(one_eur_gbp.order)
                    break

            if len(mt5.positions_get(tow_gbp.order)) == 0 and len(mt5.positions_get(tow_eur.order)) == 0 and len(mt5.positions_get(tow_eur_gbp.order)) == 0 :
                tow_gbp ,  tow_eur      , tow_eur_gbp   = tradetow()
            else:
                profit_tow = mt5.positions_get( ticket =  tow_gbp.order)[0].profit + mt5.positions_get( ticket =  tow_eur.order)[0].profit + mt5.positions_get( ticket =  tow_eur_gbp.order)[0].profit
                if profit_tow >= 4 :
                    close(tow_gbp.order)
                    close(tow_eur.order)
                    close(tow_eur_gbp.order)
                    break

            



        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


def write_to_csv(filename, data):
    df = pd.DataFrame(data, columns=['time', 'sod_eur_buy', 'sod_eur_sell', 'sod_jpy_buy', 'sod_jpy_sell', 'sod_aud_buy', 'sod_aud_sell', 'sod_gbp_buy', 'sod_gbp_sell', 'sod_chf_buy', 'sod_chf_sell', 'sod_cad_buy', 'sod_cad_sell'])
    try:
        existing_df = pd.read_csv(filename)
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_csv(filename, index=False)



def write_to(filename, data):
    df = pd.DataFrame(data, columns=['time', 'sod_eur_buy', 'sod_eur_sell', 'sod_jpy_buy', 'sod_jpy_sell', 'sod_aud_buy', 'sod_aud_sell', 'sod_gbp_buy', 'sod_gbp_sell', 'sod_chf_buy', 'sod_chf_sell', 'sod_cad_buy', 'sod_cad_sell', 'sod_eur_cad_buy', 'sod_eur_cad_sell', 'sod_eur_aud_buy', 'sod_eur_aud_sell' ])
    try:
        existing_df = pd.read_csv(filename)
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_csv(filename, index=False)


def profit_tow(one_gbp , tow_gbp , tow_eur , one_eur_gbp , one_eur , tow_eur_gbp):

    while True:
        try:

            
            profit_one = mt5.positions_get( ticket =  one_gbp.order)[0].profit + mt5.positions_get( ticket =  one_eur.order)[0].profit + mt5.positions_get( ticket =  one_eur_gbp.order)[0].profit
            profit_tow = mt5.positions_get( ticket =  tow_gbp.order)[0].profit + mt5.positions_get( ticket =  tow_eur.order)[0].profit + mt5.positions_get( ticket =  tow_eur_gbp.order)[0].profit

            
            data = [[datetime.datetime.now(), profit_one, profit_tow]]
            write_to_csv('trade_arbit.csv', data)



        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

init()

# one_gbp ,  one_eur_gbp  , one_eur       = tradeone()
# tow_gbp ,  tow_eur      , tow_eur_gbp   = tradetow()

# profit_tow(one_gbp , tow_gbp , tow_eur , one_eur_gbp , one_eur , tow_eur_gbp)



def test__():


    init_eur = mt5.symbol_info("EURUSD").ask
    init_gbp = mt5.symbol_info("GBPUSD").bid
    init_eur_gbp = mt5.symbol_info("EURGBP").bid

    init_jpy = mt5.symbol_info("USDJPY").ask
    init_eur_jpy = mt5.symbol_info("EURJPY").ask

    init_aud = mt5.symbol_info("AUDUSD").ask
    init_nzd = mt5.symbol_info("NZDUSD").ask
    init_aud_nzd = mt5.symbol_info("AUDNZD").bid

    init_gbp_jpy = mt5.symbol_info("GBPJPY").ask

    init_chf = mt5.symbol_info("USDCHF").ask
    init_eur_chf = mt5.symbol_info("EURCHF").ask

    init_cad = mt5.symbol_info("USDCAD").ask
    init_cad_jpy = mt5.symbol_info("CADJPY").ask

    init_eur_cad = mt5.symbol_info("EURCAD").ask
    init_eur_aud = mt5.symbol_info("EURAUD").ask
    init_eur_nzd = mt5.symbol_info("EURNZD").ask








    print(init_eur , init_gbp , init_eur_gbp)

    while True:
        try:
            time.sleep(0.01)

            volume_eurusd = 100_000 / mt5.symbol_info("EURUSD").ask
            volume_gbpusd = 100_000 / mt5.symbol_info("GBPUSD").ask
            volume_eurgbp = 100_000 / mt5.symbol_info("EURGBP").ask
            volume_usdjpy = 100_000 / mt5.symbol_info("USDJPY").ask
            volume_eurjpy = 100_000 / mt5.symbol_info("EURJPY").ask
            volume_audusd = 100_000 / mt5.symbol_info("AUDUSD").ask
            volume_nzdusd = 100_000 / mt5.symbol_info("NZDUSD").ask
            volume_audnzd = 100_000 / mt5.symbol_info("AUDNZD").ask
            volume_gbpjpy = 100_000 / mt5.symbol_info("GBPJPY").ask
            volume_usdchf = 100_000 / mt5.symbol_info("USDCHF").ask
            volume_eurchf = 100_000 / mt5.symbol_info("EURCHF").ask
            volume_usdcad = 100_000 / mt5.symbol_info("USDCAD").ask
            volume_cadjpy = 100_000 / mt5.symbol_info("CADJPY").ask
            volume_eurcad = 100_000 / mt5.symbol_info("EURCAD").ask
            volume_euraud = 100_000 / mt5.symbol_info("EURAUD").ask
            volume_eurnzd = 100_000 / mt5.symbol_info("EURNZD").ask

            # sod_eur_buy = (init_eur - mt5.symbol_info("EURUSD").ask) * 100_000 + (mt5.symbol_info("GBPUSD").bid - init_gbp) * 85_000 + (mt5.symbol_info("EURGBP").bid - init_eur_gbp) * 100_000 

            sod_eur_buy =  volume_eurusd * (init_eur - mt5.symbol_info("EURUSD").bid) + volume_gbpusd * (mt5.symbol_info("GBPUSD").ask - init_gbp) + volume_eurgbp * (mt5.symbol_info("EURGBP").ask - init_eur_gbp)
            sod_eur_sell = volume_eurusd * (mt5.symbol_info("EURUSD").ask - init_eur) + volume_gbpusd * (init_gbp - mt5.symbol_info("GBPUSD").bid) + volume_eurgbp * (init_eur_gbp - mt5.symbol_info("EURGBP").bid)

            sod_jpy_buy = volume_usdjpy * (mt5.symbol_info("USDJPY").ask - init_jpy) + volume_eurjpy * (init_eur_jpy - mt5.symbol_info("EURJPY").bid) + volume_eurusd * (mt5.symbol_info("EURUSD").ask - init_eur)
            sod_jpy_sell = volume_usdjpy * (init_jpy - mt5.symbol_info("USDJPY").bid) + volume_eurjpy * (mt5.symbol_info("EURJPY").ask - init_eur_jpy) + volume_eurusd * (init_eur - mt5.symbol_info("EURUSD").bid)

            sod_aud_buy = volume_audusd * (init_aud - mt5.symbol_info("AUDUSD").bid) + volume_nzdusd * (mt5.symbol_info("NZDUSD").ask - init_nzd) + volume_audnzd * (mt5.symbol_info("AUDNZD").ask - init_aud_nzd)
            sod_aud_sell = volume_audusd * (mt5.symbol_info("AUDUSD").ask - init_aud) + volume_nzdusd * (init_nzd - mt5.symbol_info("NZDUSD").bid) + volume_audnzd * (init_aud_nzd - mt5.symbol_info("AUDNZD").bid)

            sod_gbp_buy = volume_gbpusd * (init_gbp - mt5.symbol_info("GBPUSD").bid) + volume_usdjpy * (mt5.symbol_info("USDJPY").ask - init_jpy) + volume_gbpjpy * (mt5.symbol_info("GBPJPY").ask - init_gbp_jpy)
            sod_gbp_sell = volume_gbpusd * (mt5.symbol_info("GBPUSD").ask - init_gbp) + volume_usdjpy * (init_jpy - mt5.symbol_info("USDJPY").bid) + volume_gbpjpy * (init_gbp_jpy - mt5.symbol_info("GBPJPY").bid)

            sod_chf_buy = volume_usdchf * (mt5.symbol_info("USDCHF").ask - init_chf) + volume_eurchf * (init_eur_chf - mt5.symbol_info("EURCHF").bid) + volume_eurusd * (mt5.symbol_info("EURUSD").ask - init_eur)
            sod_chf_sell = volume_usdchf * (init_chf - mt5.symbol_info("USDCHF").bid) + volume_eurchf * (mt5.symbol_info("EURCHF").ask - init_eur_chf) + volume_eurusd * (init_eur - mt5.symbol_info("EURUSD").bid)

            sod_cad_buy = volume_usdcad * (mt5.symbol_info("USDCAD").ask - init_cad) + volume_cadjpy * (mt5.symbol_info("CADJPY").ask - init_cad_jpy) + volume_usdjpy * (init_jpy - mt5.symbol_info("USDJPY").bid)
            sod_cad_sell = volume_usdcad * (init_cad - mt5.symbol_info("USDCAD").bid) + volume_cadjpy * (mt5.symbol_info("CADJPY").ask - init_cad_jpy) + volume_usdjpy * (mt5.symbol_info("USDJPY").ask - init_jpy)

            sod_eur_cad_buy = volume_eurcad * (mt5.symbol_info("EURCAD").ask - init_eur_cad) + volume_usdcad * (mt5.symbol_info("USDCAD").ask - init_cad) + volume_usdjpy * (init_jpy - mt5.symbol_info("USDJPY").bid)
            sod_eur_cad_sell = volume_eurcad * (init_eur_cad - mt5.symbol_info("EURCAD").bid) + volume_usdcad * (mt5.symbol_info("USDCAD").ask - init_cad) + volume_usdjpy * (mt5.symbol_info("USDJPY").ask - init_jpy)

            sod_eur_aud_buy = volume_euraud * (mt5.symbol_info("EURAUD").ask - init_eur_aud) + volume_audusd * (mt5.symbol_info("AUDUSD").ask - init_aud) + volume_audnzd * (init_aud_nzd - mt5.symbol_info("AUDNZD").bid)
            sod_eur_aud_sell = volume_euraud * (init_eur_aud - mt5.symbol_info("EURAUD").bid) + volume_audusd * (mt5.symbol_info("AUDUSD").ask - init_aud) + volume_audnzd * (mt5.symbol_info("AUDNZD").ask - init_aud_nzd)


            if abs(sod_eur_buy) > 10 or abs(sod_eur_sell) > 10 or abs(sod_jpy_buy) > 10 or abs(sod_jpy_sell) > 10 or abs(sod_aud_buy) > 10 or abs(sod_aud_sell) > 10 or abs(sod_gbp_buy) > 10 or abs(sod_gbp_sell) > 10 or abs(sod_chf_buy) > 10 or abs(sod_chf_sell) > 10 or abs(sod_cad_buy) > 10 or abs(sod_cad_sell) > 10 or abs(sod_eur_cad_buy) > 10 or abs(sod_eur_cad_sell) > 10 or abs(sod_eur_aud_buy) > 10 or abs(sod_eur_aud_sell) > 10 :

                data = [[datetime.datetime.now(), int(sod_eur_buy) , int(sod_eur_sell) , int(sod_jpy_buy) , int(sod_jpy_sell) , int(sod_aud_buy) , int(sod_aud_sell) , int(sod_gbp_buy) , int(sod_gbp_sell) , int(sod_chf_buy) , int(sod_chf_sell) , int(sod_cad_buy) , int(sod_cad_sell) , int(sod_eur_cad_buy) , int(sod_eur_cad_sell) , int(sod_eur_aud_buy) , int(sod_eur_aud_sell) ]]
                write_to('trade_arbit.csv', data)

            print(int(sod_eur_buy) , int(sod_eur_sell) , int(sod_jpy_buy) , int(sod_jpy_sell) , int(sod_aud_buy) , int(sod_aud_sell) , int(sod_gbp_buy) , int(sod_gbp_sell) , int(sod_chf_buy) , int(sod_chf_sell) , int(sod_cad_buy) , int(sod_cad_sell) , int(sod_eur_cad_buy) , int(sod_eur_cad_sell) , int(sod_eur_aud_buy) , int(sod_eur_aud_sell) )








            # sod_eur_sell = (mt5.symbol_info("EURUSD").bid - init_eur) * 100_000 + (init_gbp - mt5.symbol_info("GBPUSD").ask) * 85_000 + (init_eur_gbp - mt5.symbol_info("EURGBP").ask) * 100_000

            # sod_jpy_buy = (mt5.symbol_info("USDJPY").ask - init_jpy) * 100_000 + (init_eur_jpy - mt5.symbol_info("EURJPY").ask) * 100_000  + (mt5.symbol_info("EURUSD").ask - init_eur) * 100_000
            # sod_jpy_sell = (init_jpy - mt5.symbol_info("USDJPY").bid) * 100_000 + (mt5.symbol_info("EURJPY").bid - init_eur_jpy) * 100_000 + (init_eur - mt5.symbol_info("EURUSD").bid) * 100_000

            # sod_aud_buy = (init_aud - mt5.symbol_info("AUDUSD").ask) * 100_000 + (mt5.symbol_info("NZDUSD").ask - init_nzd) * 100_000 + (mt5.symbol_info("AUDNZD").bid - init_aud_nzd) * 100_000
            # sod_aud_sell = (mt5.symbol_info("AUDUSD").bid - init_aud) * 100_000 + (init_nzd - mt5.symbol_info("NZDUSD").bid) * 100_000 + (init_aud_nzd - mt5.symbol_info("AUDNZD").ask) * 100_000

            # sod_gbp_buy = (init_gbp - mt5.symbol_info("GBPUSD").bid) * 100_000 + (mt5.symbol_info("USDJPY").ask - init_jpy) * 100_000 + (mt5.symbol_info("GBPJPY").ask - init_gbp_jpy) * 100_000
            # sod_gbp_sell = (mt5.symbol_info("GBPUSD").ask - init_gbp) * 100_000 + (init_jpy - mt5.symbol_info("USDJPY").bid) * 100_000 + (init_gbp_jpy - mt5.symbol_info("GBPJPY").bid) * 100_000

            # sod_chf_buy = (mt5.symbol_info("USDCHF").ask - init_chf) * 100_000 + (init_eur_chf  - mt5.symbol_info("EURCHF").ask) * 100_000 + (mt5.symbol_info("EURUSD").ask - init_eur) * 100_000
            # sod_chf_sell = (init_chf - mt5.symbol_info("USDCHF").bid) * 100_000 + (mt5.symbol_info("EURCHF").bid - init_eur_chf) * 100_000 + (init_eur - mt5.symbol_info("EURUSD").bid) * 100_000

            # sod_cad_buy = (mt5.symbol_info("USDCAD").ask - init_cad) * 100_000 + (mt5.symbol_info("CADJPY").ask - init_cad_jpy) * 100_000 + (init_jpy  - mt5.symbol_info("USDJPY").ask ) * 100_000
            # sod_cad_sell = (init_cad - mt5.symbol_info("USDCAD").bid) * 100_000 + (init_cad_jpy - mt5.symbol_info("CADJPY").bid) * 100_000 + (mt5.symbol_info("USDJPY").bid - init_jpy) * 100_000






            # if abs(sod_eur_buy) > 10 or abs(sod_eur_sell) > 10 or abs(sod_jpy_buy) > 10 or abs(sod_jpy_sell) > 10 or abs(sod_aud_buy) > 10 or abs(sod_aud_sell) > 10 or abs(sod_gbp_buy) > 10 or abs(sod_gbp_sell) > 10 or abs(sod_chf_buy) > 10 or abs(sod_chf_sell) > 10 or abs(sod_cad_buy) > 10 or abs(sod_cad_sell) > 10:

            #     data = [[datetime.datetime.now(), sod_eur_buy, sod_eur_sell, sod_jpy_buy, sod_jpy_sell, sod_aud_buy, sod_aud_sell, sod_gbp_buy, sod_gbp_sell, sod_chf_buy, sod_chf_sell, sod_cad_buy, sod_cad_sell]]
            #     write_to_csv('trade_arbit.csv', data)



            

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


def test_main():


    init_eur = mt5.symbol_info("EURUSD").ask
    init_gbp = mt5.symbol_info("GBPUSD").bid
    init_eur_gbp = mt5.symbol_info("EURGBP").bid




    print(init_eur , init_gbp , init_eur_gbp)

    while True:
        try:
            time.sleep(0.01)

            sod_eur_buy = (init_eur - mt5.symbol_info("EURUSD").ask) * 100_000 + (mt5.symbol_info("GBPUSD").bid - init_gbp) * 85_000 + (mt5.symbol_info("EURGBP").bid - init_eur_gbp) * 100_000 
            sod_eur_sell = (mt5.symbol_info("EURUSD").bid - init_eur) * 100_000 + (init_gbp - mt5.symbol_info("GBPUSD").ask) * 85_000 + (init_eur_gbp - mt5.symbol_info("EURGBP").ask) * 100_000




            if abs(sod_eur_buy) > 10 or abs(sod_eur_sell) > 10:
                data = [[datetime.datetime.now(), sod_eur_buy, sod_eur_sell ]]
                write_to('ali_main.csv', data)

            print(sod_eur_buy, sod_eur_sell )

            

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)


def test():


    init_eur = mt5.symbol_info("EURUSD").ask
    init_gbp = mt5.symbol_info("GBPUSD").bid
    init_eur_gbp = mt5.symbol_info("EURGBP").bid

    init_jpy = mt5.symbol_info("USDJPY").ask
    init_eur_jpy = mt5.symbol_info("EURJPY").ask

    init_aud = mt5.symbol_info("AUDUSD").ask
    init_nzd = mt5.symbol_info("NZDUSD").ask
    init_aud_nzd = mt5.symbol_info("AUDNZD").bid

    init_gbp_jpy = mt5.symbol_info("GBPJPY").ask

    init_chf = mt5.symbol_info("USDCHF").ask
    init_eur_chf = mt5.symbol_info("EURCHF").ask

    init_cad = mt5.symbol_info("USDCAD").ask
    init_cad_jpy = mt5.symbol_info("CADJPY").ask

    init_eur_cad = mt5.symbol_info("EURCAD").ask
    init_eur_aud = mt5.symbol_info("EURAUD").ask
    init_eur_nzd = mt5.symbol_info("EURNZD").ask


    print(init_eur , init_gbp , init_eur_gbp)

    def pip_value(symbol, lot_size=100000):
        point = mt5.symbol_info(symbol).point
        return point * lot_size

    # ارزش پیپ‌ها
    pip_eurusd = pip_value("EURUSD")
    pip_gbpusd = pip_value("GBPUSD")
    pip_eurgbp = pip_value("EURGBP")
    pip_usdjpy = pip_value("USDJPY")
    pip_eurjpy = pip_value("EURJPY")
    pip_audusd = pip_value("AUDUSD")
    pip_nzdusd = pip_value("NZDUSD")
    pip_audnzd = pip_value("AUDNZD")
    pip_gbpjpy = pip_value("GBPJPY")
    pip_usdchf = pip_value("USDCHF")
    pip_eurchf = pip_value("EURCHF")
    pip_usdcad = pip_value("USDCAD")
    pip_cadjpy = pip_value("CADJPY")

    # تنظیم ضریب‌ها
    volume_eurusd = 100_000 / pip_eurusd
    volume_gbpusd = 100_000 / pip_gbpusd
    volume_eurgbp = 100_000 / pip_eurgbp
    volume_usdjpy = 100_000 / pip_usdjpy
    volume_eurjpy = 100_000 / pip_eurjpy
    volume_audusd = 100_000 / pip_audusd
    volume_nzdusd = 100_000 / pip_nzdusd
    volume_audnzd = 100_000 / pip_audnzd
    volume_gbpjpy = 100_000 / pip_gbpjpy
    volume_usdchf = 100_000 / pip_usdchf
    volume_eurchf = 100_000 / pip_eurchf
    volume_usdcad = 100_000 / pip_usdcad
    volume_cadjpy = 100_000 / pip_cadjpy
    

    while True:
        try:
            time.sleep(0.01)

            # محاسبه SODها
            sod_eur_buy = (init_eur - mt5.symbol_info("EURUSD").ask) * volume_eurusd + \
                        (mt5.symbol_info("GBPUSD").bid - init_gbp) * volume_gbpusd + \
                        (mt5.symbol_info("EURGBP").bid - init_eur_gbp) * volume_eurgbp

            sod_eur_sell = (mt5.symbol_info("EURUSD").bid - init_eur) * volume_eurusd + \
                        (init_gbp - mt5.symbol_info("GBPUSD").ask) * volume_gbpusd + \
                        (init_eur_gbp - mt5.symbol_info("EURGBP").ask) * volume_eurgbp

            sod_jpy_buy = (mt5.symbol_info("USDJPY").ask - init_jpy) * volume_usdjpy + \
                        (init_eur_jpy - mt5.symbol_info("EURJPY").ask) * volume_eurjpy + \
                        (mt5.symbol_info("EURUSD").ask - init_eur) * volume_eurusd

            sod_jpy_sell = (init_jpy - mt5.symbol_info("USDJPY").bid) * volume_usdjpy + \
                        (mt5.symbol_info("EURJPY").bid - init_eur_jpy) * volume_eurjpy + \
                        (init_eur - mt5.symbol_info("EURUSD").bid) * volume_eurusd

            sod_aud_buy = (init_aud - mt5.symbol_info("AUDUSD").ask) * volume_audusd + \
                        (mt5.symbol_info("NZDUSD").ask - init_nzd) * volume_nzdusd + \
                        (mt5.symbol_info("AUDNZD").bid - init_aud_nzd) * volume_audnzd

            sod_aud_sell = (mt5.symbol_info("AUDUSD").bid - init_aud) * volume_audusd + \
                        (init_nzd - mt5.symbol_info("NZDUSD").bid) * volume_nzdusd + \
                        (init_aud_nzd - mt5.symbol_info("AUDNZD").ask) * volume_audnzd

            sod_gbp_buy = (init_gbp - mt5.symbol_info("GBPUSD").bid) * volume_gbpusd + \
                        (mt5.symbol_info("USDJPY").ask - init_jpy) * volume_usdjpy + \
                        (mt5.symbol_info("GBPJPY").ask - init_gbp_jpy) * volume_gbpjpy

            sod_gbp_sell = (mt5.symbol_info("GBPUSD").ask - init_gbp) * volume_gbpusd + \
                        (init_jpy - mt5.symbol_info("USDJPY").bid) * volume_usdjpy + \
                        (init_gbp_jpy - mt5.symbol_info("GBPJPY").bid) * volume_gbpjpy

            sod_chf_buy = (mt5.symbol_info("USDCHF").ask - init_chf) * volume_usdchf + \
                        (init_eur_chf - mt5.symbol_info("EURCHF").ask) * volume_eurchf + \
                        (mt5.symbol_info("EURUSD").ask - init_eur) * volume_eurusd

            sod_chf_sell = (init_chf - mt5.symbol_info("USDCHF").bid) * volume_usdchf + \
                        (mt5.symbol_info("EURCHF").bid - init_eur_chf) * volume_eurchf + \
                        (init_eur - mt5.symbol_info("EURUSD").bid) * volume_eurusd

            sod_cad_buy = (mt5.symbol_info("USDCAD").ask - init_cad) * volume_usdcad + \
                        (mt5.symbol_info("CADJPY").ask - init_cad_jpy) * volume_cadjpy + \
                        (init_jpy - mt5.symbol_info("USDJPY").ask) * volume_usdjpy

            sod_cad_sell = (init_cad - mt5.symbol_info("USDCAD").bid) * volume_usdcad + \
                        (init_cad_jpy - mt5.symbol_info("CADJPY").bid) * volume_cadjpy + \
                        (mt5.symbol_info("USDJPY").bid - init_jpy) * volume_usdjpy


            if abs(sod_eur_buy) > 10 or abs(sod_eur_sell) > 10 or abs(sod_jpy_buy) > 10 or abs(sod_jpy_sell) > 10 or abs(sod_aud_buy) > 10 or abs(sod_aud_sell) > 10 or abs(sod_gbp_buy) > 10 or abs(sod_gbp_sell) > 10 or abs(sod_chf_buy) > 10 or abs(sod_chf_sell) > 10 or abs(sod_cad_buy) > 10 or abs(sod_cad_sell) > 10:


                data = [[datetime.datetime.now(), sod_eur_buy, sod_eur_sell, sod_jpy_buy, sod_jpy_sell, sod_aud_buy, sod_aud_sell, sod_gbp_buy, sod_gbp_sell, sod_chf_buy, sod_chf_sell, sod_cad_buy, sod_cad_sell]]
                write_to_csv('ali_arbit.csv', data)

            print(sod_eur_buy, sod_eur_sell, sod_jpy_buy, sod_jpy_sell, sod_aud_buy, sod_aud_sell, sod_gbp_buy, sod_gbp_sell, sod_chf_buy, sod_chf_sell, sod_cad_buy, sod_cad_sell)

            

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)





def write_to_csv(filename, data):
    # This function should be defined to handle writing data to a CSV file
    pass


# test_main()
test__()