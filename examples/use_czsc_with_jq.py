# coding: utf-8
import sys

import jsonpath

sys.path.insert(0, "..")
sys.path.insert(0, ".")

from datetime import datetime
from czsc import KlineAnalyze, find_zs
from czsc.data.jq import get_kline, set_token


def format_bi_points(bi_points):
    for i, x in enumerate(bi_points):
        x['dt'] = i
        x.pop("start_dt")
        x.pop("end_dt")
        x.pop("fx_high")
        x.pop("fx_low")
    return bi_points

def use_kline_analyze():
    # kline = get_kline(symbol="000001.XSHG", end_date=datetime.strptime("20200830", "%Y%m%d"), freq="D", count=5000)
    # ka = KlineAnalyze(kline, name="日线", verbose=False)
    # print("分型识别结果：", ka.fx_list[-3:])
    # print("笔识别结果：", ka.bi_list[-3:])
    # print("线段识别结果：", ka.xd_list[-3:])
    #
    # kline = get_kline(symbol="300803.XSHE", end_date=datetime.strptime("20200830", "%Y%m%d"), freq="30min", count=5000)
    # ka = KlineAnalyze(kline, name="30分钟", verbose=False)
    # print("分型识别结果：", ka.fx_list[-3:])
    # print("笔识别结果：", ka.bi_list[-3:])
    # print("线段识别结果：", ka.xd_list[-3:])

    kline = get_kline(symbol="000001.XSHE", end_date=datetime.strptime("20200830", "%Y%m%d"), freq="5min", count=5000)
    ka = KlineAnalyze(kline, name="5分钟", verbose=False)
    print("分型识别结果：", ka.fx_list[-3:])
    print("笔识别结果：", ka.bi_list[-3:])
    print("线段识别结果：", ka.xd_list[-3:])

    zx = find_zs(ka)

    print(jsonpath.jsonpath(zx, '$..third_buy'))

    # 用图片或者HTML可视化
    # ka.to_image("test.png")


if __name__ == '__main__':
    use_kline_analyze()

