# coding: utf-8
import warnings

from czsc.analyze import check_bei_chi, get_potential_xd, calculate_macd_power

try:
    import talib as ta
except ImportError:
    from czsc import ta

    ta_lib_hint = "没有安装 ta-lib !!! 请到 https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib " \
                  "下载对应版本安装，预计分析速度提升2倍"
    warnings.warn(ta_lib_hint)

beyond_zs_ratio = 1.0
zoushi_list = []
tmp_fds = []


def check_trend_beichi(fds):
    assert fds[0]['direction'] == fds[-1]['direction']
    direction = fds[0]['direction']

    bc = {"bc": "没有背驰", "notes": ""}
    if direction == 'up' and fds[-1]['power'] < fds[0]['power']:
        bc={"bc": "向上趋势背驰", "notes": "123向上，3最高，力度上1大于3"}
    elif direction == 'down' and fds[2]['power'] < fds[0]['power']:
        bc = {"bc": "向下趋势背驰", "notes": "123向下，1最高，力度上1大于3"}
    return bc


def common_check_beichi(fds):
    assert isinstance(fds, list)
    size = len(fds)

    if size == 3:
        return check_trend_beichi(fds)
    elif size == 5:
        return check_bei_chi(fds[0], fds[1], fds[2], fds[3], fds[4])


def judge_more_than_3fds_zoushi(fds, macd_list):
    zoushi = {}
    direction = fds[0]['direction']

    if direction == 'down':
        zoushi = {'走势': '向下',
                  '类型': '下跌',
                  'start_time': fds[0]['start_dt'],
                  'end_time': fds[-1]['end_dt'],
                  'section_amount': len(fds),
                  'zs_high': min(fds[-3]['high'], fds[-1]['high']),
                  'zs_low': max(fds[-1]['low'], fds[-2]['low']),
                  'high': max(fds[0]['high'], fds[1]['high']),
                  'low': min(fds[-1]['low'], fds[-2]['low']),
                  'power': calculate_macd_power(macd_list, fds[0]['start_dt'], fds[-1]['end_dt'], mode='xd', direction=direction),
                  'beichi': check_trend_beichi(fds)}
    elif direction == 'up':
        zoushi = {'走势': '向上',
                  '类型': '上涨',
                  'start_time': fds[0]['start_dt'],
                  'end_time': fds[-1]['end_dt'],
                  'section_amount': len(fds),
                  'zs_high': min(fds[-1]['high'], fds[-3]['high']),
                  'zs_low': max(fds[-3]['low'], fds[-2]['low']),
                  'high': max(fds[-1]['high'], fds[-2]['high']),
                  'low': min(fds[1]['low'], fds[0]['low']),
                  'power': calculate_macd_power(macd_list, fds[0]['start_dt'], fds[-1]['end_dt'], mode='xd', direction=direction),
                  'beichi': check_trend_beichi(fds)}

    return zoushi


