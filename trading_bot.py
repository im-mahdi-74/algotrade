import MetaTrader5 as mt5
import pandas as pd
import threading as th
import time
import datetime
import math
import pytz
import logging

# تنظیم منطقه زمانی
tehran_timezone = pytz.timezone('Asia/Tehran')

# تنظیمات لاگینگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger()

# کلاس برای مدیریت حساب و عملیات‌های تجاری
class TradingBot:
    def __init__(self, path, login, password, server):
        self.path = path
        self.login = login
        self.password = password
        self.server = server
        self.df_pross = pd.DataFrame(columns=['time', 'pros', 'sum_trade', 'balance'])
        self.init_mt5()

    def init_mt5(self):
        if not mt5.initialize(path=self.path):
            logger.error("initialize() failed, error code =", mt5.last_error())
            quit()
        if not mt5.login(self.login, password=self.password, server=self.server):
            logger.error("login() failed, error code =", mt5.last_error())
            quit()

    def get_account_info(self):
        account_info = mt5.account_info()
        return account_info.balance, account_info.equity, account_info.profit

    @staticmethod
    def round_up(number, precision):
        return math.ceil(number * (10 ** precision)) / (10 ** precision)

    @staticmethod
    def get_symbol_info(symbol):
        group_symbols = mt5.symbols_get(group='*USD*')
        for s in group_symbols:
            if s.name == symbol:
                return {s.name: (s.ask, s.bid)}
        return {}

    @staticmethod
    def get_data(symbol, timeframe, n=50):
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert(tehran_timezone)
        df['time'] = df['time'].dt.tz_localize(None)
        df.set_index('time', inplace=True)
        return df

    @staticmethod
    def bollinger_bands(price, window=20, num_of_std=2):
        rolling_mean = price.rolling(window).mean()
        rolling_std = price.rolling(window).std()
        upper_band = rolling_mean + (rolling_std * num_of_std)
        lower_band = rolling_mean - (rolling_std * num_of_std)
        return upper_band, rolling_mean, lower_band

    @staticmethod
    def rsi(series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def macd(price, slow=26, fast=12, signal=9):
        exp1 = price.ewm(span=fast, adjust=False).mean()
        exp2 = price.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        hist = macd - signal_line
        return macd, signal_line, hist

    @staticmethod
    def calculate_indicators(df):
        df['upper_band'], df['middle_band'], df['lower_band'] = TradingBot.bollinger_bands(df['close'])
        df['rsi'] = TradingBot.rsi(df['close'])
        # Uncomment the following lines if needed
        # df['macd'], df['signal'], df['hist'] = TradingBot.macd(df['close'])
        # df['sma_short'] = df['close'].rolling(window=5).mean()
        # df['sma_long'] = df['close'].rolling(window=20).mean()
        return df

    def send_order(self, symbol, lot, tp_, sl_, order_type):
        if order_type == "buy":
            tp = abs(mt5.symbol_info_tick(symbol).bid + tp_)
            sl = abs(mt5.symbol_info_tick(symbol).ask - sl_)
            order_type = mt5.ORDER_TYPE_BUY
        else:
            tp = abs(mt5.symbol_info_tick(symbol).ask - tp_)
            sl = abs(mt5.symbol_info_tick(symbol).bid + sl_)
            order_type = mt5.ORDER_TYPE_SELL

        lot = self.round_up(lot, 2)
        price = mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
        deviation = 100
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": 234002,
            "comment": "PythonBot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order send failed, retcode={result.retcode}, request={request}")
            return False
        return True

    def close_position(self, symbol):
        positions = mt5.positions_get(symbol=symbol)
        for position in positions:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": position.ticket,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_BUY if position.type == mt5.ORDER_TYPE_SELL else mt5.ORDER_TYPE_SELL,
                "price": mt5.symbol_info_tick(position.symbol).bid if position.type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(position.symbol).ask,
                "deviation": 100,
                "magic": 234002,
                "comment": "PythonBot",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Close position failed, retcode={result.retcode}, request={request}")
                return False
        return True

    def trade(self, symbol, lot, tp, sl, direction):
        if direction == 'buy':
            self.send_order(symbol, lot, tp, sl, "buy")
        else:
            self.send_order(symbol, lot, tp, sl, "sell")

    def scalping_strategy(self, symbol):
        df = self.get_data(symbol, mt5.TIMEFRAME_M1)
        df = self.calculate_indicators(df)

        for i in range(1, len(df)):
            buy_signal = (df['close'][i] > df['lower_band'][i]) and (df['rsi'][i] < 30)
            sell_signal = (df['close'][i] < df['upper_band'][i]) and (df['rsi'][i] > 70)

            if buy_signal:
                return 'buy'
            if sell_signal:
                return 'sell'
        return None

    def run(self):
        while True:
            now = datetime.datetime.now(tehran_timezone)
            if 9 < now.hour < 22:
                try:
                    for symbol, lot, tp, sl in [('GBPUSD_o', 0.05, 0.0005, 0.01), ('USDJPY_o', 0.1, 0.05, 0.05), ('USDCHF_o', 0.05, 0.0005, 0.0006)]:
                        signal = self.scalping_strategy(symbol)
                        if signal == 'buy' and len(mt5.positions_get(symbol=symbol)) == 0:
                            th.Thread(target=self.trade, args=(symbol, lot, tp, sl, 'buy')).start()
                        if signal == 'sell' and len(mt5.positions_get(symbol=symbol)) == 0:
                            th.Thread(target=self.trade, args=(symbol, lot, tp, sl, 'sell')).start()
                except Exception as e:
                    logger.error(f"Error in run method: {e}")
                    time.sleep(60)  # Wait for 1 minute before retrying
            time.sleep(10)

if __name__ == "__main__":
    bot = TradingBot(path=r"C:\Program Files\LiteFinance MT5 real\terminal64.exe", login=6910350, password='Mahdi1400@', server='LiteFinance-MT5-Live')
    bot.run()
