#거래랑 비교 후 k 값 산정

import time
import pyupbit
import datetime
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import requests

name = "SHERRY"
access = "x70SQ3jOuppQBeedtfUNqMhSHZzCBLtc7CJ8CEvz"
secret = "XnuKCo7vOxrsbd92PpAKB4sbsSgvn6pIGOwuz1uy"

original_coin_list = ["BTC", "BCH", "BSV", "BTG", "ETH",
                      "XRP", "ADA", "SOL", "DOGE", "STX",
                      "VET", "LINK", "AVAX", "SAND", "WAXP",
                      "ATOM", "STRAX", "ETC", "QTUM", "PDA",
                      "GAS", "SOL", "TON", "ONG"]

additional_coins = ["BTC", "ETH", "LINK", "GAS", "SOL", "ETC", "QTUM"] #240228_추가

find_date = 10
ma_date = 5
cut_rate_overraise = 1.15  #전일 상승폭이 너무 높은 코인 제외

buy_rate = [0.34, 0.33, 0.33]
emergency_sell_rate = [1.06, 1.06, 1.06]

def send_message(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"\n■[{now.strftime('%m/%d %H:%M:%S')}][{str(name)}]■\n{str(msg)}\n"}
    requests.post(DISCORD_WEBHOOK_URL, data=message)
    print(message)

###여기서 부터는 같음###    
    
fee = 0.0005  # trade fee # upbit
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1214595525458919444/gcMwVip7NUESb0NPu2O-BnRhooqqZlkVUk7BiCKXt8KCr4HkWmUOWiPtPq9VYignYw7R"

# 오늘 날짜를 yymmdd 형식으로 가져옵니다.
today_date = datetime.datetime.now().strftime('%y%m%d')

def filtered_ma(ma_date, max_retry_count=10):
    ma_up_coin_list = []

    for coin in original_coin_list:
        retry_count = 0
        while retry_count < max_retry_count:
            try:
                ohlcv_name = "KRW-" + coin
                df_1 = pyupbit.get_ohlcv(ohlcv_name, interval="day", count=ma_date)
                if df_1 is not None:  # 데이터가 없는 경우 처리
                    ma5 = df_1['close'].mean()  # MA5 계산
                    current_price = pyupbit.get_current_price(ohlcv_name)  # 현재 가격
                    print(coin,current_price, ma5)
                    if current_price > ma5:  # 현재 가격이 MA5보다 높으면
                        ma_up_coin_list.append(coin)
                    break

            except Exception as e:
                retry_count += 1
                print(f"오류 발생 ({coin}): {e}, 재시도 횟수: {retry_count}")

    if len(ma_up_coin_list) <= 5:
        for coin in additional_coins:
            if coin not in ma_up_coin_list:
                ma_up_coin_list.append(coin)
    
    # 중복 제거
    ma_up_coin_list = list(set(ma_up_coin_list))
    print("ma_filtered:",ma_up_coin_list)

    return ma_up_coin_list

def filtered_upcut(cut_rate_overraise, ma_up_coin_list, max_retry_count=10):
    trade_coin_list = []

    for coin in ma_up_coin_list:
        retry_count = 0
        while retry_count < max_retry_count:
            try:
                ohlcv_name = "KRW-" + coin
                df_1 = pyupbit.get_ohlcv(ohlcv_name, interval="day", count=2)

                # 오늘과 어제의 종가 값을 가져옴
                today_close = df_1['close'].iloc[-1]
                yesterday_close = df_1['close'].iloc[0]

                # 가격이 오늘보다 어제보다 증가율을 계산        
                price_increase_rate = today_close / yesterday_close
                print(coin,"increase rate:", price_increase_rate)

                # 증가율이 cut_rate_overraise 보다 큰 경우 trade_coin_list 에 추가하지 않음
                if price_increase_rate < cut_rate_overraise:
                    trade_coin_list.append(coin)
                    break

            except Exception as e:
                retry_count += 1
                print(f"오류 발생 ({coin}): {e}, 재시도 횟수: {retry_count}")

    if len(trade_coin_list) <= 5:
        for coin in additional_coins:
            if coin not in trade_coin_list:
                trade_coin_list.append(coin)
    
    # 중복 제거
    trade_coin_list = list(set(trade_coin_list))

    return trade_coin_list