def judge_3fds_zoushi(fds, macd_list):
    zoushi = {}

    direction = fds[0]['direction']

    if direction == 'down':
        if fds[0]['high'] > fds[1]['high'] * beyond_zs_ratio or fds[0]['low'] > fds[2]['low'] * beyond_zs_ratio:
            zoushi = {'走势': '向下盘整',
                      '类型': '下跌',
                      'start_time': fds[0]['start_dt'],
                      'end_time': fds[2]['end_dt'],
                      'section_amount': len(fds),
                      'zs_high': min(fds[0]['high'], fds[1]['high']),
                      'zs_low': max(fds[1]['low'], fds[2]['low']),
                      'high': max(fds[0]['high'], fds[1]['high']),
                      'low': min(fds[1]['low'], fds[2]['low']),
                      'power': calculate_macd_power(macd_list, fds[0]['start_dt'], fds[-1]['end_dt'], mode='xd', direction=direction),
                      'beichi': check_trend_beichi(fds)}
        else:
            zoushi = {'走势': '向下盘整',
                      '类型': '盘整',
                      'start_time': fds[0]['start_dt'],
                      'end_time': fds[2]['end_dt'],
                      'section_amount': len(fds),
                      'zs_high': min(fds[0]['high'], fds[1]['high']),
                      'zs_low': max(fds[1]['low'], fds[2]['low']),
                      'high': max(fds[0]['high'], fds[1]['high']),
                      'low': min(fds[1]['low'], fds[2]['low']),
                      'power': calculate_macd_power(macd_list, fds[0]['start_dt'], fds[-1]['end_dt'], mode='xd', direction=direction),
                      'beichi': check_trend_beichi(fds)}
    elif direction == 'up':
        if fds[1]['low'] > fds[0]['low'] * beyond_zs_ratio or fds[2]['high'] > fds[1]['high'] * beyond_zs_ratio:
            zoushi = {'走势': '向上盘整',
                      '类型': '上涨',
                      'start_time': fds[0]['start_dt'],
                      'end_time': fds[2]['end_dt'],
                      'section_amount': len(fds),
                      'zs_high': min(fds[1]['high'], fds[2]['high']),
                      'zs_low': max(fds[0]['low'], fds[1]['low']),
                      'high': max(fds[0]['high'], fds[1]['high']),
                      'low': min(fds[1]['low'], fds[2]['low']),
                      'power': calculate_macd_power(macd_list, fds[0]['start_dt'], fds[-1]['end_dt'], mode='xd', direction=direction),
                      'beichi': check_trend_beichi(fds)}
        else:
            zoushi = {'走势': '向上盘整',
                      '类型': '盘整',
                      'start_time': fds[0]['start_dt'],
                      'end_time': fds[2]['end_dt'],
                      'section_amount': len(fds),
                      'zs_high': min(fds[0]['high'], fds[1]['high']),
                      'zs_low': max(fds[1]['low'], fds[2]['low']),
                      'high': max(fds[0]['high'], fds[1]['high']),
                      'low': min(fds[1]['low'], fds[2]['low']),
                      'power': calculate_macd_power(macd_list, fds[0]['start_dt'], fds[-1]['end_dt'], mode='xd', direction=direction),
                      'beichi': check_trend_beichi(fds)}
    return zoushi


def judge_zoushi(fds, macd_list):
    length = len(fds)
    if 3 > length:
        return {}
    elif 3 == length:
        return judge_3fds_zoushi(fds, macd_list)
    else:
        return judge_more_than_3fds_zoushi(fds, macd_list)


def construct_zoushi(fds, macd_list):
    length = len(fds)

    if length < 3:
        return zoushi_list

    for i in range(0, length-1):
        tmp_fds.append(fds[i])
        tmp_length = len(tmp_fds)
        if tmp_length < 3 and i < length -2:
            continue

        if tmp_length % 2 == 0:
            if tmp_fds[0]['direction'] == 'up' and tmp_fds[-1]['low'] > tmp_fds[-3]['high']:
                continue
            elif tmp_fds[0]['direction'] == 'down' and tmp_fds[-1]['high'] < tmp_fds[-3]['low']:
                continue

            zoushi_list.append(judge_zoushi(tmp_fds[0:-1], macd_list))
            tmp_fds.clear()
            tmp_fds.append(fds[i])

        elif tmp_length % 2 == 1:
            if tmp_fds[0]['direction'] == 'up' and tmp_fds[-1]['high'] > tmp_fds[-3]['high']:
                continue
            elif tmp_fds[0]['direction'] == 'down' and tmp_fds[-1]['low'] < tmp_fds[-3]['low']:
                continue
            zoushi_list.append(judge_zoushi(tmp_fds, macd_list))
            tmp_fds.clear()
            tmp_fds.append(fds[i-1])
            tmp_fds.append(fds[i])
    if len(tmp_fds)  == 1 and tmp_fds[0]['direction'] == 'down' or len(tmp_fds) == 2 and tmp_fds[1]['direction'] == 'down':
        zoushi_list.append(judge_zoushi(fds[-3:], macd_list))
    elif len(tmp_fds) > 2:
        zoushi_list.append(judge_zoushi(tmp_fds, macd_list))
    return zoushi_list









