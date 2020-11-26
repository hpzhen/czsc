import sys
sys.path.insert(0, ".")
sys.path.insert(0, "..")

import czsc
print(czsc.__version__)

from datetime import datetime
from typing import List
import traceback
import pandas as pd
import numpy as np
from tqdm import tqdm_notebook as tqdm
from czsc.analyze import KlineAnalyze
# 导入 Tushare 数据（推荐使用）
from czsc.data.ts import *

# 如果是第一次使用需要设置 token
# set_token("trushare.pro token")

# 导入聚宽数据
from czsc.data.jq import *

# 如果是第一次使用需要设置 token
# set_token("手机号", "密码")




# 条件描述： 最近五笔走势，前三笔构成中枢，第四笔离开中枢，第五笔向下不回中枢

def selector(symbols: List):
    """输入股票列表，输入符合买点定义的股票"""
    res = []
    for symbol in tqdm(symbols, desc="缠论日线笔中枢三买选股"):
        try:
            kline = get_kline(symbol=symbol, end_date=datetime.now(), freq="D", count=1000)
            ka = KlineAnalyze(kline, ma_params=(5, 34, 120, 233), bi_mode="new")
            points = ka.bi_list[-6:]

            if len(points) == 6 and points[-1]['fx_mark'] == "d":
                zs_g = min([x['bi'] for x in points[:4] if x['fx_mark'] == 'g'])
                zs_d = max([x['bi'] for x in points[:4] if x['fx_mark'] == 'd'])

                if points[-1]['bi'] > zs_g > zs_d:
                    res.append(symbol)

        except:
            print("{} 分析失败".format(symbol))
            traceback.print_exc()
    return res

# 中枢如果能当下确认，基本逻辑如下：
#
# ma 233<close<ma 60 ---得 codes_list1
# codes_list1中选择 符合日线笔中枢形态的，得codes_list2
# 2.1 笔中枢形态：方向下: 日线中枢完成，第四笔底分型
# codes_list2 中中枢第一笔到第四笔得日期跨度 date1
# date1时间跨度中，codes_list2 ma233 cross的个数，并标注 codes_list3
def cross_number(x1, x2):
    """输入两个序列，计算 x1 下穿 x2 的次数"""
    x = np.array(x1) < np.array(x2)
    num = 0
    for i in range(len(x)-1):
        b1, b2 = x[i], x[i+1]
        if b2 and b1 != b2:
            num += 1
    return num


def selector(symbols: List):
    """输入股票列表，输入符合买点定义的股票"""
    res = []
    for symbol in tqdm(symbols, desc="缠论选股"):
        try:
            kline = get_kline(symbol=symbol, end_date=datetime.now(), freq="D", count=1000)
            ka = KlineAnalyze(kline, ma_params=(5, 34, 60, 250), bi_mode="new")

            if ka.ma[-1]['ma60'] >= ka.latest_price >= ka.ma[-1]['ma250']:
                # print("{} 满足条件1：ma60 > close > ma233".format(symbol))
                points = ka.bi_list[-7:]

                if len(points) == 7 and points[-1]['fx_mark'] == 'd':
                    zs_g = min([x['bi'] for x in points[2:6] if x['fx_mark'] == 'g'])
                    zs_d = max([x['bi'] for x in points[2:6] if x['fx_mark'] == 'd'])

                    if zs_g > zs_d:
                        # print("{} 满足条件2：向下中枢完成".format(symbol))
                        date_span = [points[-5]['dt'], points[-1]['dt']]
                        low = [x['low'] for x in ka.kline_raw if date_span[1] >= x['dt'] >= date_span[0]]
                        ma_ = [x['ma250'] for x in ka.ma if date_span[1] >= x['dt'] >= date_span[0]]
                        num = cross_number(low, ma_)
                        res.append({"symbol": symbol, "cross_num": num})
        except:
            print("{} 分析失败".format(symbol))
            traceback.print_exc()
    return res



def jq_xuangu():
    # 使用聚宽数据在创业板综指上选股
    symbols = get_index_stocks("399006.XSHE")
    selected = selector(symbols)

    print("选股结果：", selected)
    # df = pd.DataFrame(selected)
    # df.to_excel("选股结果.xlsx", index=False)


if __name__ == '__main__':
    jq_xuangu()