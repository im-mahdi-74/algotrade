

import MetaTrader5 as mt5
import pandas as pd 
import threading as th
import time
import datetime

import math
import pytz
import numpy as np
import json
import streamlit as st
import subprocess
import os
from PIL import Image


st.set_page_config(

    page_title= 'جوقول دیار خسته ها',
    page_icon= 'hot'
    #layout= 'wide'
    )



st.title("زنده باد جوقول دیار خسته ها")

st.warning(' استراتژی سید خسته جوقولی دستی شده توسط اقا سید مهدی  ')

def init( ):
    # mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 real\terminal64.exe")
    # mt5.login(6910350 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Live')
    mt5.initialize(path = r"C:\Program Files\LiteFinance MT5 2\terminal64.exe")
    mt5.login(89373537 , password= 'Mahdi1400@' , server= 'LiteFinance-MT5-Demo')


def hand():




        option_symbol = st.selectbox(
        "نماد ?",
        ("EURUSD_o", "GBPUSD_o", "USDJPY_o" , "USDCHF_o" , "AUDUSD_o" , "NZDUSD_o" , "USDCAD_o"),
        index=None,
        placeholder="نماد را دی کدی",
        key = 'option_symbol')
        if option_symbol :
            vol = st.number_input("حجم را دی کن" , key= 'vol')

            option_type = st.selectbox(
            "خرید  یا فروش ?",
            ("buy" , "sell"),
            index=None,
            placeholder= "نوع معامله را دی کن",
            key = 'option_type')

            option_tp = st.selectbox(
            "سود به پیپ ?",
            ("4", "5", "6" , "7" , "8" , "9" , "10" , "11" , "12" , "13" , "14" , "15" , "16" , "17" , "18" , "19" , "20"),
            index=None,
            placeholder="سود را دی کدی",
            key = 'option_tp')

            option_level = st.selectbox(
            "لول به پیپ ?",
            ("2" , "3" , "4", "5", "6" , "7" , "8" , "9" , "10" ),
            index=None,
            placeholder="لول را دی کدی",
            key = 'option_level')

            if option_symbol and vol and option_type and option_tp and option_level :

                run = st.button('انجام معامله')
                if run:
                    init()
                    
                    current_dir = os.path.dirname(os.path.realpath(__file__))
                    
                    # مسیر فایل پارامترها
                    params_file_path = os.path.join(current_dir, 'params.json')
                    if os.path.exists(params_file_path):
                        # اگر وجود دارد، آن را حذف کنید
                        os.remove(params_file_path)
                        print(f"فایل {params_file_path} با موفقیت حذف شد.")

                    with open(params_file_path, "w") as file:
                        if len(mt5.positions_get(symbol=option_symbol)) == 0:
                            params = {
                                "symbol": option_symbol,
                                "type": option_type,
                                "vol": float(vol),
                                # "tp": float(option_tp) / 100 if option_symbol == "USDJPY_o" else float(option_tp) / 10000,
                                "tp" : option_tp ,
                                # "level": float(option_level) / 100 if option_symbol == "USDJPY_o" else float(option_level) / 10000,
                                "level" : option_level,
                                'None': 3,
                                "price": mt5.symbol_info_tick(option_symbol).bid if option_type == 'buy' else mt5.symbol_info_tick(option_symbol).ask
                            }

                            json.dump(params, file)

                            try:
                                directory_path = os.path.dirname(__file__)

                                # مسیر کامل فایل sag_dast_streamlit_.py را بسازید
                                full_path = os.path.join(directory_path, "sag_dast_streamlit_.py")

                                # با استفاده از subprocess برای اجرای فایل با کنترل بیشتر استفاده کنید
                                subprocess.Popen(["python", full_path])
                            except Exception as e:
                                st.write(e)



                    st.write(st.session_state)
                    time.sleep(1)
                    if len(st.session_state.keys()) > 0 :
                        for key in st.session_state.keys():
                            del st.session_state[key]





if __name__ == "__main__":



    hand()

image = Image.open(f'{os.path.dirname(__file__)}\jo.jpg')
st.image(image, caption=" جوقول")
    