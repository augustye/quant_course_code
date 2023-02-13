import vnpy_crypto
vnpy_crypto.init()

from vnpy_ctastrategy.backtesting import BacktestingEngine
from vnpy.trader.object import Interval
from datetime import datetime

from strategies.class_12_fixed_trade_time_strategy import Class12FixedTradeTimeStrategy

# Note: Need to crawl data first

engine = BacktestingEngine()
engine.set_parameters(
    vt_symbol="btcusdt.BINANCE",
    interval=Interval.MINUTE,
    start=datetime(2018,1,1),
    end  =datetime(2018,1,31),
    rate=1/1000,     # 币安手续费千分之1
    slippage=0,
    size=1,          # 若币本位合约为100
    pricetick=0.01,  # 价格精度
    capital=300000)

engine.add_strategy(Class12FixedTradeTimeStrategy, {})
engine.load_data()
engine.run_backtesting()

engine.calculate_result()
engine.calculate_statistics()
engine.show_chart()