
import MetaTrader5 as mt5
import pandas as pd 
import threading as th
import time
from datetime import datetime, timedelta
from functools import lru_cache
import math
import pytz

import numpy as np 




tehran_timezone = pytz.timezone('Asia/Tehran')
df_pross = pd.DataFrame(columns= ['time' ,  'pros' , 'sum_trade' , 'balance'])
df_history = pd.DataFrame(columns= ['time_open' , 'time'])



def comission(lot , comission):
    return     (lot * 100) * comission


def round_up(number, precision):

  return math.ceil(number * (10**precision)) / (10**precision)


def init():
    mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 real\terminal64.exe")
    mt5.login(6910350 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Live')


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


def get_tick_data(symbol  ):
    utc_from = datetime( 2024, 5, 21, hour=8 , tzinfo=tehran_timezone)
    utc_to = datetime(2024 , 5, 23 , hour = 21, tzinfo=tehran_timezone)
    # get bars from USDJPY M5 within the interval of 2020.01.10 00:00 - 2020.01.11 13:00 in UTC time zone
    ticks = mt5.copy_ticks_range(symbol, utc_from, utc_to, mt5.COPY_TICKS_ALL)
    ticks_frame = pd.DataFrame(ticks)
    ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert(tehran_timezone)
    ticks_frame['time'] = ticks_frame['time'].dt.tz_localize(None)
    return ticks_frame
 

def get_data(symbol, timeframe):
    # تنظیم زمان‌های UTC
    utc_from = datetime( 2024, 5, 21, hour=8 , tzinfo=tehran_timezone)
    utc_to = datetime(2024 , 5, 23 , hour = 20, tzinfo=tehran_timezone)
    
    # utc_from = tehran_time_from.astimezone(pytz.utc)
    # utc_to = tehran_time_to.astimezone(pytz.utc)
    
    rates = mt5.copy_rates_range(symbol ,timeframe, utc_from,utc_to)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert(tehran_timezone)
    df['time'] = df['time'].dt.tz_localize(None)
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

# Function to calculate statistics
def calculate_statistics(df, window=20):
    df['mean_high'] = df['high'].rolling(window).mean()
    df['std_high'] = df['high'].rolling(window).std()
    df['mean_low'] = df['low'].rolling(window).mean()
    df['std_low'] = df['low'].rolling(window).std()
    
    df['high_dev_ratio'] = ((df['std_high']* 100) / df['mean_high']) * 100
    df['low_dev_ratio'] = ((df['std_low']* 100) / df['mean_low']) * 100
    
    
    return df

# Function to calculate signals
def calculate_signals(df, high_dev_threshold=7, low_dev_threshold=7):
    df['buy_signal'] = df['high_dev_ratio'] >= high_dev_threshold
    df['sell_signal'] = df['low_dev_ratio'] >= low_dev_threshold
    return df


def smooth_rng(x, t, m):
    wper = (t * 2) - 1
    avrng = x.diff().abs().rolling(window=t).mean()
    smoothrng = avrng.ewm(span=wper, adjust=False).mean() * m
    return smoothrng

def rng_filt(x, r):
    rngfilt = np.zeros_like(x)
    rngfilt[0] = x[0]  # Initial condition for the filter
    for i in range(1, len(x)):
        if x[i] > rngfilt[i - 1]:
            rngfilt[i] = rngfilt[i - 1] if (x[i] - r[i]) < rngfilt[i - 1] else (x[i] - r[i])
        else:
            rngfilt[i] = rngfilt[i - 1] if (x[i] + r[i]) > rngfilt[i - 1] else (x[i] + r[i])
    return rngfilt

def calculate_indicators_(df, per, mult):
    src = df['close']
    smrng = smooth_rng(src, per, mult)
    filt = rng_filt(src, smrng)

    df['smooth_rng'] = smrng
    df['filt'] = filt

    upward = np.zeros(len(filt))
    downward = np.zeros(len(filt))

    for i in range(1, len(filt)):
        if filt[i] > filt[i - 1]:
            upward[i] = upward[i - 1] + 1
            downward[i] = 0
        elif filt[i] < filt[i - 1]:
            downward[i] = downward[i - 1] + 1
            upward[i] = 0
        else:
            upward[i] = upward[i - 1]
            downward[i] = downward[i - 1]

    df['upward'] = upward
    df['downward'] = downward

    hband = filt + smrng
    lband = filt - smrng

    df['hband'] = hband
    df['lband'] = lband

    df['buy_signal'] = (((df['close'] > df['filt']) & (df['close'] > df['close'].shift(1)) & (df['upward'] > 0)) |
                        ((df['close'] > df['filt']) & (df['close'] < df['close'].shift(1)) & (df['upward'] > 0)))

    df['sell_signal'] = (((df['close'] < df['filt']) & (df['close'] < df['close'].shift(1)) & (df['downward'] > 0)) |
                         ((df['close'] < df['filt']) & (df['close'] > df['close'].shift(1)) & (df['downward'] > 0)))

    df['long_condition'] = df['buy_signal'] & (~df['buy_signal'].shift(1).fillna(False))
    df['short_condition'] = df['sell_signal'] & (~df['sell_signal'].shift(1).fillna(False))

    return df

# Function to calculate indicators
def calculate_indicators(df):
    df['upper_band'], df['middle_band'], df['lower_band'] = bollinger_bands(df['close'])
    # df['rsi'] = RSI(df['close'])
    # df['macd'], df['signal'], df['hist'] = MACD(df['close'])
    # df['sma_short'] = df['close'].rolling(window=5).mean()
    # df['sma_long'] = df['close'].rolling(window=20).mean()
    # df = calculate_statistics(df)
    # df = calculate_signals(df)



          

    return df


@lru_cache(maxsize=None)
def price(symbol):
    df = get_tick_data(symbol )
    return df


def write_to_csv(filename, data):
    df = pd.DataFrame(data, columns=[ 'balance' ,'symbol' , 'timeopen' , 'timeclose' , 'priceopen' , 'priceclose' , 'tp' , 'tp_' , 'sl' , 'trades' ,  'profit' , 'tp_num' ,  'reward',  'per', 'mult' ])
    try:
        existing_df = pd.read_csv(filename)
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_csv('trade_data.csv', index=False)

loc_count_one = [pd.Timestamp(datetime.now() - timedelta(days=10*365))]
loc_count_tow = [pd.Timestamp(datetime.now() - timedelta(days=10*365))]
prof_level_tow = 1000
prof_level_one = 1000
## از این تابع ها خروجی برای ساختن هستوری ایجاد شود 
# تعداد ترید و مدت زمان  ترید و وین ریت و غیره
def level_one(symbol, loc, lot, tp, sl, type_, level, df, balance, treger, reward,  per, mult):
    global prof_level_tow
    level_tp = None
    level_sl = None
    init_price = None

    iter = 0
    bissy = False
    time_biss = 0

    num_signal = treger
    global loc_count_tow

    init = True

    if treger != 0 :
        try:
            start_index = df.index.get_loc(df.index[df['time'] == loc.time][0])
        except IndexError:
            start_index = 0
    else:
        start_index = 0

    
    if loc.time > loc_count_tow[-1]  :
        # print('if')

        for index in range(start_index, len(df)):
            rows = df.iloc[index]
            
            
            
        
            # print(rows.bid ,  type_ , treger ,rows.time, loc.time ,  loc_count_tow[-1] )
            if rows.time >= loc.time :
                if type_ == "buy" and not bissy:
                    if iter == 0:
                        level_tp = rows.bid + tp
                        level_sl = rows.bid - ( tp / reward)
                        init_price = rows.bid
                        iter += 1
                        bissy = True
                        continue

                    if rows.bid >= level_tp and type_ == "buy":
                        balance = balance + (abs(init_price - rows.bid) * (lot * 100_000))
                        balance = balance - comission(lot , 0.035)
                        time_biss = rows.time
                        bissy = False
                        loc_count_tow.append(rows.time) 
                        break

                    if rows.bid <= level_sl and type_ == "buy":
                        balance = balance - (abs(init_price - rows.bid) * (lot * 100_000))
                        balance = balance - comission(lot , 0.035)
                        time_biss = rows.time
                        bissy = False
                        loc_count_tow.append(rows.time) 
                        break

                if type_ == "sell" and not bissy:
                    if iter == 0:
                        level_tp = rows.bid - tp
                        level_sl = rows.bid + ( tp / reward)
                        init_price = rows.bid
                        iter += 1
                        bissy = True
                        continue

                    if rows.bid <= level_tp and type_ == "sell" :
                        balance = balance + (abs(init_price - rows.bid) * (lot * 100_000))
                        balance = balance - comission(lot , 0.035)
                        time_biss = rows.time
                        bissy = False
                        loc_count_tow.append(rows.time) 
                        break

                    if rows.bid >= level_sl and type_ == "sell":
                        balance = balance - (abs(init_price - rows.bid) * (lot * 100_000))
                        balance = balance - comission(lot , 0.035)
                        time_biss = rows.time
                        bissy = False
                        loc_count_tow.append(rows.time) 
                        break

        prof_level_tow = (balance - 1000) + (prof_level_tow)

        init = False
        print( symbol , prof_level_tow , balance - 1000 , level)
        return balance


def level_tow(symbol, loc, lot, tp, sl, type_, level, df, balance, treger, reward,  per, mult):
    if symbol == 'USDJPY_o':
        tp = tp * 100
        lot = lot / 100
    global prof_level_tow
    zareb = 2  #  ضریب افزایش حجم باید به تابع داده شود
    level_tp = None
    level_sl = None
    init_price_buy_buy = None
    init_price__buy_sell = None

    init_price_sell_buy = None
    init_price__sell_sell = None

    iter = 0
    bissy = False
    time_biss = 0

    num_signal = treger
    on_level = None

    level_start = None

    level_buy_buy  = None 
    level_buy_sell = None

    level_sell_buy  = None 
    level_sell_sell = None

    level_tp_ = None
    level_sl_ = None

    global loc_count_tow

    buy_on = True
    sell_on = True

    buy_on_ = True
    sell_on_ = True

    sum_volum = []
    init = True

    trades = 0

    if treger != 0 :
        try:
            start_index = df.index.get_loc(df.index[df['time'] == loc.time][0])
        except IndexError:
            start_index = 0
    else:
        start_index = 0

    
    if loc.time > loc_count_tow[-1] and 8 < loc.time.hour < 21  :
        # print('if')

        for index in range(start_index, len(df)):
            rows = df.iloc[index]
            
            
            
        
            # print(rows.bid ,  type_ , treger ,rows.time, loc.time ,  loc_count_tow[-1] )
            if rows.time >= loc.time :
                # print(rows.time ,  loc.time )
                # buy init
                if type_ == "buy":
                    # print('buy')
                    
                    if type_ == "buy" and buy_on :
                        # print('init buy')
                        
                        level_tp = rows.bid + tp
                        level_buy_buy  = rows.bid 
                        level_buy_sell = rows.bid - ( tp / reward)
                        init_price_buy_buy = rows.bid
                        iter += 1
                        buy_on = False
                        on_level = 'buy'
                        sum_volum.append(lot)
                        trades += 1
                        continue

                    # buy tp
                    
                    if rows.bid >= level_tp and on_level == 'buy' and type_ == "buy" and sell_on and not buy_on:
                        # print(1)
                        balance = balance + (abs(level_buy_buy - rows.bid ) * (lot * 100_000))
                        balance = balance - comission(lot , 0.035)
                        loc_count_tow.append(rows.time) 
                        break

                    # sell init
                    
                    if rows.bid <= level_buy_sell and on_level == 'buy' and type_ == "buy" and sell_on and not buy_on:
                        # print(2)
                        
                        init_price_buy_sell = rows.bid
                        level_tp_ = rows.bid - tp
                        level_sl_ = init_price_buy_buy
                        on_level = 'sell'
                        loc_count_tow.append(rows.time) 
                        sell_on = False
                        continue

                    # sell tp
                    
                    if not sell_on:
                        
                        if rows.bid <= level_tp_ and on_level == 'sell' and type_ == "buy" and not buy_on  :
                            # print(3)
                            sum_volum.append(round_up(lot * zareb , 2))
                            balance = balance + (abs(init_price_buy_sell - rows.bid) * ((round_up(lot * zareb , 2)) * 100_000))
                            balance = balance - (abs(init_price_buy_buy - rows.bid) * (lot * 100_000))
                            balance = balance - comission(sum(sum_volum) , 0.035)
                            loc_count_tow.append(rows.time) 
                            break

                    # sl 
                    
                    if not sell_on:

                        if rows.bid >= level_sl_ and on_level == 'sell' and type_ == "buy" and not buy_on :
                            # print(4)
                            balance = balance - (abs(init_price_buy_sell - rows.bid) * ((round_up(lot * zareb , 2)) * 100_000))
                            balance = balance - (abs(init_price_buy_buy - rows.bid) * (lot * 100_000))
                            balance = balance - comission(sum(sum_volum) , 0.035)
                            loc_count_tow.append(rows.time) 
                            break




                # init sell
                if type_ == "sell":
                    

                    if type_ == "sell" and sell_on_ :
                        # print('sell')
                        level_tp = rows.bid - tp
                        level_sell_sell  = rows.bid 
                        level_sell_buy = rows.bid + ( tp / reward)
                        init_price_sell_sell = rows.bid
                        iter += 1
                        sell_on_ = False
                        on_level = 'sell'
                        sum_volum.append(lot)
                        trades += 1
                        continue

                    
                    # sell tp
                    # print(5)
                    if rows.bid <= level_tp and on_level == 'sell' and type_ == "sell" and buy_on_ and not sell_on_:
                        balance = balance + (abs(level_sell_sell - rows.bid ) * (lot * 100_000))
                        balance = balance - comission(lot , 0.035)
                        loc_count_tow.append(rows.time) 
                        break

                    # buy init
                    # print(6)
                    if rows.bid >= level_sell_buy and on_level == 'sell' and type_ == "sell" and buy_on_ and not sell_on_:
                        
                        init_price_sell_buy = rows.bid
                        level_tp_ = rows.bid + tp
                        level_sl_ = init_price_sell_sell
                        on_level = 'buy'
                        loc_count_tow.append(rows.time) 
                        buy_on_ = False
                        continue

                    # buy tp
                    # print(7)
                    if not buy_on_ : 
                        if rows.bid >= level_tp_ and on_level == 'buy' and type_ == "sell" and   not sell_on_:
                            sum_volum.append(round_up(lot * zareb , 2))
                            balance = balance + (abs(init_price_sell_buy - rows.bid) * ((round_up(lot * zareb , 2)) * 100_000))
                            balance = balance - (abs(init_price_sell_sell - rows.bid) * (lot * 100_000))
                            balance = balance - comission(sum(sum_volum) , 0.035)
                            loc_count_tow.append(rows.time) 
                            break

                    # func sl
                    # print(8)
                    if not buy_on_ : 
                        if rows.bid <= level_sl_ and on_level == 'buy' and type_ == "sell" and not sell_on_:
                            balance = balance - (abs(init_price_sell_buy - rows.bid) * ((round_up(lot * zareb , 2)) * 100_000))
                            balance = balance - (abs(init_price_sell_sell - rows.bid) * (lot * 100_000))
                            balance = balance - comission(sum(sum_volum) , 0.035)
                            loc_count_tow.append(rows.time) 
                            break

        prof_level_tow = (balance - 1000) + (prof_level_tow)

        init = False
        print( symbol , prof_level_tow , balance - 1000 , reward , tp , loc.time  )
                #['symbol', 'prof_level_tow', 'balance', 'reward', 'tp', 'loc_time']
                #['symbol' , 'timeopen' , 'timeclose' , 'priceopen' , 'priceclose' , tp , tp_ , sl , balance , profit , reward]
        data = [[prof_level_tow,symbol , loc.time ,rows.time , loc.open , rows.bid , level_tp_ ,level_tp , level_sl_ ,trades ,   balance - 1000, tp , reward,  per, mult]]
        #data = [[symbol, prof_level_tow, balance - 1000, reward, tp, loc.time]]

       
        write_to_csv('trade_data.csv', data)
        return balance


def level_tree(symbol , loc , lot , tp , sl , type_ , level , df, balance):

    for idex , rows in  df.iterrows():
 
 
        if rows.time == loc.time :
            pass


def level_for(symbol , loc , lot , tp , sl , type_ , level , df, balance):

    for idex , rows in  df.iterrows():
 
 
        if rows.time == loc.time :
            pass


def level_five(symbol , loc , lot , tp , sl , type_ , level , df, balance):

    for idex , rows in  df.iterrows():
 
 
        if rows.time == loc.time :
            pass



def trade_up(symbol , loc , lot , tp , sl , type_ , level , balance , treger , reward,  per, mult):

    df = price(symbol)
    if level == 1 : 
        return level_one(symbol , loc , lot , tp , sl , type_ , level , df, balance, treger, reward,  per, mult)
    if level == 2 : 
        return level_tow(symbol , loc , lot , tp , sl , type_ , level , df, balance, treger, reward,  per, mult)
    # if level == 3 : 
    #     return level_tree(symbol , loc , lot , tp , sl , type_ , level , df, balance, treger, reward)
    # if level == 4 : 
    #     return level_for(symbol , loc , lot , tp , sl , type_ , level , df, balance, treger, reward)
    # if level == 5 : 
    #     return level_five(symbol , loc , lot , tp , sl , type_ , level , df, balance, treger, reward)


biz = False
def simolet(loc , type_ , symbol , level , treger  , lot , tp , sl , reward ,  per, mult ) :
    

    
    return trade_up(symbol , loc , lot , tp , sl , type_ , level , 1000 , treger , reward,  per, mult )




def scalping_strategy(symbol , level , lot , tp , sl , reward ,  per, mult):
    df= get_data(symbol, mt5.TIMEFRAME_M5)
    # df = calculate_indicators(df)

    df = calculate_indicators_(df ,  per, mult)
    
    

    for i in range(1, len(df)):
        # buy_signal = (df['close'][i] > df['lower_band'][i]) and (df['rsi'][i] > 30) and (df['macd'][i] > df['signal'][i]) and (df['sma_short'][i] > df['sma_long'][i])
        # sell_signal = (df['close'][i] < df['upper_band'][i]) and (df['rsi'][i] < 70) and (df['macd'][i] < df['signal'][i]) and (df['sma_short'][i] < df['sma_long'][i])

        # buy_signal = (df['close'][i] < df['lower_band'][i]) and df['long_condition'][i]
        # sell_signal = (df['close'][i] > df['upper_band'][i]) and df['short_condition'][i]

        # buy_signal = (df['rsi'][i] < 30) 
        # sell_signal =  (df['rsi'][i] > 70) 

        # buy_signal = df['buy_signal'][i]  
        # sell_signal = df['sell_signal'][i] 

        buy_signal = df['long_condition'][i]
        sell_signal = df['short_condition'][i]


        # buy_signal = (df['close'][i] < df['lower_band'][i]) 
        # sell_signal = (df['close'][i] > df['upper_band'][i])

        if buy_signal:
            # print(f'simolet buy {df.loc[i]  , symbol , level, i}')
            simolet(df.loc[i] ,  'buy' , symbol , level, i , lot , tp , sl  , reward,  per, mult )  # balance
            

        if sell_signal:
            # print(f'simolet sell {df.loc[i]  , symbol , level , i}')
            simolet(df.loc[i] ,  'sell' , symbol , level , i  , lot , tp , sl , reward,  per, mult )

            
    global loc_count_one
    loc_count_one.clear()
    loc_count_one = [pd.Timestamp(datetime.now() - timedelta(days=10*365))]

    global loc_count_tow
    loc_count_tow.clear()
    loc_count_tow = [pd.Timestamp(datetime.now() - timedelta(days=10*365))]

    global prof_level_tow
    print('scalping', prof_level_tow)
    prof_level_tow = 0        



def run():
    init()

    now = datetime.now(tehran_timezone)
    # if 9 < now.hour < 22:
    per_values = [ 50, 75 , 100, 150]
    mult_values = [ 2.0, 3.0, 4.0]
    # per_values = [ 50 ,  100]
    # mult_values = [ 2.0]
    
    # symbols = ['USDJPY_o', 'GBPUSD_o','EURUSD_o' , 'USDCAD_o', 'USDCHF_o' ]
    symbols = ['GBPUSD_o']
    param_combinations = [

        
        (2, 0.1, 0.0009, 0.0005, 3),
        (2, 0.1, 0.0012, 0.0005, 3),
        (2, 0.1, 0.0015, 0.0005, 3),
        (2, 0.1, 0.0018, 0.0005, 3),
        (2, 0.1, 0.0020, 0.0005, 3),
        (2, 0.1, 0.001, 0.0005, 4),
        (2, 0.1, 0.0012, 0.0005, 4),
        (2, 0.1, 0.0015, 0.0005, 4),
        (2, 0.1, 0.0018, 0.0005, 4),
        (2, 0.1, 0.0020, 0.0005, 4),
        (2, 0.1, 0.001, 0.0005, 5),
        (2, 0.1, 0.0012, 0.0005, 5),
        (2, 0.1, 0.0015, 0.0005, 5),
        (2, 0.1, 0.0018, 0.0005, 5),
        (2, 0.1, 0.0020, 0.0005, 5)
    ]

    try:
        for per in per_values:
            for mult in mult_values:
                for symbol in symbols:
                    for params in param_combinations:
                        scalping_strategy(symbol, *params, per, mult)
                        global prof_level_tow
                        prof_level_tow = 1000
    except Exception as e:
        print(f"Error: {e}")


print(datetime.now(tehran_timezone))
run()

