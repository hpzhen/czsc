from functools import reduce

import jsonpath
from pandas.io.json import json_normalize
import pandas as pd

from czsc import KlineAnalyze, find_zs
# from czsc.data.local import get_local_kline
from czsc.analyze import find_zs_enhanced_v1
from czsc.data.local import get_local_kline, get_local_day_kline


def test_use_local_data():
    # kline = get_local_kline(symbol=['300494'], end='2020-04-31', freq='5min', start='2019-01-01')
    kline = get_local_day_kline('000001', end='2020-12-31', start='2019-01-01')

    ka = KlineAnalyze(kline, name="1min", verbose=False)
    print("分型识别结果：", ka.fx_list[-3:])
    print("笔识别结果：", ka.bi_list[-3:])
    print("线段识别结果：", ka.xd_list[-3:])
    zx = find_zs_enhanced_v1(ka.bi_list, ka.macd)
    print("中枢识别结果：", zx)

    bei_chi = jsonpath.jsonpath(zx, '$..bei_chi')
    bei_chi = json_normalize(bei_chi)
    bei_chi.set_index('dt', inplace=True)

    third_buy = jsonpath.jsonpath(zx, '$..third_buy')
    third_buy = json_normalize(third_buy)
    third_buy['type'] = "3"

    second_buy = jsonpath.jsonpath(zx, '$..second_buy')
    second_buy = json_normalize(second_buy)
    second_buy['type'] ="2"

    first_buy = jsonpath.jsonpath(zx, '$..first_buy')
    first_buy = json_normalize(first_buy)
    first_buy['type'] = 1


    dfs = [first_buy, second_buy, third_buy]
    points = reduce(lambda left, right: pd.concat([left, right], axis=0, join='outer'), dfs)
    points = pd.DataFrame(points).set_index('dt').sort_index()
    points = pd.concat([points, bei_chi], axis=1, join='outer')

    kline = pd.DataFrame(kline).set_index(['dt'])
    result = pd.concat([kline, points], axis=1, join='outer').reset_index()

    result = result.fillna(0).set_index(['symbol', 'dt'])



    print(result)


    # 用图片或者HTML可视化
    ka.to_image("test.png")


if __name__ == '__main__':
    test_use_local_data()