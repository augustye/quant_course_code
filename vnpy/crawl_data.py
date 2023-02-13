"""
我们使用币安原生的api进行数据爬取.
1. 增加代理配置

author: 51bitquant

discord: 51bitquant#8078

"""

import vnpy_crypto
vnpy_crypto.init()

import pandas as pd
import time
import json
from datetime import datetime
import requests
import pytz
from vnpy.trader.database import get_database, BaseDatabase

from vnpy.trader.object import BarData,Interval
from vnpy.trader.constant import Exchange

pd.set_option('expand_frame_repr', False)  #

BINANCE_SPOT_LIMIT = 1000
BINANCE_FUTURE_LIMIT = 1500

CHINA_TZ = pytz.timezone("Asia/Shanghai")
from threading import Thread

database: BaseDatabase = get_database()

def generate_datetime(timestamp: float) -> datetime:
    """
    :param timestamp:
    :return:
    """
    dt = datetime.fromtimestamp(timestamp / 1000)
    dt = CHINA_TZ.localize(dt)
    return dt


def get_binance_data(symbol: str, exchanges: str, start_time: str, end_time: str):
    """
    爬取币安交易所的数据
    :param symbol: BTCUSDT.
    :param exchanges: 现货、USDT合约, 或者币币合约.
    :param start_time: 格式如下:2020-1-1 或者2020-01-01
    :param end_time: 格式如下:2020-1-1 或者2020-01-01
    :param gate_way the gateway name for binance is:BINANCE_SPOT, BINANCE_USDT, BINANCE_INVERSE
    :return:
    """

    api_url = ''
    save_symbol = symbol

    if exchanges == 'spot':
        print("spot")
        limit = BINANCE_SPOT_LIMIT
        save_symbol = symbol.lower()
        gateway = "BINANCE_SPOT"
        api_url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit={limit}'

    elif exchanges == 'usdt_future':
        print('usdt_future')
        limit = BINANCE_FUTURE_LIMIT
        gateway = "BINANCE_USDT"
        api_url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1m&limit={limit}'

    elif exchanges == 'inverse_future':
        print("inverse_future")
        limit = BINANCE_FUTURE_LIMIT
        gateway = "BINANCE_INVERSE"
        f'https://dapi.binance.com/dapi/v1/klines?symbol={symbol}&interval=1m&limit={limit}'

    else:
        raise Exception('交易所名称请输入以下其中一个：spot, future, coin_future')

    start_time = int(datetime.strptime(start_time, '%Y-%m-%d').timestamp() * 1000)
    end_time = int(datetime.strptime(end_time, '%Y-%m-%d').timestamp() * 1000)

    while True:
        try:
            print(start_time)
            url = f'{api_url}&startTime={start_time}'
            print(url)
            datas = requests.get(url=url, timeout=10, proxies=proxies).json()

            """
            [
                [
                    1591258320000,      // 开盘时间
                    "9640.7",           // 开盘价
                    "9642.4",           // 最高价
                    "9640.6",           // 最低价
                    "9642.0",           // 收盘价(当前K线未结束的即为最新价)
                    "206",              // 成交量
                    1591258379999,      // 收盘时间
                    "2.13660389",       // 成交额(标的数量)
                    48,                 // 成交笔数
                    "119",              // 主动买入成交量
                    "1.23424865",      // 主动买入成交额(标的数量)
                    "0"                 // 请忽略该参数
                ]

            """

            buf = []

            for row in datas:
                bar: BarData = BarData(
                    symbol=save_symbol,
                    exchange=Exchange.BINANCE,
                    datetime=generate_datetime(row[0]),
                    interval=Interval.MINUTE,
                    volume=float(row[5]),
                    turnover=float(row[7]),
                    open_price=float(row[1]),
                    high_price=float(row[2]),
                    low_price=float(row[3]),
                    close_price=float(row[4]),
                    gateway_name=gateway
                )
                buf.append(bar)
                #buf.append(bar)

            database.save_bar_data(buf)

            # 到结束时间就退出, 后者收盘价大于当前的时间.
            if (datas[-1][0] > end_time) or datas[-1][6] >= (int(time.time() * 1000) - 60 * 1000):
                break

            start_time = datas[-1][0]

        except Exception as error:
            print("error:", error)
            time.sleep(10)


def download_spot(symbol):
    """
    下载现货数据的方法.
    :return:
    """
    t1 = Thread(target=get_binance_data, args=(symbol, 'spot', "2018-1-1", "2018-1-31"))
    t2 = Thread(target=get_binance_data, args=(symbol, 'spot', "2018-2-1", "2018-2-28"))
    t3 = Thread(target=get_binance_data, args=(symbol, 'spot', "2018-3-1", "2018-3-31"))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()


def download_future(symbol):
    """
    下载合约数据的方法。
    :return:
    """

    # BTCUSDT的， 要注意看该币的上市时间。
    t1 = Thread(target=get_binance_data, args=(symbol, 'future', "2019-9-10", "2020-2-1"))
    t2 = Thread(target=get_binance_data, args=(symbol, 'future', "2020-2-1", "2020-7-1"))
    t3 = Thread(target=get_binance_data, args=(symbol, 'future', "2020-7-1", "2020-12-1"))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()


if __name__ == '__main__':
    with open('.vntrader/connect_binance_spot.json') as json_file:
        connect_binance = json.load(json_file)

    proxy_host = connect_binance["代理地址"]
    proxy_port = connect_binance["代理端口"]
    
    proxies = None
    if proxy_host and proxy_port:
        proxy = f'http://{proxy_host}:{proxy_port}'
        proxies = {'http': proxy, 'https': proxy}

    download_spot("BTCUSDT") # 下载现货的数据
    # download_future("BTCUSDT")  # 下载合约的数据
