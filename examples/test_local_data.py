from czsc import KlineAnalyze
from czsc.data.local import get_local_kline


def test_use_local_data():
    kline = get_local_kline(symbol=['000001'], end='2020-11-30', freq='30min', start='2020-01-01')

    ka = KlineAnalyze(kline, name="30分钟", verbose=False)
    print("分型识别结果：", ka.fx_list[-3:])
    print("笔识别结果：", ka.bi_list[-3:])
    print("线段识别结果：", ka.xd_list[-3:])

    # 用图片或者HTML可视化
    ka.to_image("test.png")


if __name__ == '__main__':
    test_use_local_data()