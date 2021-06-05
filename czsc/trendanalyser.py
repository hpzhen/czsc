from czsc.analyze import calculate_macd_power


class TrendAnalyser:

    def __init__(self, fds, macd_list=None):
        self.__exceedRatio = 1.0
        self.__zoushi_list = []
        self.__input_fds = fds
        self.__macd_list = macd_list
        self._tmp_fds = []

    def __check_trend_beichi(self, fds=None):
        if fds is None:
            assert len(self._tmp_fds) > 2
            assert self._tmp_fds[0]['direction'] == self._tmp_fds[-1]['direction']
            if self._tmp_fds[-1]['power'] < self._tmp_fds[0]['power'] \
                    or self._tmp_fds[-1]['power'] < self._tmp_fds[-3]['power']:
                return True
        else:
            assert len(fds) > 2
            assert fds[-1]['direction'] == fds[0]['direction']
            if fds[-1]['power'] < fds[0]['power'] or fds[-1]['power'] < fds[-3]['power']:
                return True
        return False

    def __judge_more_than_3fds_zoushi(self):
        zoushi = {}
        direction = self._tmp_fds[0]['direction']

        if direction == 'down':
            zoushi = {'走势': '向下',
                      '类型': '下跌',
                      'symbol': self._tmp_fds[0]['symbol'],
                      'start_time': self._tmp_fds[0]['start_dt'],
                      'end_time': self._tmp_fds[-1]['end_dt'],
                      'section_amount': len(self._tmp_fds),
                      'zs_high': min(self._tmp_fds[-3]['high'], self._tmp_fds[-1]['high']),
                      'zs_low': max(self._tmp_fds[-1]['low'], self._tmp_fds[-2]['low']),
                      'high': max(self._tmp_fds[0]['high'], self._tmp_fds[1]['high']),
                      'low': min(self._tmp_fds[-1]['low'], self._tmp_fds[-2]['low']),
                      'power': calculate_macd_power(self.__macd_list, self._tmp_fds[0]['start_dt'],
                                                    self._tmp_fds[-1]['end_dt'], mode='xd',
                                                    direction=direction),
                      'beichi': self.__check_trend_beichi()}
        elif direction == 'up':
            zoushi = {'走势': '向上',
                      '类型': '上涨',
                      'symbol': self._tmp_fds[0]['symbol'],
                      'start_time': self._tmp_fds[0]['start_dt'],
                      'end_time': self._tmp_fds[-1]['end_dt'],
                      'section_amount': len(self._tmp_fds),
                      'zs_high': min(self._tmp_fds[-1]['high'], self._tmp_fds[-3]['high']),
                      'zs_low': max(self._tmp_fds[-3]['low'], self._tmp_fds[-2]['low']),
                      'high': max(self._tmp_fds[-1]['high'], self._tmp_fds[-2]['high']),
                      'low': min(self._tmp_fds[1]['low'], self._tmp_fds[0]['low']),
                      'power': calculate_macd_power(self.__macd_list, self._tmp_fds[0]['start_dt'],
                                                    self._tmp_fds[-1]['end_dt'], mode='xd',
                                                    direction=direction),
                      'beichi': self.__check_trend_beichi()}

        return zoushi

    def __judge_3fds_zoushi(self):
        zoushi = {}

        direction = self._tmp_fds[0]['direction']

        if direction == 'down':
            if self._tmp_fds[0]['high'] > self._tmp_fds[1]['high'] * self.__exceedRatio or self._tmp_fds[0]['low'] > \
                    self._tmp_fds[2]['low'] * self.__exceedRatio:
                zoushi = {'走势': '向下盘整',
                          '类型': '下跌',
                          'symbol': self._tmp_fds[0]['symbol'],
                          'start_time': self._tmp_fds[0]['start_dt'],
                          'end_time': self._tmp_fds[2]['end_dt'],
                          'section_amount': len(self._tmp_fds),
                          'zs_high': min(self._tmp_fds[0]['high'], self._tmp_fds[1]['high']),
                          'zs_low': max(self._tmp_fds[1]['low'], self._tmp_fds[2]['low']),
                          'high': max(self._tmp_fds[0]['high'], self._tmp_fds[1]['high']),
                          'low': min(self._tmp_fds[1]['low'], self._tmp_fds[2]['low']),
                          'power': calculate_macd_power(self.__macd_list, self._tmp_fds[0]['start_dt'],
                                                        self._tmp_fds[-1]['end_dt'], mode='xd', direction=direction),
                          'beichi': self.__check_trend_beichi()}
            else:
                zoushi = {'走势': '向下盘整',
                          '类型': '盘整',
                          'symbol': self._tmp_fds[0]['symbol'],
                          'start_time': self._tmp_fds[0]['start_dt'],
                          'end_time': self._tmp_fds[2]['end_dt'],
                          'section_amount': len(self._tmp_fds),
                          'zs_high': min(self._tmp_fds[0]['high'], self._tmp_fds[1]['high']),
                          'zs_low': max(self._tmp_fds[1]['low'], self._tmp_fds[2]['low']),
                          'high': max(self._tmp_fds[0]['high'], self._tmp_fds[1]['high']),
                          'low': min(self._tmp_fds[1]['low'], self._tmp_fds[2]['low']),
                          'power': calculate_macd_power(self.__macd_list, self._tmp_fds[0]['start_dt'],
                                                        self._tmp_fds[-1]['end_dt'], mode='xd', direction=direction),
                          'beichi': self.__check_trend_beichi()}
        elif direction == 'up':
            if self._tmp_fds[1]['low'] > self._tmp_fds[0]['low'] * self.__exceedRatio \
                    or self._tmp_fds[2]['high'] > self._tmp_fds[1]['high'] * self.__exceedRatio:
                zoushi = {'走势': '向上盘整',
                          '类型': '上涨',
                          'symbol': self._tmp_fds[0]['symbol'],
                          'start_time': self._tmp_fds[0]['start_dt'],
                          'end_time': self._tmp_fds[2]['end_dt'],
                          'section_amount': len(self._tmp_fds),
                          'zs_high': min(self._tmp_fds[1]['high'], self._tmp_fds[2]['high']),
                          'zs_low': max(self._tmp_fds[0]['low'], self._tmp_fds[1]['low']),
                          'high': max(self._tmp_fds[0]['high'], self._tmp_fds[1]['high']),
                          'low': min(self._tmp_fds[1]['low'], self._tmp_fds[2]['low']),
                          'power': calculate_macd_power(self.__macd_list, self._tmp_fds[0]['start_dt'],
                                                        self._tmp_fds[-1]['end_dt'], mode='xd', direction=direction),
                          'beichi': self.__check_trend_beichi()}
            else:
                zoushi = {'走势': '向上盘整',
                          '类型': '盘整',
                          'symbol': self._tmp_fds[0]['symbol'],
                          'start_time': self._tmp_fds[0]['start_dt'],
                          'end_time': self._tmp_fds[2]['end_dt'],
                          'section_amount': len(self._tmp_fds),
                          'zs_high': min(self._tmp_fds[0]['high'], self._tmp_fds[1]['high']),
                          'zs_low': max(self._tmp_fds[1]['low'], self._tmp_fds[2]['low']),
                          'high': max(self._tmp_fds[0]['high'], self._tmp_fds[1]['high']),
                          'low': min(self._tmp_fds[1]['low'], self._tmp_fds[2]['low']),
                          'power': calculate_macd_power(self.__macd_list, self._tmp_fds[0]['start_dt'],
                                                        self._tmp_fds[-1]['end_dt'], mode='xd', direction=direction),
                          'beichi': self.__check_trend_beichi()}
        return zoushi

    def __judge_zoushi(self):
        length = len(self._tmp_fds)
        if 3 > length:
            return {}
        elif 3 == length:
            return self.__judge_3fds_zoushi()
        else:
            if length % 2 == 0:
                self._tmp_fds.pop()
            return self.__judge_more_than_3fds_zoushi()

    def __construct_zoushi(self):
        length = len(self.__input_fds)

        if length < 3:
            return self.__zoushi_list

        for i in range(0, length):
            self._tmp_fds.append(self.__input_fds[i])
            tmp_length = len(self._tmp_fds)

            if tmp_length < 3:
                continue

            if tmp_length % 2 == 0:
                if self._tmp_fds[0]['direction'] == 'up' and self._tmp_fds[-1]['low'] > self._tmp_fds[-3]['high']:
                    continue
                elif self._tmp_fds[0]['direction'] == 'down' and self._tmp_fds[-1]['high'] < self._tmp_fds[-3]['low']:
                    continue

                self.__zoushi_list.append(self.__judge_zoushi())
                self._tmp_fds.clear()
                self._tmp_fds.append(self.__input_fds[i])

            elif tmp_length % 2 == 1:
                if self._tmp_fds[0]['direction'] == 'up' and self._tmp_fds[-1]['high'] > self._tmp_fds[-3]['high']:
                    continue
                elif self._tmp_fds[0]['direction'] == 'down' and self._tmp_fds[-1]['low'] < self._tmp_fds[-3]['low']:
                    continue
                self.__zoushi_list.append(self.__judge_zoushi())
                self._tmp_fds.clear()
                self._tmp_fds.append(self.__input_fds[i - 1])
                self._tmp_fds.append(self.__input_fds[i])
        if len(self._tmp_fds) > 2:
            self.__zoushi_list.append(self.__judge_zoushi())
            self._tmp_fds.clear()


    def _judge_buy_or_sell_points(self):
        try:
            assert len(self._tmp_fds) < 3
        except:
            print("assert error")
        result = {}

        if not self.__zoushi_list[-1]['beichi']:
            return result

        if len(self._tmp_fds) == 0:
            if self.__zoushi_list[-1]['direction'] == 'down':
                result = {'买卖点': '第一买点',
                          '时间': self.__zoushi_list[-1]['end_time'],
                          'symbol': self.__zoushi_list[-1]['symbol']}
            else:
                result = {'买卖点': '第一卖点',
                          '时间': self.__zoushi_list[-1]['end_time'],
                          'symbol': self.__zoushi_list[-1]['symbol']}
        elif len(self._tmp_fds) == 1 and self.__check_trend_beichi(fds=self.__input_fds[-3:]):
            if self.__zoushi_list[-1]['direction'] == 'down':
                result = {'买卖点': '第三买点',
                          '时间': self.__zoushi_list[-1]['end_time'],
                          'symbol': self.__zoushi_list[-1]['symbol']}
            else:
                result = {'买卖点': '第三卖点',
                          '时间': self.__zoushi_list[-1]['end_time'],
                          'symbol': self.__zoushi_list[-1]['symbol']}
        elif len(self._tmp_fds) == 2  \
                and self.__check_trend_beichi(fds=self.__input_fds[-3:]) \
                and self._tmp_fds[-1]['low'] > self._tmp_fds[0]['low']:
            result = {'买卖点': '第二卖点',
                      '时间': self.__zoushi_list[-1]['end_time'],
                      'symbol': self.__zoushi_list[-1]['symbol']}
        return result


    def getAnalysisResult(self):
        self.__construct_zoushi()
        return self._judge_buy_or_sell_points()
