from typing import Optional

from vnpy.trader.constant import Interval
from vnpy.trader.object import TickData, BarData, TradeData, OrderData, Status
from vnpy.trader.utility import BarGenerator, ArrayManager
from vnpy_ctastrategy.engine import  CtaTemplate, StopOrder, CtaEngine, EngineType
from vnpy.trader.event import EVENT_TIMER, EVENT_ACCOUNT
from vnpy.event import Event

TIMER_WAITING_INTERVAL = 10

class Class16SpotGridStrategy(CtaTemplate):
    author = "51bitquant"

    grid_step    = 0.1  # 价格间隙，建议为交易费用的3～5倍。例如买入0.01个价格1500的以太坊再卖出，手续费为 0.01 * 1500 * 0.1% * 2 = 0.03
    trading_size = 0.01 # 每次下单的头寸，最小数量为10刀/价格
    max_size     = 1000 # 最大网格数 self.pos <= max_size * trading_size

    parameters = ["grid_step", "trading_size", "max_size"]

    def __init__(self, cta_engine: CtaEngine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.buy_orders = []  # 所有的buy orders.
        self.sell_orders = []  # 所有的sell orders.

        self.timer_interval = 0

        self.last_filled_order: Optional[OrderData] = None  # 联合类型, 或者叫可选类型，二选一那种.
        self.tick: Optional[TickData] = None  #

        print("交易的交易对:", vt_symbol)

        # 订阅的资产信息. BINANCE_SPOT.资产名
        self.cta_engine.event_engine.register(EVENT_ACCOUNT + "BINANCE_SPOT.USDT", self.process_account_event)
        self.cta_engine.event_engine.register(EVENT_ACCOUNT + "BINANCE_SPOT.BTC", self.process_account_event)
        self.cta_engine.event_engine.register(EVENT_ACCOUNT + "BINANCE_SPOT.ETH", self.process_account_event)

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

        # 定时器.
        self.cta_engine.event_engine.register(EVENT_TIMER, self.process_timer_event)

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")
        self.cta_engine.event_engine.unregister(EVENT_TIMER, self.process_timer_event)

    def process_timer_event(self, event: Event):

        if self.tick is None:
            return

        self.timer_interval += 1
        if self.timer_interval >= TIMER_WAITING_INTERVAL:

            # 如果你想比较高频可以把定时器给关了
            self.timer_interval = 0

            # 建立初始网格
            if len(self.buy_orders) == 0 and len(self.sell_orders) == 0:

                # 限制下单的数量
                if abs(self.pos) > self.max_size * self.trading_size:
                    return

                buy_price = self.tick.bid_price_1 - self.grid_step / 2
                sell_price = self.tick.ask_price_1 + self.grid_step / 2

                buy_orders_ids = self.buy(buy_price, self.trading_size)  # 列表.
                sell_orders_ids = self.sell(sell_price, self.trading_size)

                self.buy_orders.extend(buy_orders_ids)
                self.sell_orders.extend(sell_orders_ids)

                print(f"[开启网格交易] BUY: {buy_orders_ids}@{buy_price}, SELL: {sell_orders_ids}@{sell_price}")

            elif len(self.buy_orders) == 0 or len(self.sell_orders) == 0:
                # 网格两边的数量不对等.
                self.cancel_all()

    def process_account_event(self, event:Event):
        print("收到的账户资金的信息:", event.data)

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.tick = tick

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        pass

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """

        if order.status == Status.ALLTRADED:

            if order.vt_orderid in self.buy_orders:
                self.buy_orders.remove(order.vt_orderid)

            if order.vt_orderid in self.sell_orders:
                self.sell_orders.remove(order.vt_orderid)

            self.cancel_all()
            print("订单成交, 撤销其他订单")

            self.last_filled_order = order

            # 在订单价位上下设置网格
            if self.tick and abs(self.pos) < self.max_size * self.trading_size:
                step = self.get_step()

                buy_price = order.price - step * self.grid_step
                sell_price = order.price + step * self.grid_step

                # 避免超过市价
                buy_price = min(self.tick.bid_price_1 * (1 - 0.0001), buy_price)  
                sell_price = max(self.tick.ask_price_1 * (1 + 0.0001), sell_price)

                buy_ids = self.buy(buy_price, self.trading_size)
                sell_ids = self.sell(sell_price, self.trading_size)

                self.buy_orders.extend(buy_ids)
                self.sell_orders.extend(sell_ids)

                print(f"[订单成交后更新网格] BUY: {buy_ids}@{buy_price}, SELL: {sell_ids}@{sell_price}")

        if not order.is_active():
            if order.vt_orderid in self.buy_orders:
                self.buy_orders.remove(order.vt_orderid)

            elif order.vt_orderid in self.sell_orders:
                self.sell_orders.remove(order.vt_orderid)

        self.put_event()

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass

    def get_step(self) -> int:
        """
        这个步长的乘积，随你你设置， 你可以都设置为1
        :return:
        """

        return 1
        # pos = abs(self.pos)  #
        #
        # if pos < 3 * self.trading_size:
        #     return 1
        #
        # elif pos < 5 * self.trading_size:
        #     return 2
        #
        # elif pos < 7 * self.trading_size:
        #     return 3
        #
        # return 4

        # or you can set it to only one.
        # return 1

