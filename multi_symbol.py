
import MetaTrader5 as mt5
import pandas as pd 
import threading as th
import time
import datetime

import math
import pytz


tehran_timezone = pytz.timezone('Asia/Tehran')

df_pross = pd.DataFrame(columns= ['time' ,  'pros' , 'sum_trade' , 'balance'])

def round_up(number, precision):

  return math.ceil(number * (10**precision)) / (10**precision)




def init():
    mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 2\terminal64.exe")
    mt5.login(89371057 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Demo')


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
        
    else:
        return ("Done . position #{} closed".format(result)) , True    
    # check the execution result
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
    
    tp = abs(mt5.symbol_info_tick(symbol).ask - tp_ ) 
    sl = abs(mt5.symbol_info_tick(symbol).bid + sl_ ) 
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
        
    else:
        return ("Done . position #{} closed".format(result)) , True
    # print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol,lot,price,deviation));
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


def trade(symbol , lot , tp , sl):
    numtrade = 0
    # up_numtrade = 0
    sl = sl * 10
    level_buy  = None   # price level buy
    level_sell = None   # price level sell
    
    level_buy_count  = 0
    level_sell_count = 0
    
    level_vol_buy   = 0
    level_vol_sell  = 0
    
    position_count = 0
    
    sod_main = 0.0
    
    level_trade = 2
    
    final_level = 7
    
    vol_zarb = 1
    
    pros = 0
    count_trade = 0
    
    sum_volum = []

    pross = 0

    init_position = True
    init_sell = False
    
    while True:
        
        
        
        positions_total=len(mt5.positions_get(symbol=symbol))
        
        if positions_total == 0:
            position_count = 0
            
        
        
        

        if positions_total > 0 and positions_total < position_count :
            
            position_count = 0
            df_pross.loc[pros -1 , 'sum_trade'] = len(mt5.positions_get(symbol=symbol))
            close(symbol)
            
            break
            
            
            
            
            # continue
        
        
     
        if   positions_total == 0 and init_position :
            
            
            buy( symbol, lot ,  tp ,  sl )
            # th.Thread(target= sell , args= ( symbol, lot ,  tp ,  sl)).start()
            
            level_buy  = mt5.symbol_info_tick(symbol).bid 
            level_sell = abs(mt5.symbol_info_tick(symbol).ask - (tp / 2 )) 
            
            
            level_buy_count += 1
            position_count += 1
            level_vol_buy = lot
            level_sell_count = 0
            sum_volum = []
            sum_volum.append(lot)
            
            numtrade += 1
            
            

            
            pros += 1
            


            pross += 1
            init_position = False
            init_sell = True
            continue


        
        # if positions_total > level_trade :
        #     # vol_zarb = (positions_total - level_trade) + 1
        #     vol_zarb = (sum(sum_volum) *  0.06 ) * 100
        
        # if positions_total >= level_trade and (mt5.account_info().equity - mt5.account_info().balance )  >=  vol_zarb :

        #     position_count = 0
        #     df_pross.loc[pros -1 , 'sum_trade'] = len(mt5.positions_get(symbol=symbol))
        #     close(symbol)
        #     break
            

            
            # continue
        
        # if positions_total == final_level and (mt5.account_info().equity - mt5.account_info().balance ) <= -50 :
            
        #     position_count = 0
        #     df_pross.loc[pros -1 , 'sum_trade'] = len(mt5.positions_get(symbol=symbol))
        #     close(symbol)
        #     break
            
            
            
            
        
        # if positions_total >= level_trade  and mt5.symbol_info_tick(symbol).bid   >= level_buy - 0.0002:
            
        #     position_count = 0
        #     df_pross.loc[pros -1 , 'sum_trade'] = len(mt5.positions_get(symbol=symbol))
        #     close(symbol)
        #     time.sleep(1)
            
            
            
        #     continue         
        
        
        if mt5.symbol_info_tick(symbol).ask   <= level_sell  and level_sell_count < level_buy_count and numtrade == 1  and init_sell  :
            


            level_sell_count = level_buy_count +1
            position_count += 1
            level_vol_sell  = level_vol_buy * 2.5 
            sell( symbol, level_vol_sell ,  tp ,  sl )
            numtrade += 1
            sum_volum.append(level_vol_sell)

            
            
            
        if mt5.symbol_info_tick(symbol).ask   >= level_buy  and level_buy_count  < level_sell_count and numtrade == 2   :
            

            # level_buy_count  = level_sell_count +1
            # position_count += 1
            # level_vol_buy = level_vol_sell - lot
            
            # buy( symbol, level_vol_buy ,  tp ,  sl )
            # numtrade += 1
            # sum_volum.append(level_vol_buy)
            position_count = 0
            close(symbol)
            break


            
        
        
        # if  positions_total != None :
        #     if positions_total < numtrade :
                
        #         th.Thread(target= buy  , args= ( symbol, lot ,  tp ,  sl )).start()
        #         th.Thread(target= sell , args= ( symbol, lot ,  tp ,  sl)).start()
                
                
        #         numtrade =+ 2
        #         continue
            

            
        #     numtrade = positions_total


        time.sleep(0.01)
        
        
def main():
    # دریافت زمان فعلی


    init()

    


    th.Thread(target= trade , args= ( 'USDJPY_o' ,  0.3 , 0.05   , 0.05 )).start()
    time.sleep(0.1)    
    th.Thread(target= trade , args= ( 'GBPUSD_o' ,  0.3 , 0.0005, 0.01 )).start()
    time.sleep(0.1)
    th.Thread(target= trade , args= ( 'AUDUSD_o' ,  0.3 , 0.0005 , 0.01 )).start()
    time.sleep(0.1)
    th.Thread(target= trade , args= ( 'NZDUSD_o' ,  0.3 , 0.0005 , 0.01 )).start()
    time.sleep(0.1)
    th.Thread(target= trade , args= ( 'EURUSD_o' ,  0.3 , 0.0005 , 0.01 )).start()
    time.sleep(0.1)
    th.Thread(target= trade , args= ( 'USDCAD_o' ,  0.1 , 0.00009 , 0.0006)).start()
    # th.Thread(target= trade , args= ( 'USDCHF_o' ,  0.1 , 0.00009 , 0.0006 )).start()



    # trade(symbol='USDJPY_o' , lot= 0.1 ,tp= 0.009 ,sl= 0.006)
    # trade(symbol='GBPUSD_o' , lot= 0.5 ,tp= 0.0006 ,sl= 0.004)
    # trade(symbol='NZDUSD_o' , lot= 0.1 ,tp= 0.00009 ,sl= 0.0006)
    # trade(symbol='USDCAD_o' , lot= 0.1 ,tp= 0.00009 ,sl= 0.0006)
    # trade(symbol='USDCHF_o' , lot= 0.1 ,tp= 0.00009 ,sl= 0.0006)
    # trade(symbol='EURUSD_o' , lot= 0.2 ,tp= 0.0004 ,sl= 0.01)
    # trade(symbol='XAUUSD_o' , lot= 0.02  ,tp= 1,sl= 1)

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
            "comment": "Gu",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK ,
        }

        result = mt5.order_send(request)
        return result

    for position in positions:
        # print(position)
        
        if position.symbol == symbol :
            close_position(position)
            time.sleep(0.1)

