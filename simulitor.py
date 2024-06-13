import MetaTrader5 as mt5
import pandas as pd
import threading as th
import time
import datetime
import math
import pytz
from itertools import product

tehran_timezone = pytz.timezone('Asia/Tehran')

# def init():
#     mt5.initialize(path=r"C:\Program Files\LiteFinance MT5 1\terminal64.exe")
#     mt5.login(89357646, password='Mahdi1400@', server='LiteFinance-MT5-Demo')

def get_data(symbol, timeframe, n=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert(tehran_timezone)
    df['time'] = df['time'].dt.tz_localize(None)
    df.set_index('time', inplace=True)
    return df

# Function to calculate Bollinger Bands
def bollinger_bands(price, window=20, num_of_std=2):
    rolling_mean = price.rolling(window).mean()
    rolling_std = price.rolling(window).std()
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)
    return upper_band, rolling_mean, lower_band

# Function to calculate RSI
def RSI(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to calculate MACD
def MACD(price, slow=26, fast=12, signal=9):
    exp1 = price.ewm(span=fast, adjust=False).mean()
    exp2 = price.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist

# Function to calculate indicators
def calculate_indicators(df, bb_window, bb_std, rsi_period, macd_slow, macd_fast, macd_signal):
    df['upper_band'], df['middle_band'], df['lower_band'] = bollinger_bands(df['close'], window=bb_window, num_of_std=bb_std)
    df['rsi'] = RSI(df['close'], period=rsi_period)
    df['macd'], df['signal'], df['hist'] = MACD(df['close'], slow=macd_slow, fast=macd_fast, signal=macd_signal)
    df['sma_short'] = df['close'].rolling(window=5).mean()
    df['sma_long'] = df['close'].rolling(window=20).mean()
    return df

def scalping_strategy(df, bb_window, bb_std, rsi_period, macd_slow, macd_fast, macd_signal):
    df = calculate_indicators(df, bb_window, bb_std, rsi_period, macd_slow, macd_fast, macd_signal)
    df['buy_signal'] = (df['close'] > df['lower_band']) & (df['rsi'] < 30)
    df['sell_signal'] = (df['close'] < df['upper_band']) & (df['rsi'] > 70)
    return df

def simulate_trade(df, initial_balance=10000, lot_size=0.1):
    balance = initial_balance
    position = None
    history = []

    for i in range(1, len(df)):
        if df['buy_signal'][i] and position is None:
            # Open Buy Position
            position = {'type': 'buy', 'open_price': df['close'][i], 'open_time': df.index[i]}
            print(f"Buy at {df['close'][i]} on {df.index[i]}")
        
        elif df['sell_signal'][i] and position is not None and position['type'] == 'buy':
            # Close Buy Position
            profit = (df['close'][i] - position['open_price']) * lot_size * 100000  # Assuming 1 pip = $10 for standard lot
            balance += profit
            position['close_price'] = df['close'][i]
            position['close_time'] = df.index[i]
            position['profit'] = profit
            history.append(position)
            print(f"Close Buy at {df['close'][i]} on {df.index[i]} with profit {profit}")
            position = None

        elif df['sell_signal'][i] and position is None:
            # Open Sell Position
            position = {'type': 'sell', 'open_price': df['close'][i], 'open_time': df.index[i]}
            print(f"Sell at {df['close'][i]} on {df.index[i]}")

        elif df['buy_signal'][i] and position is not None and position['type'] == 'sell':
            # Close Sell Position
            profit = (position['open_price'] - df['close'][i]) * lot_size * 100000  # Assuming 1 pip = $10 for standard lot
            balance += profit
            position['close_price'] = df['close'][i]
            position['close_time'] = df.index[i]
            position['profit'] = profit
            history.append(position)
            print(f"Close Sell at {df['close'][i]} on {df.index[i]} with profit {profit}")
            position = None

    return balance, history

def evaluate_strategy(symbol, params):
    df = get_data(symbol, mt5.TIMEFRAME_M1, 1000)
    df = scalping_strategy(df, *params)
    final_balance, trade_history = simulate_trade(df)
    total_profit = final_balance - 10000  # Assuming initial balance is 10000
    return total_profit

def optimize_parameters(symbol):
    bb_windows = [15, 20, 25]
    bb_stds = [2, 2.5, 3]
    rsi_periods = [10, 14, 20]
    macd_slows = [20, 26, 30]
    macd_fasts = [10, 12, 15]
    macd_signals = [7, 9, 12]

    best_params = None
    best_profit = -float('inf')

    for params in product(bb_windows, bb_stds, rsi_periods, macd_slows, macd_fasts, macd_signals):
        profit = evaluate_strategy(symbol, params)
        if profit > best_profit:
            best_profit = profit
            best_params = params

    return best_params

init()
# best_params = optimize_parameters('GBPUSD_o')
# print(f'Best parameters: {best_params}')

best_params = (25, 2, 20, 20, 10, 7)
# Use the best parameters in your strategy
bb_window, bb_std, rsi_period, macd_slow, macd_fast, macd_signal = best_params

# Example of running the strategy with the best parameters
symbol = 'GBPUSD_o'
df = get_data(symbol, mt5.TIMEFRAME_M1, 1000)
df = scalping_strategy(df, bb_window, bb_std, rsi_period, macd_slow, macd_fast, macd_signal)
# final_balance, trade_history = simulate_trade(df)