# encoding: utf-8

from gmsdk import *
import symbol

def symbol(pos):
    return "{}.{}".format(pos.exchange, pos.sec_id)


class RiskController(Strategy):
    symbols = set()
    positions = dict()
    cm = ContractManager.instance()
    lose_threshold = -3.0 # percentage

    def on_position_open(self, pos):
        sym = symbol(pos)
        print(
            '{} position opened, side = {}, volume/today = {}/{}, price = {}'.
            format(sym, pos.side, pos.volume, pos.volume_today, pos.price))
        pos_key = "{}__{}".format(sym, pos.side)
        if not pos_key in self.positions:
            if pos.volume > 0:
                self.subscribe({sym})
                self.positions[pos_key] = pos
                print("pos opened, subscribe {}".format(sym))
        else:
            p = self.positions[pos_key]
            p.price = (p.price * p.volume + pos.price * pos.volume) / (p.volume + pos.volume)
            p.volume += pos.volume
            p.volume_today += pos.volume_today

    def on_position_close(self, pos):
        sym = symbol(pos)
        print(
            '{} position closed, side = {}, volume/today = {}/{}, price = {}'.
            format(sym, pos.side, pos.volume, pos.volume_today, pos.price))

        pos_key = "{}__{}".format(sym, pos.side)

        if pos_key in self.positions:
            p = self.positions[pos_key]
            p.volume -= pos.volume
            p.volume_today -= pos.volume_today

            # remove empty position
            if p.volume <= 0:
                self.positions.pop(pos_key)
                self.unsubscribe({sym})
                print("pos closed, unsubscribe {}".format(sym))

    def on_tick(self, tick):
        print('tick {}, ask: {} -- {} bid: {} -- {}'.format(
            tick.symbol(), tick.ask_p1, tick.ask_v1, tick.bid_p1, tick.bid_v1))
        self.care_positions(tick)

    def care_positions(self, tick):
        sym = tick.symbol()
        for side in (PositionSide.Long, PositionSide.Short):
            pos_key = "{}__{}".format(sym, side)
            if pos_key in self.positions:
                pos = self.positions[pos_key]
                c = get_contract(sym)
                ins = self.cm.by_contract(c)
                if not ins:
                    print("cannot find contract info for {}".format(c))
                    return

                multiplier = ins.multiplier
                price_tk = ins.price_tick
                margin_ratio = ins.spec_ratio.long_margin_ratio if pos.side == PositionSide.Long else ins.spec_ratio.short_margin_ratio
                if not margin_ratio > 0:
                    print("error margin ratio configuration for ", sym)
                    return
                if not pos.price > 0:
                    print("empty position of sym: ", sym)
                    return

                #pos_pnl = 100.0*pnl(c, pos.side, pos.volume, pos.price, tick.last_price)/margin(c, pos.side, pos.volume, pos.price)

                if pos.side == PositionSide.Long:
                    print("100.0*(tick.bid_p1 - pos.price)/pos.price / margin_ratio = ", 100.0 * (tick.bid_p1 - pos.price) / pos.price / margin_ratio)
                    if 100.0*(tick.bid_p1 - pos.price)/pos.price / margin_ratio < self.lose_threshold:
                        self.sell_close(sym, OrderPriceType.LimitPrice, tick.bid_p1 - price_tk, pos.available)
                if pos.side == PositionSide.Short:
                    print("100.0 * (pos.price - tick.ask_p1) / pos.price / margin_ratio = ", 100.0 * (pos.price - tick.ask_p1) / pos.price / margin_ratio)
                    if 100.0 * (pos.price - tick.ask_p1) / pos.price / margin_ratio < self.lose_threshold:
                        self.buy_close(sym, OrderPriceType.LimitPrice, tick.ask_p1 + price_tk, pos.available)

    def on_order_new(self, order):
        pos_key = "{}.{}__{}".format(order.exchange, order.sec_id, order.side)
        pos = self.positions.get(pos_key)
        if not pos:
            return

        if order.effect == PositionEffect.Close_Today:
            pos.available_today -= order.volume

        if order.effect != PositionEffect.Open:
            pos.available -= order.volume

if __name__ == '__main__':
    s = RiskController()
    s.lose_threshold = -3.0
    s.run()