def run():



    while True:
        time.sleep(1)


        
          # توقف اجرا برای ۶۰ ثانیه
        # current_time = datetime.datetime.now().time()
        # print(current_time)
        # # مقایسه زمان فعلی با زمان مورد نظر (ساعت 6:00 صبح)
        # target_time = datetime.time(16, 19, 1)  # زمان مورد نظر
        # target_close = datetime.time(22, 1, 1)  # زمان مورد نظر
        # run_main = 0
        # close_main = 0

        # if current_time.hour == target_time.hour and current_time.minute == target_time.minute  and run_main == 0  :
        #     run_main = 1

        #     main()
            
        
        # if current_time.hour == target_close.hour and current_time.minute == target_close.minute and close_main == 0 :
        #     close_main = 1

        #     close()



        now = datetime.datetime.now(tehran_timezone)

        if now.hour == 6 or now.hour == 8 or now.hour == 12 :
            if now.minute == 1 :
                main()
                time.sleep(100)           

        if now.hour == 16 or now.hour == 20 :

            if now.minute == 5 :
                main()
                time.sleep(100)
    
        # if now.hour == 15 and  now.minute == 31  :

            
        #     print('main')
        #     main()
        #     time.sleep(100)
            

        
        # close()

# init()
run()
# th.Thread(target= ).start()

