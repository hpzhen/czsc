import os

from czsc import NewBar, Direction
from czsc.analyze import remove_include, check_fx, CZSC
from czsc.data.local_mongo import local_mongo
from czsc.objects import FX
from czsc.utils import kline_pro
from test.test_analyze import get_user_signals


def read_daily():
    client = local_mongo()
    bars = client.get_kline_period(symbol=['000001'], start_date="2022-01-01", end_date="2022-05-30", freq='D')
    return bars


def test_find_bi():
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


def test_czsc_update():
    bars = read_daily()
    # 不计算任何信号
    c = CZSC(bars)
    assert not c.signals

    # 测试 ubi 属性
    ubi = c.ubi
    assert ubi['direction'] == Direction.Down
    assert ubi['high_bar'].dt < ubi['low_bar'].dt
    # 测试自定义信号
    c = CZSC(bars, get_signals=get_user_signals)
    assert len(c.signals) == 7

    kline = [x.__dict__ for x in c.bars_raw]
    bi = [{'dt': x.fx_a.dt, "bi": x.fx_a.fx} for x in c.bi_list] + \
         [{'dt': c.bi_list[-1].fx_b.dt, "bi": c.bi_list[-1].fx_b.fx}]
    chart = kline_pro(kline, bi=bi, title="{} - {}".format(c.symbol, c.freq))
    file_html = "x.html"
    chart.render(file_html)
    os.remove(file_html)
