
import MetaTrader5 as mt5 
import pandas as pd 
from datetime import datetime
import time
import socket
import numpy as np
import threading as th
from datetime import datetime
import threading as th
import re
from multiprocessing import Pool


acc_slave2 , server_slave2 , password_slave2 =   7780110  , 'Eightcap-Demo' , 'Mahdi1400@'
adres_slave2 =  r"C:\Program Files\EightCap MetaTrader 5\terminal64.exe" 


acc_slave , server_slave , password_slave =   89161277  , 'LiteFinance-MT5-Demo' , 'Mahdi1400@'
adres_slave =  r"C:\Program Files\LiteFinance MT5 Terminal\terminal64.exe" 



acc_master , server_master , password_master =    61220065 , 'Pepperstone-Demo' , 'Mahdi1400@'
adres_master = r"C:\Program Files\Pepperstone MetaTrader 5\terminal64.exe"


def trade(symbol , lot , tp_ , sl_ , type_ , id , login  , server   , password   , path ):
    mt5.initialize( path = path)
    mt5.login( login = login , server =  server  , password = password  )
    


            
            
    if type_ == 1:
        pos = mt5.ORDER_TYPE_SELL
    if type_ == 0 :
        pos = mt5.ORDER_TYPE_BUY








    price = mt5.symbol_info_tick(f"{symbol}").ask
    deviation = 1000
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": f'{symbol}',
        "volume": lot,
        "type":  pos ,
        "price": price,
        "sl": sl_ ,
        "tp": tp_ ,
        "deviation": deviation,
        "magic": 234092,
        "comment": str(id) ,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK ,
    }
    #print(request)   
    # send a trading request
    result = mt5.order_send(request)
    
    # # check the execution result
    # #print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol,lot,price,deviation))
    # #print(result)






dicts = []


