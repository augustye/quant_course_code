import sys
import json
from time import sleep
from datetime import datetime, time
from logging import INFO

import vnpy_crypto
vnpy_crypto.init()

from vnpy.event import EventEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.engine import MainEngine
from vnpy_ctastrategy import CtaStrategyApp
from vnpy_ctastrategy.engine import CtaEngine
from vnpy_ctastrategy.base import EVENT_CTA_LOG

from vnpy_ib import IbGateway
from vnpy_binance import BinanceSpotGateway,BinanceUsdtGateway,BinanceInverseGateway

SETTINGS["log.level"] = INFO
SETTINGS["log.file"] = True
SETTINGS["log.active"] = True  
SETTINGS["log.console"] = True 

event_engine = EventEngine()  
main_engine = MainEngine(event_engine) 
main_engine.add_gateway(BinanceSpotGateway)
#main_engine.add_gateway(BinanceUsdtGateway)

cta_engine: CtaEngine = main_engine.add_app(CtaStrategyApp) # 添加cta引擎, 实际上就是初始化引擎
main_engine.write_log("主引擎创建成功")

log_engine = main_engine.get_engine("log")
event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
main_engine.write_log("注册日志事件监听")

# 连接到交易所
with open('.vntrader/connect_binance_spot.json') as json_file:
    connect_binance = json.load(json_file)
    main_engine.connect(connect_binance, "")
    main_engine.write_log("connect binance gateway")

sleep(10) #等待连接
cta_engine.init_engine()
main_engine.write_log("CTA引擎初始化完成")

# 具体加载的策略来自于配置文件.vntrader/cta_strategy_settings.json
# 仓位信息来自于.vntrader/cta_strategy_data.json
# 在配置文件有这个策略就不需要手动添加
cta_engine.add_strategy('Class11SimpleStrategy', 'bnbusdt_spot', 'bnbusdt.BINANCE', {})
cta_engine.init_all_strategies()
main_engine.write_log("CTA策略初始化完成")

sleep(10) #等待初始化
cta_engine.start_all_strategies()
main_engine.write_log("CTA策略启动完成")

while True:
    sleep(10)