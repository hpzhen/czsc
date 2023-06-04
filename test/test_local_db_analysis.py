from collections import OrderedDict

from czsc import NewBar
from czsc.analyze import remove_include, check_fx, CZSC
from czsc.data.local_mongo import local_mongo
from czsc.objects import FX
from czsc.signals import cxt_bi_base_V230228, cxt_fx_power_V221107, cxt_third_buy_V230228, cxt_first_buy_V221126
from czsc.signals.bxt import get_s_three_bi, get_s_d0_bi
from czsc.utils import kline_pro


def read_daily():
    client = local_mongo()
    bars = client.get_kline_period(symbol=['000001'], start_date="2022-01-01", end_date="2022-03-17", freq='D')
    return bars


def read_15min():
    client = local_mongo()
    bars = client.get_kline_period(symbol=['000001'], start_date="2022-01-01 00:00:00", end_date="2022-03-09 14:20:00", freq='15min')
    return bars


def get_user_signals(c: CZSC) -> OrderedDict:
    """在 CZSC 对象上计算信号，这个是标准函数，主要用于研究。
    实盘时可以按照自己的需要自定义计算哪些信号

    :param c: CZSC 对象
    :return: 信号字典
    """
    s = OrderedDict({"symbol": c.symbol, "dt": c.bars_raw[-1].dt, "close": c.bars_raw[-1].close})
    # 倒0，特指未确认完成笔
    # 倒1，倒数第1笔的缩写，表示第N笔
    # 倒2，倒数第2笔的缩写，表示第N-1笔
    # 倒3，倒数第3笔的缩写，表示第N-2笔
    # 以此类推
    for i in range(1, 3):
        s.update(get_s_three_bi(c, i))
    s.update(get_s_d0_bi(c))
    return s


def get_min_bi_signals(c: CZSC):
    s = OrderedDict({"symbol": c.symbol, "dt": c.bars_raw[-1].dt, "close": c.bars_raw[-1].close})

    for i in range(1, 3):
        s.update(cxt_fx_power_V221107(c, di=i))

    s.update(cxt_bi_base_V230228(c))
    return s


def test_find_bi_day():
    bars = read_daily()
    # 去除包含关系
    bars1 = []
    for bar in bars:
        if len(bars1) < 2:
            bars1.append(NewBar(symbol=bar.symbol, id=bar.id, freq=bar.freq,
                                dt=bar.dt, open=bar.open,
                                close=bar.close, high=bar.high, low=bar.low,
                                vol=bar.vol, elements=[bar]))
        else:
            k1, k2 = bars1[-2:]
            has_include, k3 = remove_include(k1, k2, bar)
            if has_include:
                bars1[-1] = k3
            else:
                bars1.append(k3)

    fxs = []
    for i in range(1, len(bars1) - 1):
        fx = check_fx(bars1[i - 1], bars1[i], bars1[i + 1])
        if isinstance(fx, FX):
            fxs.append(fx)
    return fxs


def test_czsc_update_15min():
    bars = read_15min()
    c = CZSC(bars)

    assert len(c.signals) == 7

    kline = [x.__dict__ for x in c.bars_raw]
    bi = [{'dt': x.fx_a.dt, "bi": x.fx_a.fx} for x in c.bi_list] + \
         [{'dt': c.bi_list[-1].fx_b.dt, "bi": c.bi_list[-1].fx_b.fx}]
    chart = kline_pro(kline, bi=bi, title="{} - {}".format(c.symbol, c.freq))
    file_html = "x_{}.html".format("15min")
    chart.render(file_html)

def test_get_sigal_15min():
    def get_test_signals(c: CZSC) -> OrderedDict:
        s = OrderedDict({"symbol": c.symbol, "dt": c.bars_raw[-1].dt, "close": c.bars_raw[-1].close})
        s.update(cxt_third_buy_V230228(c))
        return s
    bars = read_15min()
    c = CZSC(bars, get_signals=get_test_signals)

    kline = [x.__dict__ for x in c.bars_raw]
    bi = [{'dt': x.fx_a.dt, "bi": x.fx_a.fx} for x in c.bi_list] + \
         [{'dt': c.bi_list[-1].fx_b.dt, "bi": c.bi_list[-1].fx_b.fx}]
    chart = kline_pro(kline, bi=bi, title="{} - {}".format(c.symbol, c.freq))
    file_html = "x_{}_{}.html".format(c.symbol, c.freq)
    chart.render(file_html)


def test_czsc_update():
    bars = read_daily()
    # 不计算任何信号
    c = CZSC(bars)
    assert not c.signals

    # 测试 ubi 属性
    ubi = c.ubi
    # assert ubi['direction'] == Direction.Down
    # assert ubi['high_bar'].dt < ubi['low_bar'].dt
    # 测试自定义信号
    c = CZSC(bars, get_signals=get_user_signals)
    assert len(c.signals) == 7

    kline = [x.__dict__ for x in c.bars_raw]
    bi = [{'dt': x.fx_a.dt, "bi": x.fx_a.fx} for x in c.bi_list] + \
         [{'dt': c.bi_list[-1].fx_b.dt, "bi": c.bi_list[-1].fx_b.fx}]
    chart = kline_pro(kline, bi=bi, title="{} - {}".format(c.symbol, c.freq))
    file_html = "x.html"
    # chart.render(file_html)
    # os.remove(file_html)