class copy:
    

    def __init__(self , acc , server , password , adres , type , eu):
        self.acc     = acc
        self.adres   = adres
        self.server  = server
        self.password= password
        self.type   = type
        self.eu     = eu



    def master(self):
        global dicts
        if self.type == 'master' :
            
   
            

                
            while True:
                init_master = mt5.initialize( path = self.adres)
                login_master= mt5.login( login = self.acc , server =  self.server  , password = self.password  )
                if not init_master or not login_master:
                    continue
                # account_info = mt5.account_info()                        
                
                # pd.set_option('display.max_columns', 500) # number of columns to be displayed
                # pd.set_option('display.width', 1500)      # max table width to display
                # display data on the MetaTrader 5 package


                
                # get open positions on USDCHF
                positions=mt5.positions_get()
                if len(positions) < 1:
                    dicts = []
                elif len(positions)>0:
                    #print("positions_get={}".format(len(positions)))
                    # display these positions as a table using pandas.DataFrame
                    # df=pd.DataFrame(list(positions),columns=positions[0]._asdict().keys())
                    # df['time'] = pd.to_datetime(df['time'], unit='s')
                    # df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
                    # #print(df)
                # for position in positions:
                #     #print(position._asdict())
                #     # df = positions[0]
                #     # #print(df)

                    dicts= [
                        {
                            'ticket': t[0],
                            'time': t[1],
                            'time_msc': t[2],
                            'time_update': t[3],
                            'time_update_msc': t[4],
                            'type': t[5],
                            'magic': t[6],
                            'identifier': t[7],
                            'reason': t[8],
                            'volume': t[9],
                            'price_open': t[10],
                            'sl': t[11],
                            'tp': t[12],
                            'price_current': t[13],
                            'swap': t[14],
                            'profit': t[15],
                            'symbol': re.sub(r'[^A-Z0-9]', '',t[16])  ,
                            'comment': t[17],
                            'external_id': t[18]
                        }
                        for t in positions
                    ]
                
                   
                
                time.sleep(0.1)



                
                    
                
    def slave(self):
        global dicts
        pos = []
        if self.type == 'slave':
     
            

                
            while True:
                
                time.sleep(0.2)

                init_slave =  mt5.initialize( path = self.adres)
                login_slave=  mt5.login( login = self.acc , server =  self.server  , password = self.password  )

                if not init_slave or not login_slave:
                    continue


                positions=mt5.positions_get()
                if positions==None:
                    #print("No positions with group=\"*USD*\", error code={}".format(mt5.last_error()))
                    pass
                elif len(positions)>0:
                    


                    pos = [
                        {
                            'ticket': t[0],
                            'time': t[1],
                            'time_msc': t[2],
                            'time_update': t[3],
                            'time_update_msc': t[4],
                            'type': t[5],
                            'magic': t[6],
                            'identifier': t[7],
                            'reason': t[8],
                            'volume': t[9],
                            'price_open': t[10],
                            'sl': t[11],
                            'tp': t[12],
                            'price_current': t[13],
                            'swap': t[14],
                            'profit': t[15],
                            'symbol': t[16],
                            'comment': t[17],
                            'external_id': t[18]
                        }
                        for t in positions
                    ]


                list_ticket = list(map(lambda dicts : dicts['ticket'] , dicts))
                
                list_comment = list(map(lambda pos : pos['comment'] , pos))
                # list_comment = list(map(int , list_comment))
                list_comment = [int(num) for num in list_comment if num.isdigit()]
                
                
                    
                if list_ticket :
                    new = list(set(list_ticket) - set(list_comment))
                    
                    
                    dic_ticket = {comment['ticket']: comment for comment in dicts}
                    for ticket in new:
                        if ticket in dic_ticket:
                            
                            #print('hi')
                            target_dict = dic_ticket[ticket]
                            #(symbol , lot , tp_ , sl_ , type , id )
                            
                            symbol = target_dict.get('symbol') + self.eu
                            lot    = target_dict.get('volume')
                            tp_    = target_dict.get('tp')
                            sl_    = target_dict.get('sl')
                            type_   = target_dict.get('type')                                  
                            id__     = target_dict.get('ticket')
                            #symbol , lot , tp_ , sl_ , type , id , login  , server   , password   ,                        adres 
                            trade( symbol , lot , tp_ , sl_ , type_ , id__ ,  self.acc ,   self.server  ,  self.password ,    self.adres  )
                            


                    
                def close_position(position , login  , server   , password   , path , eu ):


                    # mt5.initialize( path = path)
                    # mt5.login( login = login , server =  server  , password = password  )



    
                    #print('her is ',position.symbol)
                    tick = mt5.symbol_info_tick(position.symbol)
                    price = mt5.symbol_info_tick(position.symbol).ask
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "position": position.ticket,
                        "symbol": position.symbol  ,
                        "volume": position.volume,
                        "type": mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
                        "price": price ,  
                        "deviation": 100,
                        "magic": 234002,
                        "comment": "Gu",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_FOK ,
                    }

                    result = mt5.order_send(request)     
                    
                    
                        
                close = list(set(list_comment) - set(list_ticket))
                
                
                
                
                
                
                #print(list_comment , list_ticket )
                
                positions = mt5.positions_get()
                
                
                for position in positions:

            
                    

                    
                    #print(position)
                    if close:
                        if int(position.comment) in close:
                            
                            close_position(position , self.acc ,   self.server  ,  self.password ,    self.adres , self.eu )
                        
                        

















def to_ag(args):
    acc, server, password, adres, type_, eu = args
    copy_obj = copy(acc, server, password, adres, type_, eu)
    if type_ == 'master':
        copy_obj.master()
    elif type_ == 'slave':
        copy_obj.slave()
            

    args = [
        (acc_slave, server_slave, password_slave, adres_slave, 'master', ''),
        (acc_slave, server_slave, password_slave, adres_slave, 'slave', '_o'),
        (acc_master, server_master, password_master, adres_master, 'master', '')
    ]
    
    # ایجاد یک Pool با تعداد نخ‌های مورد نیاز
    with Pool() as pool:
        pool.map(to_ag, args)


