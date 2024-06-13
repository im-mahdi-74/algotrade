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

class Main:
    def __init__(self):
        self.init()

    def round_up(self, number, precision):
        return math.ceil(number * (10**precision)) / (10**precision)

    def init(self):
        # mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 real\terminal64.exe")
        # mt5.login(6910350 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Live')
        # mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 real 2\terminal64.exe")
        # mt5.login(6920086 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Live')
        mt5.initialize(path=r"C:\Program Files\LiteFinance MT5 3\terminal64.exe")
        mt5.login(89373537, password='Mahdi1400@', server='LiteFinance-MT5-Demo')

    def info(self):
        account_info = mt5.account_info()
        balance = account_info.balance
        equity = account_info.equity
        profit = account_info.profit
        return balance, equity, profit

    def buy(self, symbol, lot, tp_, sl_, comment):
        tp = abs(mt5.symbol_info_tick(symbol).bid + tp_)
        sl = abs(mt5.symbol_info_tick(symbol).ask - sl_)
        pos = mt5.ORDER_TYPE_BUY

        lot = self.round_up(lot, 2)
        price = mt5.symbol_info_tick(symbol).ask
        deviation = 100
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": pos,
            "price": price,
            "deviation": deviation,
            "magic": 234002,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return f"failed . order_send failed, retcode={result.retcode} {request}", False
            
        if result.retcode == 10009:
            return result

    def sell(self, symbol, lot, tp_, sl_, comment):
        tp = abs(mt5.symbol_info_tick(symbol).ask - tp_)
        sl = abs(mt5.symbol_info_tick(symbol).bid + sl_)
        pos = mt5.ORDER_TYPE_SELL

        lot = self.round_up(lot, 2)
        price = mt5.symbol_info_tick(symbol).ask
        deviation = 100
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": pos,
            "price": price,
            "deviation": deviation,
            "magic": 234002,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return f"failed . order_send failed, retcode={result.retcode} {request}", False
            
        if result.retcode == 10009:
            return result

    def close(self, ticket):
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
                    "type_filling": mt5.ORDER_FILLING_FOK,
                }

                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(f"Close failed . order_send failed, retcode={result.retcode} {request}")
                    return False
                if result.retcode == 10009:
                    return True
            except Exception as e:
                print(f'Close : Error in def close {e}')

        positions = mt5.positions_get()
        for position in positions:
            if position.ticket == ticket:
                try:
                    doit = close_position(position)
                    return doit
                except Exception as e:
                    print(f'Close : Error for Close {e}')

    def close_(self, ticket, volume, comment):
        comment = str(comment)
        volume = round(volume, 2)
        
        def close_position(position, volume, comment):
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
                    "type_filling": mt5.ORDER_FILLING_FOK,
                }

                result = mt5.order_send(request)
                print(result, request)
            except Exception as e:
                print(f'Close : Error in def close {e}')

        positions = mt5.positions_get()
        for position in positions:
            if position.ticket == ticket:
                try:
                    close_position(position, volume, comment)
                    return 'close'
                except Exception as e:
                    print(f'Close : Error for Close {e}')

    def order_close(self, symbol):
        orders = mt5.orders_get(symbol=symbol)
        if orders:
            request = {
                'action': mt5.TRADE_ACTION_REMOVE,
                'order': mt5.orders_get(symbol=symbol)[0].ticket
            }
            
            result = mt5.order_send(request)
            if result is None:
                print(f"No orders with group=\"*GBP*\", error code={mt5.last_error()}")
            else:
                if result.retcode == 10009:
                    return True

    def close_pos(self, tickit_one_one, tickit_one_two, tickit_two_one, tickit_two_two):
        sod = 5
        zar = -5
        level_close = 10

        while True:
            time.sleep(0.25)
            
            positions_one_one = mt5.positions_get(ticket=tickit_one_one.order)
            positions_one_two = mt5.positions_get(ticket=tickit_one_two.order)
            positions_two_one = mt5.positions_get(ticket=tickit_two_one.order)
            positions_two_two = mt5.positions_get(ticket=tickit_two_two.order)

            if not positions_one_one or not positions_one_two or not positions_two_one or not positions_two_two:
                return True

            balance_kol = positions_one_one[0].profit + positions_one_two[0].profit + positions_two_one[0].profit + positions_two_two[0].profit
            balance_one = positions_one_one[0].profit + positions_one_two[0].profit
            balance_two = positions_two_one[0].profit + positions_two_two[0].profit

            print(balance_kol, balance_one, balance_two)

            if positions_one_one[0].volume <= 0.1: 
                pass

            if balance_kol >= 0:
                for i in [tickit_one_one.order, tickit_one_two.order, tickit_two_one.order, tickit_two_two.order]:
                    time.sleep(0.2)
                    self.close(i)
                break

            if balance_one >= sod:
                self.close_(tickit_one_one.order, self.round_up(positions_one_one[0].volume / level_close, 2), level_close)
                self.close_(tickit_one_two.order, self.round_up(positions_one_two[0].volume / level_close, 2), level_close)
                
                if positions_one_two[0].volume <= 0.1:
                    break

                while True:
                    positions_two_one = mt5.positions_get(ticket=tickit_two_one.order)
                    positions_two_two = mt5.positions_get(ticket=tickit_two_two.order)
                    balance_two_pass = positions_two_one[0].profit + positions_two_two[0].profit

                    if balance_two_pass / level_close >= zar:
                        self.close_(tickit_two_one.order, self.round_up(positions_two_one[0].volume / level_close, 2), level_close)
                        self.close_(tickit_two_two.order, self.round_up(positions_two_two[0].volume / level_close, 2), level_close)
                        level_close -= 1
                        break

            if balance_two >= sod:
                self.close_(tickit_two_one.order, self.round_up(positions_two_one[0].volume / level_close, 2), level_close)
                self.close_(tickit_two_two.order, self.round_up(positions_two_two[0].volume / level_close, 2), level_close)
                
                if positions_two_two[0].volume <= 0.1:
                    break

                while True:
                    positions_one_one = mt5.positions_get(ticket=tickit_one_one.order)
                    positions_one_two = mt5.positions_get(ticket=tickit_one_two.order)
                    balance_one_pass = positions_one_one[0].profit + positions_one_two[0].profit

                    if balance_one_pass / level_close >= zar:
                        self.close_(tickit_one_one.order, self.round_up(positions_one_one[0].volume / level_close, 2), level_close)
                        self.close_(tickit_one_two.order, self.round_up(positions_one_two[0].volume / level_close, 2), level_close)
                        level_close -= 1
                        break

    def sod_sang(self, tickit_one_one, tickit_one_two, tickit_two_one, tickit_two_two):
        init_balance_one = True
        init_balance_two = True
        pos = 'two'
        init = False
        while True:
            time.sleep(0.3)
            now = datetime.datetime.now(tehran_timezone)
            if 0 < now.hour < 24:
                if init_balance_one:
                    positions_one_one = mt5.positions_get(ticket=tickit_one_one.order)
                    positions_one_two = mt5.positions_get(ticket=tickit_one_two.order)
                    if positions_one_one and positions_one_two:
                        balance_one = positions_one_one[0].profit + positions_one_two[0].profit
                        if balance_one > 40 or balance_one < 0:
                            print(balance_one)
                        if balance_one > 300 and init_balance_one and pos == 'two':
                            self.close(tickit_one_one.order)
                            time.sleep(0.1)
                            self.close(tickit_one_two.order)
                            init_balance_one = False
                            pos = 'one'
                            tickit_one_one, tickit_one_two = self.run_one()
                            self.close_pos(tickit_one_one, tickit_one_two, tickit_two_one, tickit_two_two)
                            break

                if init_balance_two:
                    positions_two_one = mt5.positions_get(ticket=tickit_two_one.order)
                    positions_two_two = mt5.positions_get(ticket=tickit_two_two.order)
                    if positions_two_one and positions_two_two:
                        balance_two = positions_two_one[0].profit + positions_two_two[0].profit
                        if balance_two > 40 or balance_two < 0:
                            print(balance_two)
                        if balance_two > 300 and init_balance_two and pos == 'two':
                            self.close(tickit_two_one.order)
                            time.sleep(0.1)
                            self.close(tickit_two_two.order)
                            init_balance_two = False
                            pos = 'one'
                            tickit_two_one, tickit_two_two = self.run_two()
                            self.close_pos(tickit_one_one, tickit_one_two, tickit_two_one, tickit_two_two)
                            break
            else:
                dic_tick = {}
                jam = 0
                positions = mt5.positions_get()
                for position in positions:
                    dic_tick[position.ticket] = position.profit
                    jam += position.profit
                print('else', jam)
                if jam >= 0:
                    for i in dic_tick:
                        time.sleep(0.2)
                        self.close(i)
                        break

    def close_nith(self):
        while True:
            time.sleep(0.2)
            try:
                dic_tick = {}
                jam = 0
                positions = mt5.positions_get()
                for position in positions:
                    dic_tick[position.ticket] = position.profit
                    jam += position.profit
                print('nith close', jam)
                if jam >= 0:
                    for i in dic_tick:
                        time.sleep(0.2)
                        self.close(i)
                        break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)

    def run_one(self):
        tickit_one_one = self.buy('GBPUSD_o', 2.6, 0, 0, 'one')
        tickit_one_two = self.sell('EURUSD_o', 3, 0, 0, 'one')
        return tickit_one_one, tickit_one_two

    def run_two(self):
        tickit_two_one = self.sell('GBPUSD_o', 2.6, 0, 0, 'two')
        tickit_two_two = self.buy('EURUSD_o', 3, 0, 0, 'two')
        return tickit_two_one, tickit_two_two

    def run(self):
        self.init()
        now = datetime.datetime.now(tehran_timezone)
        if 0 < now.hour < 24:
            try:
                if len(mt5.positions_get(symbol='GBPUSD_o')) == 0 and len(mt5.positions_get(symbol='EURUSD_o')) == 0:
                    tickit_one_one = self.buy('GBPUSD_o', 2.6, 0, 0, 'one')
                    tickit_one_two = self.sell('EURUSD_o', 3, 0, 0, 'one')
                    tickit_two_one = self.sell('GBPUSD_o', 2.6, 0, 0, 'two')
                    tickit_two_two = self.buy('EURUSD_o', 3, 0, 0, 'two')
                    return tickit_one_one, tickit_one_two, tickit_two_one, tickit_two_two
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)  # Wait for 1 minute before retrying

    def main(self):
        while True:
            print(datetime.datetime.now(tehran_timezone))
            tickit_one_one, tickit_one_two, tickit_two_one, tickit_two_two = self.run()
            if tickit_one_one and tickit_one_two and tickit_two_one and tickit_two_two:
                self.sod_sang(tickit_one_one, tickit_one_two, tickit_two_one, tickit_two_two)
            time.sleep(60)

# اجرای مثال
if __name__ == "__main__":
    bot = Main()
    bot.main()
