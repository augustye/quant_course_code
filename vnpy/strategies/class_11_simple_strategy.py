from vnpy.trader.constant import Interval
from vnpy.trader.object import TickData, BarData, TradeData, OrderData
from vnpy.trader.utility import BarGenerator, ArrayManager
from vnpy_ctastrategy.engine import  CtaTemplate, StopOrder, CtaEngine, EngineType

class Class11SimpleStrategy(CtaTemplate):
    author = "51bitquant"

    def __init__(self, cta_engine: CtaEngine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar)
        self.bg2 = BarGenerator(self.on_bar, 2, self.on_2min_bar, Interval.MINUTE)
        self.bg5 = BarGenerator(self.on_bar, 5, self.on_5min_bar, Interval.MINUTE)
        self.bg_1hour = BarGenerator(self.on_bar, 1, self.on_1hour_bar, Interval.HOUR)

        self.place_order = False
        self.orders = []
        # self.pos #

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")
        self.put_event()

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")
        self.put_event()

    def on_tick(self, tick: TickData):
        print(f"tick, ask1:{tick.ask_price_1}, {tick.ask_volume_1}, bid:{tick.bid_price_1}, {tick.bid_volume_1}, pos: {self.pos}")
        if self.place_order is False and self.trading:
            self.place_order = True
            buy_order = self.buy(tick.bid_price_1 * 0.9999, 0.01)
            sell_order = self.sell(tick.ask_price_1 * 1.0001, 0.01)
            # self.short()
            # self.cover() 
            print(f"placed buy_order: {buy_order}, sell_order: {sell_order}")
            self.orders.extend(buy_order)
            self.orders.extend(sell_order)

        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        print("1分钟的K线数据", bar)
        self.bg2.update_bar(bar)
        self.bg5.update_bar(bar)  # 合成2分钟的K线
        self.bg_1hour.update_bar(bar)  # 合成一小时的数据。
        self.put_event()

    def on_2min_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        print("2分钟的K线数据", bar)
        self.put_event()

    def on_5min_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        print("5分钟的K线数据", bar)
        self.put_event()

    def on_1hour_bar(self, bar:BarData):
        print("1小时的K线数据", bar)
        self.put_event()

    def on_order(self, order: OrderData):
        print("订单状态更新:", order)
        self.put_event()

    def on_trade(self, trade: TradeData):
        """
        订单成交的推送，比如你下10个BTC,那么可能不会一下子成交，会不断慢慢的成交，
        这时有成交它就会推送给你，告诉你成交了多少，还有多少没有成交
        系统通过里面处理这个方法，知道你当前的仓位数量
        """
        print("最新的成交: ", trade)
        self.put_event()  # 更新UI界面方法。

    def on_stop_order(self, stop_order: StopOrder):
        """
        这个是一个停止单的方法，用来监听你止损单的方法。
        """
        pass

