import time
import pyupbit
import datetime

access = "your-access"
secret = "your-secret"

# ticker는 어떤 코인인 지를 의미함


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    # 2일치에 해당하는 일 데이터를 조회함
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    # 변동성 돌파전략 통해 target_price 설정
    # df.iloc[0]['close']는 다음날 시가와 동일
    target_price = df.iloc[0]['close'] + \
        (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price


def get_start_time(ticker):
    """시작 시간 조회"""
    # get_ohlcv를 이용하면 일봉 조회가 가능한데 그 시간이 자체적으로 9시로 설정되어 있음
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    # df 인덱스의 가장 첫번째 값이 start_time임
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


def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")   # 9시
        end_time = start_time + datetime.timedelta(days=1)   # 9시 + 1일

        # 9시 < 현재 시각 < 8시 59분 50초 이면 target_price, current_price를 가져오도록 함
        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
