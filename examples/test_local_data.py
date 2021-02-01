import jsonpath
from pandas.io.json import json_normalize
import pandas as pd

from czsc import KlineAnalyze, find_zs
# from czsc.data.local import get_local_kline
from czsc.analyze import find_zs_enhanced_v1
from czsc.data.local import get_local_kline, get_local_day_kline


def test_use_local_data():
    kline = get_local_kline(symbol=['300494'], end='2020-04-31', freq='5min', start='2019-01-01')
    # kline = get_local_day_kline('300494', end='2020-12-31', start='2019-01-01')

    ka = KlineAnalyze(kline, name="1min", verbose=False)
    print("分型识别结果：", ka.fx_list[-3:])
    print("笔识别结果：", ka.bi_list[-3:])
    print("线段识别结果：", ka.xd_list[-3:])
    zx = find_zs_enhanced_v1(ka.bi_list, ka.macd)
    print("中枢识别结果：", zx)

    third_buy = jsonpath.jsonpath(zx, '$..third_buy')
    third_buy = json_normalize(third_buy)

    third_buy.set_index(['dt'])
    kline.set_index(['dt'])
    result = pd.merge(kline, third_buy, how="outer").fillna(0).set_index(['symbol', 'dt'])

    print(result)


    # 用图片或者HTML可视化
    ka.to_image("test.png")


if __name__ == '__main__':
    test_use_local_data()