def get_coin_kvalue(trade_coin_list, find_date, fee):
    today_date = datetime.datetime.now().strftime('%y%m%d')

    data = {'trade_coin': [], 'k_value': [], 'last_hpr': []}
    for trade_coin in trade_coin_list:
        msg = trade_coin
        send_message(msg)
        print(trade_coin)
        try:
            for k in np.arange(0.2, 0.51, 0.02):
                k_value = np.round(k, 3)
                ohlcv_name = "KRW-" + trade_coin
                df = pyupbit.get_ohlcv(ohlcv_name, count=find_date)
                if df is not None:
                    df['range'] = (df['high'] - df['low']) * k_value
                    df['target'] = df['open'] + df['range'].shift(1)
                    df['ror'] = np.round(np.where(df['high'] > df['target'], df['close'] / df['target'] - fee, 1), 4)
                    df['hpr'] = np.round(df['ror'].cumprod(), 4)
                    df['dd'] = np.round((df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100, 4)

                    last_hpr = round((df['hpr'].iloc[-1] - 1) * 100, 3)
                    
                    # 데이터 테이블에 값 추가
                    data['trade_coin'].append(trade_coin)
                    data['k_value'].append(k_value)
                    data['last_hpr'].append(last_hpr)
        except Exception as e:
            print(f"오류 발생: {e}")
            continue  # 다음 코인으로 넘어감

    if not data['trade_coin']:  # 데이터가 비어 있으면 반환
        return "", "", ""

    df_table = pd.DataFrame(data)  

    # 최고 수익률을 가진 코인과 k 값을 찾기
    df_table_sorted = df_table.sort_values(by='last_hpr', ascending=False)
    no1_coin = df_table_sorted.iloc[0]['trade_coin']
    no1_k = df_table_sorted.iloc[0]['k_value']
    no1_hpr = df_table_sorted.iloc[0]['last_hpr']

    # 가장 높은 수익률을 가진 코인 데이터 삭제
    df_table = df_table[df_table['trade_coin'] != no1_coin]

    # 두 번째로 높은 수익률을 가진 코인과 k 값을 찾기
    df_table_sorted = df_table.sort_values(by='last_hpr', ascending=False)
    no2_coin = df_table_sorted.iloc[0]['trade_coin']
    no2_k = df_table_sorted.iloc[0]['k_value']
    no2_hpr = df_table_sorted.iloc[0]['last_hpr']

    # 가장 높은 수익률을 가진 코인 데이터 삭제
    df_table = df_table[df_table['trade_coin'] != no2_coin]

    # 세 번째로 높은 수익률을 가진 코인과 k 값을 찾기
    df_table_sorted = df_table.sort_values(by='last_hpr', ascending=False)
    no3_coin = df_table_sorted.iloc[0]['trade_coin']
    no3_k = df_table_sorted.iloc[0]['k_value']
    no3_hpr = df_table_sorted.iloc[0]['last_hpr']

    return no1_coin, no1_k, no1_hpr, no2_coin, no2_k, no2_hpr, no3_coin, no3_k, no3_hpr



def get_target_price_gap(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="day", count=1)  # count를 1로 수정
        if df is None:
            raise ValueError("Failed to retrieve data for {}".format(ticker))
        
        target_price_gap = (df.iloc[0]['high'] - df.iloc[0]['low']) * k
        return target_price_gap
    except Exception as e:
        print("Error occurred:", e)
        return None

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_earning_msg(selected_coin, sell_mny, earning):
    earning_sign = '+' if earning >= 0 else '-'
    earning_abs = abs(earning)
    earning_rate = round(earning / (sell_mny - earning) * 100, 1)
    return ("    ☎매도 Coin : {0}\n"
            "           판매금액 : {1:,}원\n"
            "                   수익 : {2}{3:,}원\n"
            "               수익율 : {5}%").format(selected_coin, sell_mny, earning_sign, earning_abs, earning_sign, earning_rate)

def get_ma5_compare(ticker):
    df_ma5 = pyupbit.get_ohlcv(ticker, interval="minute1", count=5)
    ma5_close = df_ma5['close'].mean()
    return ma5_close


# 로그인
upbit = pyupbit.Upbit(access, secret)

msg = "Auto Trade Start"
send_message(msg)
print(msg)

# 자동매매 시작
no1_coin, no1_k, no1_hpr, no1_trade_msg, no1_buy_msg, no1_sell_msg = "", "", "", "", "", ""
no2_coin, no2_k, no2_hpr, no2_trade_msg, no2_buy_msg, no2_sell_msg = "", "", "", "", "", ""
no3_coin, no3_k, no3_hpr, no3_trade_msg, no3_buy_msg, no3_sell_msg = "", "", "", "", "", ""
total_sell_msg = ""

no1_coin_buy, no2_coin_buy, no3_coin_buy = 0, 0, 0
no1_sell_mny, no2_sell_mny, no3_sell_mny = 0, 0, 0
no1_earning, no2_earning, no3_earning = 0, 0, 0

no1_selected_coin, no2_selected_coin, no3_selected_coin = "", "", ""

while True:
    try:
        now = datetime.datetime.now().time()
        trade_start_time = datetime.time(8, 0, 0)
        trade_end_time = datetime.time(8, 40, 0)

        if trade_start_time > now or now > trade_end_time:
            print(trade_start_time,"~",trade_end_time)
            if no1_coin == "" and no2_coin == "" and no3_coin == "":
                msg = "calculate best trade volume coin"
                send_message(msg)
                print(msg)

                ma_up_coin_list = filtered_ma(ma_date)
                msg = "Up_MA5 list :" + str(ma_up_coin_list)
                send_message(msg)
                print(msg)                
                
                trade_coin_list = filtered_upcut(cut_rate_overraise, ma_up_coin_list)
                msg = "Up_Cut list :" + str(trade_coin_list)
                send_message(msg)
                print(msg)

                msg = "calculate best coin and k-value"
                send_message(msg)
                print(msg)

                no1_coin, no1_k, no1_hpr, no2_coin, no2_k, no2_hpr, no3_coin, no3_k, no3_hpr = get_coin_kvalue(trade_coin_list, find_date, fee)

                msg_no1 = "   no1_Trade Coin:" + str(no1_coin) + "\n   K-value:" + str(no1_k) + "\n   일 평균수익:" + str(round(no1_hpr/find_date, 1)) + "%"
                send_message(msg_no1)
                print(msg_no1)
                msg_no2 = "   no2_Trade Coin:" + str(no2_coin) + "\n   K-value:" + str(no2_k) + "\n   일 평균수익:" + str(round(no2_hpr/find_date, 1)) + "%"
                send_message(msg_no2)
                print(msg_no2)
                msg_no3 = "   no3_Trade Coin:" + str(no3_coin) + "\n   K-value:" + str(no3_k) + "\n   일 평균수익:" + str(round(no3_hpr/find_date, 1)) + "%"
                send_message(msg_no3)
                print(msg_no3)

                no1_selected_coin = "KRW-" + no1_coin
                no2_selected_coin = "KRW-" + no2_coin
                no3_selected_coin = "KRW-" + no3_coin
                
                no1_target_price_base = get_current_price(no1_selected_coin)
                no2_target_price_base = get_current_price(no2_selected_coin)
                no3_target_price_base = get_current_price(no3_selected_coin)
                
                krw = get_balance("KRW")
                print(now.strftime('%Y.%m.%d %H:%M:%S - '),"지갑에 ",krw,"원이 있습니다")
                no1_coin_buy = float(buy_rate[0] * krw * 0.9995)
                no2_coin_buy = float(buy_rate[1] * krw * 0.9995)
                no3_coin_buy = float(buy_rate[2] * krw * 0.9995)                
                
            
            
            no1_current_price = get_current_price(no1_selected_coin)
            print("no1_current_price :",no1_current_price)
            if no1_target_price_base > no1_current_price:
                no1_target_price_base = get_current_price(no1_selected_coin)
            no1_target_price_gap = get_target_price_gap(no1_selected_coin, no1_k)
            no1_target_price = no1_target_price_base + no1_target_price_gap
            print("no1_target_price_base:",no1_target_price_base)
            print("no1_target_price_gap:",no1_target_price_gap)
            print("no1_k:",no1_k)
            print("no1_target_price:",no1_target_price)
            if no1_buy_msg == "" :
                no1_emer_sell_price = float(no1_target_price * emergency_sell_rate[0])
                print("no1_emer_sell_price", no1_emer_sell_price)
            
            no2_current_price = get_current_price(no2_selected_coin)
            if no2_target_price_base > no2_current_price:
                no2_target_price_base = get_current_price(no2_selected_coin)
            no2_target_price_gap = get_target_price_gap(no2_selected_coin, no2_k)
            no2_target_price = no2_target_price_base + no2_target_price_gap
            if no2_buy_msg == "" :
                no2_emer_sell_price = float(no2_target_price * emergency_sell_rate[1])
            
            no3_current_price = get_current_price(no3_selected_coin)
            if no3_target_price_base > no3_current_price:
                no3_target_price_base = get_current_price(no3_selected_coin)
            no3_target_price_gap = get_target_price_gap(no3_selected_coin, no3_k)
            no3_target_price = no3_target_price_base + no3_target_price_gap
            if no3_buy_msg == "" :
                no3_emer_sell_price = float(no3_target_price * emergency_sell_rate[2])
                                                  
            if no1_trade_msg == "":
                no1_trade_msg = ("   ▶시작no1_Coin: {}\n"
                                "       current_price: {:,.1f}\n"
                                "          target_price: {:,.1f}").format(no1_coin, round(no1_current_price, 1), round(no1_target_price, 1))
                send_message(no1_trade_msg)
                print(no1_trade_msg)

            if no2_trade_msg == "":
                no2_trade_msg = ("   ▶시작no2_Coin: {}\n"
                                "       current_price: {:,.1f}\n"
                                "          target_price: {:,.1f}").format(no2_coin, round(no2_current_price, 1), round(no2_target_price, 1))
                send_message(no2_trade_msg)
                print(no2_trade_msg)

            if no3_trade_msg == "":
                no3_trade_msg = ("   ▶시작no3_Coin: {}\n"
                                "       current_price: {:,.1f}\n"
                                "          target_price: {:,.1f}").format(no3_coin, round(no3_current_price, 1), round(no3_target_price, 1))
                send_message(no3_trade_msg)
                print(no3_trade_msg)

            if no1_target_price < no1_current_price and no1_buy_msg == "":
                krw = get_balance("KRW")
                print(now.strftime('%Y.%m.%d %H:%M:%S - '),"지갑에 ",krw,"원이 있습니다")
                if krw > 5000 and no1_buy_msg == "":
                    upbit.buy_market_order(no1_selected_coin, no1_coin_buy)###매매 코드
                    no1_buy_msg = "     ♬매수 no1_Coin: {}\n                                    {}원".format(no1_selected_coin, format(int(no1_coin_buy), ','))
                    send_message(no1_buy_msg)
                    print(now.strftime('%Y.%m.%d %H:%M:%S - '), no1_selected_coin,"를 ",round(no1_coin_buy, 2),"원 구매했습니다")
                    no1_sell_msg = ""
                    no1_emer_sell_price = float(no1_target_price * emergency_sell_rate[0])
                    print("판매후 가격 결정", no1_emer_sell_price)

            if no2_target_price < no2_current_price and no2_buy_msg == "":
                krw = get_balance("KRW")
                print(now.strftime('%Y.%m.%d %H:%M:%S - '),"지갑에 ",krw,"원이 있습니다")
                if krw > 5000 and no2_buy_msg == "":
                    upbit.buy_market_order(no2_selected_coin, no2_coin_buy)###매매 코드
                    no2_buy_msg = "     ♬매수 no2_Coin: {}\n                                    {}원".format(no2_selected_coin, format(int(no2_coin_buy), ','))
                    send_message(no2_buy_msg)
                    print(now.strftime('%Y.%m.%d %H:%M:%S - '), no2_selected_coin,"를 ",round(no2_coin_buy, 2),"원 구매했습니다")
                    no2_sell_msg = ""
                    no2_emer_sell_price = float(no2_target_price * emergency_sell_rate[1])

            if no3_target_price < no3_current_price and no3_buy_msg == "":
                krw = get_balance("KRW")
                print(now.strftime('%Y.%m.%d %H:%M:%S - '),"지갑에 ",krw,"원이 있습니다")
                if krw > 5000 and no3_buy_msg == "":
                    upbit.buy_market_order(no3_selected_coin, no3_coin_buy)###매매 코드
                    no3_buy_msg = "     ♬매수 no3_Coin: {}\n                                    {}원".format(no3_selected_coin, format(int(no3_coin_buy), ','))
                    send_message(no3_buy_msg)
                    print(now.strftime('%Y.%m.%d %H:%M:%S - '), no3_selected_coin,"를 ",round(no3_coin_buy, 2),"원 구매했습니다")
                    no3_sell_msg =""
                    no3_emer_sell_price = float(no3_target_price * emergency_sell_rate[2])


                    
            no1_ma5_compare = get_ma5_compare(no1_selected_coin)
            print("no1_ma5_compare :",no1_ma5_compare)
            print("no1_current_price:",no1_current_price)
            if no1_current_price > no1_emer_sell_price and no1_sell_msg == "" and no1_current_price < no1_ma5_compare :
                no1_balance = get_balance(no1_coin)
                if no1_coin=="":
                    no1_current_price = 0
                else :
                    no1_current_price = get_current_price(no1_selected_coin)                
                print("현재코인1번 잔고:",no1_current_price*no1_balance)
                if (no1_current_price*no1_balance) > 5000:
                    upbit.sell_market_order(no1_selected_coin, no1_balance*0.9995)###매매 코드
                    no1_sell_mny = int(no1_current_price *no1_balance*0.9995)
                    no1_earning = int(no1_sell_mny-no1_coin_buy)
                    no1_sell_msg = get_earning_msg(no1_selected_coin, no1_sell_mny, no1_earning)
                    send_message(no1_sell_msg)
                    print(now.strftime('%Y.%m.%d %H:%M:%S - '), no1_selected_coin, "을 ", round(no1_balance*0.9995, 3), "만큼 매도하였습니다")


            no2_ma5_compare = get_ma5_compare(no2_selected_coin)
            if no2_current_price > no2_emer_sell_price and no2_sell_msg == "" and no2_current_price < no2_ma5_compare :
                no2_balance = get_balance(no2_coin)
                if no2_coin=="":
                    no2_current_price = 0
                else :
                    no2_current_price = get_current_price(no2_selected_coin)
                if (no2_current_price*no2_balance) > 5000:
                    upbit.sell_market_order(no2_selected_coin, no2_balance*0.9995)###매매 코드
                    no2_sell_mny = int(no2_current_price * no2_balance * 0.9995)
                    no2_earning = int(no2_sell_mny - no2_coin_buy)
                    no2_sell_msg = get_earning_msg(no2_selected_coin, no2_sell_mny, no2_earning)
                    send_message(no2_sell_msg)
                    print(now.strftime('%Y.%m.%d %H:%M:%S - '), no2_selected_coin, "을 ", round(no2_balance*0.9995, 3), "만큼 매도하였습니다")

            no3_ma5_compare = get_ma5_compare(no3_selected_coin)
            if no3_current_price > no3_emer_sell_price and no3_sell_msg == "" and no3_current_price < no3_ma5_compare :
                no3_balance = get_balance(no3_coin)
                if no3_coin=="":
                    no3_current_price = 0
                else :
                    no3_current_price = get_current_price(no3_selected_coin)
                if (no3_current_price*no3_balance) > 5000:
                    upbit.sell_market_order(no3_selected_coin, no3_balance*0.9995)###매매 코드
                    no3_sell_mny = int(no3_current_price * no3_balance * 0.9995)
                    no3_earning = int(no3_sell_mny - no3_coin_buy)
                    no3_sell_msg = get_earning_msg(no3_selected_coin, no3_sell_mny, no3_earning)
                    send_message(no3_sell_msg)
                    print(now.strftime('%Y.%m.%d %H:%M:%S - '), no3_selected_coin, "을 ", round(no3_balance*0.9995, 3), "만큼 매도하였습니다")
        
        
        else:
            # no1 코인 판매
            no1_balance = get_balance(no1_coin)
            if no1_coin=="":
                no1_current_price = 0
            else :
                no1_current_price = get_current_price(no1_selected_coin)
            if (no1_balance*no1_current_price) > 5000 and no1_sell_msg == "":
                upbit.sell_market_order(no1_selected_coin, no1_balance*0.9995)###매매 코드
                no1_sell_mny = int(no1_current_price *no1_balance*0.9995)
                no1_earning = int(no1_sell_mny-no1_coin_buy)
                no1_sell_msg = get_earning_msg(no1_selected_coin, no1_sell_mny, no1_earning)
                send_message(no1_sell_msg)
                print(now.strftime('%Y.%m.%d %H:%M:%S - '), no1_selected_coin, "을 ", round(no1_balance*0.9995, 3), "만큼 매도하였습니다")
                    
            # no2 코인 판매
            no2_balance = get_balance(no2_coin)
            if no2_coin=="":
                no2_current_price = 0
            else :
                no2_current_price = get_current_price(no2_selected_coin)
            if (no2_balance*no2_current_price) > 5000 and no2_sell_msg == "":
                upbit.sell_market_order(no2_selected_coin, no2_balance*0.9995)###매매 코드
                no2_sell_mny = int(no2_current_price * no2_balance * 0.9995)
                no2_earning = int(no2_sell_mny - no2_coin_buy)
                no2_sell_msg = get_earning_msg(no2_selected_coin, no2_sell_mny, no2_earning)
                send_message(no2_sell_msg)
                print(now.strftime('%Y.%m.%d %H:%M:%S - '), no2_selected_coin, "을 ", round(no2_balance*0.9995, 3), "만큼 매도하였습니다")
                    
            # no3 코인 판매
            no3_balance = get_balance(no3_coin)
            if no3_coin=="":
                no3_current_price = 0
            else :
                no3_current_price = get_current_price(no3_selected_coin)
            if (no3_balance*no3_current_price) > 5000 and no3_sell_msg == "":
                upbit.sell_market_order(no3_selected_coin, no3_balance*0.9995)###매매 코드
                no3_sell_mny = int(no3_current_price * no3_balance * 0.9995)
                no3_earning = int(no3_sell_mny - no3_coin_buy)
                no3_sell_msg = get_earning_msg(no3_selected_coin, no3_sell_mny, no3_earning)
                send_message(no3_sell_msg)
                print(now.strftime('%Y.%m.%d %H:%M:%S - '), no3_selected_coin, "을 ", round(no3_balance*0.9995, 3), "만큼 매도하였습니다")

            no1_coin, no2_coin, no3_coin = "", "", ""
            no1_hpr, no2_hpr, no3_hpr = "", "", ""
            no1_k, no2_k, no3_k = "", "", ""
            no1_buy_msg, no2_buy_msg, no3_buy_msg = "", "", ""
            
            print("60초 쉽니다")
            time.sleep(60)
            
            if no1_sell_mny>0 or no2_sell_mny>0 or no3_sell_mny>0:
                end_msg = "Today's Summary☎"
                total_sell_mny = no1_sell_mny + no2_sell_mny + no3_sell_mny
                total_earning = no1_earning + no2_earning + no3_earning
                total_sell_msg = get_earning_msg(end_msg, total_sell_mny, total_earning)
                send_message(total_sell_msg)
                no1_coin_buy, no2_coin_buy, no3_coin_buy = 0, 0, 0
                no1_sell_mny, no2_sell_mny, no3_sell_mny = 0, 0, 0
                no1_earning, no2_earning, no3_earning = 0, 0, 0
                no1_trade_msg, no2_trade_msg, no3_trade_msg = "","",""
                
            print("60초 쉽니다")    
            time.sleep(60)

        time.sleep(1)
        
    except Exception as e:
        error_msg = "에러발생:" + str(e)
        send_message(error_msg)
        print(error_msg)
        time.sleep(5)
