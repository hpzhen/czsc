from functools import reduce

import jsonpath
from pandas.io.json import json_normalize
import pandas as pd

from czsc import KlineAnalyze, find_zs
# from czsc.data.local import get_local_kline
from czsc.analyze import find_zs_enhanced_v1, get_fd_from_points
from czsc.analyze_enhance import common_check_beichi, judge_zoushi, construct_zoushi
from czsc.data.local import get_local_kline, get_local_day_kline, QA_fetch_stock_week
from czsc.trendanalyser import TrendAnalyser


def test_use_local_data():
    kline_1min = get_local_kline(symbol=['300494'], end='2020-12-31', freq='1min', start='2020-01-01')
    kline_5min = get_local_kline(symbol=['300494'], end='2020-12-31', freq='5min', start='2020-01-01')
    # kline = get_local_day_kline(symbol=['000001'], end='2019-04-31', start='2018-01-01')
    # kline = QA_fetch_stock_week('000002', end='2019-12-13', start='2019-03-29')

    ka_1min = KlineAnalyze(kline_1min, name="1min", verbose=False)
    ka_5min = KlineAnalyze(kline_5min, name="5min", verbose=False)
    print("分型识别结果：", ka_1min.fx_list[-3:])
    print("笔识别结果：", ka_1min.bi_list[-3:])
    print("线段识别结果：", ka_1min.xd_list[-3:])
    fds = get_fd_from_points(ka_1min.bi_list, ka_1min.macd, symbol=ka_1min.symbol)
    # zoushi = construct_zoushi(fds, ka.macd)
    ta_1min= TrendAnalyser(fds, ka_1min.macd)
    ta_5min= TrendAnalyser(ta_1min.get_zoushi_list(), ka_5min.macd)
    result = ta_5min.getAnalysisResult()

    bc = common_check_beichi(ka_1min.xd_list[-5:])
    zx = find_zs_enhanced_v1(ka_1min.bi_list, ka_1min.macd)
    print("中枢识别结果：", zx)

    bei_chi = jsonpath.jsonpath(zx, '$..bei_chi')
    if isinstance(bei_chi, bool):
        bei_chi=pd.DataFrame()
    else:
        bei_chi = json_normalize(bei_chi)
        bei_chi.set_index('dt', inplace=True)

    third_buy = jsonpath.jsonpath(zx, '$..third_buy')
    if isinstance(third_buy, bool):
        third_buy=pd.DataFrame()
    else:
        third_buy = json_normalize(third_buy)
        third_buy['type'] = "3"

    second_buy = jsonpath.jsonpath(zx, '$..second_buy')
    if isinstance(second_buy, bool):
        second_buy= pd.DataFrame()
    else:
        second_buy = json_normalize(second_buy)
        second_buy['type'] ="2"

    first_buy = jsonpath.jsonpath(zx, '$..first_buy')
    if isinstance(first_buy, bool):
        first_buy = pd.DataFrame()
    else:
        first_buy = json_normalize(first_buy)
        first_buy['type'] = 1

    # third_bs = jsonpath.jsonpath(zx, '$..third_bs_section')
    # third_bs = json_normalize(third_bs)
    # third_bs.set_index('dt', inplace=True)


    dfs = [first_buy, second_buy, third_buy]
    points = reduce(lambda left, right: pd.concat([left, right], axis=0, join='outer'), dfs)
    if len(points) == 0:
        pass
    else:
        points = pd.DataFrame(points).set_index('dt').sort_index()
        points = pd.concat([points, bei_chi], axis=1, join='outer')
        # points = pd.concat([points, third_bs], axis=1, join='outer')

        kline_1min = pd.DataFrame(kline_1min).set_index(['dt'])
        result = pd.concat([kline_1min, points], axis=1, join='outer').reset_index()

        result = result.fillna(0).set_index(['symbol', 'dt'])

        print(result)


    # 用图片或者HTML可视化
    ka_1min.to_image("test.png")


if __name__ == '__main__':
    test_use_local_data()