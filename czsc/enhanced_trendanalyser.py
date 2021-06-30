import sys

from czsc.analyze import calculate_macd_power


class EnhancedTrendAnalyser:
    def __init__(self, fds, macd_list=None):
        self.__exceedRatio = 1.0
        self.__zoushi_list = []
        self.__input_fds = fds
        self.__macd_list = macd_list
        self._tmp_fds = []
        self.__construct_zoushi()
        self.__merge_zoushi_list()

    def __merge_zoushi_list(self):
        zoushi_len = len(self.__zoushi_list)
        tmp_list = []
        result = []

        for i in range(0, zoushi_len):
            tmp_list.append(self.__zoushi_list[i])
            if len(tmp_list) < 2:
                continue

            try:
                if tmp_list[-2]['direction'] == tmp_list[-1]['direction']:
                    continue
                else:
                    result.append(self.__merge_zoushi(tmp_list[:-1]))
                    del tmp_list[:-1]
            except:
                print("Error")
        if len(tmp_list) > 0:
            result.append(self.__merge_zoushi(tmp_list))

        self.__zoushi_list.clear()
        self.__zoushi_list.extend(result)

    def __merge_zoushi(self, fd_list):
        zoushi = {}

        if len(fd_list) == 1:
            return fd_list[0]

        if len(fd_list) > 1:

            def __count_fd_amount(fds):
                amount = 0
                for j in range(0, len(fds)):
                    amount += fds[j]['section_amount']
                return amount

            if fd_list[0]['direction'] == 'down':
                zoushi = {'走势': fd_list[0]['走势'],
                          '类型': '盘整',
                          'symbol': fd_list[0]['symbol'],
                          'start_dt': fd_list[0]['start_dt'],
                          'end_dt': fd_list[-1]['end_dt'],
                          'section_amount': __count_fd_amount(fd_list),
                          'zs_high': fd_list[-1]['zs_high'],
                          'zs_low': fd_list[-1]['zs_low'],
                          'high': fd_list[0]['high'],
                          'low': fd_list[-1]['low'],
                          'direction': 'down',
                          'power': calculate_macd_power(self.__macd_list, fd_list[0]['start_dt'],
                                                        fd_list[-1]['end_dt'], mode='bi', direction='down'),
                          'beichi': fd_list[-2]['beichi']}
            elif fd_list[0]['direction'] == 'up':
                zoushi = {'走势': fd_list[0]['走势'],
                          '类型': '盘整',
                          'symbol': fd_list[0]['symbol'],
                          'start_dt': fd_list[0]['start_dt'],
                          'end_dt': fd_list[-1]['end_dt'],
                          'section_amount': __count_fd_amount(fd_list),
                          'zs_high': fd_list[-1]['zs_high'],
                          'zs_low': fd_list[-1]['zs_low'],
                          'high': fd_list[-1]['high'],
                          'low': fd_list[0]['low'],
                          'direction': 'up',
                          'power': calculate_macd_power(self.__macd_list, fd_list[0]['start_dt'],
                                                        fd_list[-1]['end_dt'], mode='bi', direction='down'),
                          'beichi': fd_list[-1]['beichi']}
            return zoushi

    def __construct_single_up_or_down_zoushi(self, fds):
        zoushi = {}
        if fds[0]['direction'] == 'down':
            zoushi = {'走势': '向下走势',
                      '类型': '下跌',
                      'symbol': fds[0]['symbol'],
                      'start_dt': fds[0]['start_dt'],
                      'end_dt': fds[-1]['end_dt'],
                      'section_amount': len(fds),
                      'zs_high': fds[-1]['high'],
                      'zs_low': fds[-3]['low'],
                      'high': max(fds[0]['high'], fds[2]['high']),
                      'low': min(fds[-1]['low'], fds[-3]['low']),
                      'direction': 'down',
                      'power': calculate_macd_power(self.__macd_list, fds[0]['start_dt'],
                                                    fds[-1]['end_dt'], mode='bi', direction='down'),
                      'beichi': self.__check_trend_beichi(fds)}
        elif fds[0]['direction'] == 'up':
            zoushi = {'走势': '向上走势',
                      '类型': '上涨',
                      'symbol': fds[0]['symbol'],
                      'start_dt': fds[0]['start_dt'],
                      'end_dt': fds[-1]['end_dt'],
                      'section_amount': len(fds),
                      'zs_high': min(fds[-3]['high'], fds[-1]['high']),
                      'zs_low': fds[-1]['low'],
                      'high': max(fds[-1]['high'], fds[-2]['high']),
                      'low': min(fds[0]['low'], fds[1]['low']),
                      'direction': 'up',
                      'power': calculate_macd_power(self.__macd_list, fds[0]['start_dt'],
                                                    fds[-1]['end_dt'], mode='bi', direction='down'),
                      'beichi': self.__check_trend_beichi(fds)}

        return zoushi

    def __construct_3fds_zoushi(self, fds):
        zoushi = {}

        direction = fds[0]['direction']
        fd_high = max(fds[0]['high'], fds[2]['high'])
        fd_low = min(fds[0]['low'], fds[2]['low'])

        if direction == 'down':
            if fds[0]['high'] > fds[2]['high'] * self.__exceedRatio or fds[0]['low'] > \
                    fds[2]['low'] * self.__exceedRatio:
                zoushi = {'走势': '向下盘整',
                          '类型': '下跌',
                          'symbol': fds[0]['symbol'],
                          'start_dt': fds[0]['start_dt'],
                          'end_dt': fds[2]['end_dt'],
                          'section_amount': len(fds),
                          'zs_high': min(fds[0]['high'], fds[1]['high']),
                          'zs_low': max(fds[1]['low'], fds[2]['low']),
                          'high': fds[0]['high'],
                          'low': fds[2]['low'],
                          'direction': 'down' if fds[0]['high']> fds[2]['low'] else 'up',
                          'power': calculate_macd_power(self.__macd_list, fds[0]['start_dt'],
                                                        fds[-1]['end_dt'], mode='bi', direction=direction),
                          'beichi': self.__check_trend_beichi(fds)}
            else:
                zoushi = {'走势': '向下盘整',
                          '类型': '盘整',
                          'symbol': fds[0]['symbol'],
                          'start_dt': fds[0]['start_dt'],
                          'end_dt': fds[2]['end_dt'],
                          'section_amount': len(fds),
                          'zs_high': min(fds[0]['high'], fds[1]['high']),
                          'zs_low': max(fds[1]['low'], fds[2]['low']),
                          'high': fds[0]['high'],
                          'low': fds[2]['low'],
                          'direction': 'down' if fds[0]['high']> fds[2]['low'] else 'up',
                          'power': calculate_macd_power(self.__macd_list, fds[0]['start_dt'],
                                                        fds[-1]['end_dt'], mode='bi', direction=direction),
                          'beichi': self.__check_trend_beichi(fds)}
        elif direction == 'up':
            if fds[1]['low'] > fds[0]['low'] * self.__exceedRatio \
                    or fds[2]['high'] > fds[1]['high'] * self.__exceedRatio:
                zoushi = {'走势': '向上盘整',
                          '类型': '上涨',
                          'symbol': fds[0]['symbol'],
                          'start_dt': fds[0]['start_dt'],
                          'end_dt': fds[2]['end_dt'],
                          'section_amount': len(fds),
                          'zs_high': min(fds[1]['high'], fds[2]['high']),
                          'zs_low': max(fds[0]['low'], fds[1]['low']),
                          'high': fds[2]['high'],
                          'low': fds[0]['low'],
                          'direction': 'up' if fds[2]['high'] > fds[0]['low'] else 'down',
                          'power': calculate_macd_power(self.__macd_list, fds[0]['start_dt'],
                                                        fds[-1]['end_dt'], mode='bi', direction=direction),
                          'beichi': self.__check_trend_beichi(fds)}
            else:
                zoushi = {'走势': '向上盘整',
                          '类型': '盘整',
                          'symbol': fds[0]['symbol'],
                          'start_dt': fds[0]['start_dt'],
                          'end_dt': fds[2]['end_dt'],
                          'section_amount': len(fds),
                          'zs_high': min(fds[0]['high'], fds[1]['high']),
                          'zs_low': max(fds[1]['low'], fds[2]['low']),
                          'high': fds[2]['high'],
                          'low': fds[0]['low'],
                          'direction': 'up' if fds[2]['high'] > fds[0]['low'] else 'down',
                          'power': calculate_macd_power(self.__macd_list, fds[0]['start_dt'],
                                                        fds[-1]['end_dt'], mode='bi', direction=direction),
                          'beichi': self.__check_trend_beichi(fds)}
        return zoushi

    def __build_zoushi(self, fds):

        if len(fds) < 3:
            return None
        elif len(fds) == 3:
            return self.__construct_3fds_zoushi(fds)
        else:
            assert len(fds) % 2 == 1
            return self.__construct_single_up_or_down_zoushi(fds)

    def __handle_left_fds(self):
        left_sections = len(self._tmp_fds)
        if left_sections >= 3:
            if left_sections % 2 == 1:
                self.__zoushi_list.append(self.__build_zoushi(self._tmp_fds))
                self._tmp_fds.clear()
            else:
                self.__zoushi_list.append(self.__build_zoushi(self._tmp_fds[:-1]))
                del self._tmp_fds[:-1]

    def __check_trend_beichi(self, fds=None):
        if fds is None:
            assert len(self._tmp_fds) > 2
            assert self._tmp_fds[0]['direction'] == self._tmp_fds[-1]['direction']
            if self._tmp_fds[-1]['power'] < self._tmp_fds[0]['power'] \
                    or self._tmp_fds[-1]['power'] < self._tmp_fds[-3]['power']:
                return True
        else:
            try:
                assert len(fds) > 2
                assert fds[-1]['direction'] == fds[-3]['direction']
            except:
                print('assert error: ' + sys._getframe().f_code.co_filename+":"+ str(sys._getframe().f_lineno))
            if fds[-1]['power'] < fds[-3]['power']:
                return True
        return False

    def _judge_buy_or_sell_points(self):
        try:
            assert len(self._tmp_fds) < 3
        except:
            print("assert failed:" + sys._getframe().f_code.co_filename+" "+str(sys._getframe().f_lineno))
        result = {}

        if self.__check_trend_beichi(fds=self.__input_fds[-3:]) == False:
            return result

        if len(self._tmp_fds) == 0:
            if self.__zoushi_list[-1]['direction'] == 'down':
                result = {'买卖点': '第一买点',
                          '时间': self.__zoushi_list[-1]['end_dt'],
                          'symbol': self.__zoushi_list[-1]['symbol']}
            elif self.__zoushi_list[-1]['direction'] == 'up':
                result = {'买卖点': '第一卖点',
                          '时间': self.__zoushi_list[-1]['end_dt'],
                          'symbol': self.__zoushi_list[-1]['symbol']}
        elif len(self._tmp_fds) == 1:
            if self.__zoushi_list[-2]['direction'] == 'down' \
                    and self.__zoushi_list[-1]['direction'] == 'up' \
                    and self.__input_fds[-1]['low'] > self.__input_fds[-3]['high']:
                result = {'买卖点': '第三买点',
                          '时间': self.__zoushi_list[-1]['end_dt'],
                          'symbol': self.__zoushi_list[-1]['symbol']}
            elif self.__zoushi_list[-2]['direction'] == 'up' \
                    and self.__zoushi_list[-1]['direction'] == 'down' \
                    and self.__input_fds[-1]['high'] < self.__input_fds[-3]['low']:
                result = {'买卖点': '第三卖点',
                          '时间': self.__zoushi_list[-1]['end_dt'],
                          'symbol': self.__zoushi_list[-1]['symbol']}

        elif len(self._tmp_fds) == 2:
            if self.__zoushi_list[-1]['direction'] == 'down' \
                    and self.__input_fds[-1]['low'] > self.__input_fds[-3]['low']:
                result = {'买卖点': '第二买点',
                          '时间': self.__zoushi_list[-1]['end_dt'],
                          'symbol': self.__zoushi_list[-1]['symbol']}
            elif self.__zoushi_list[-1]['direction'] == 'up' \
                    and self.__input_fds[-1]['high'] < self.__input_fds[-3]['high']:
                result = {'买卖点': '第二卖点',
                          '时间': self.__zoushi_list[-1]['end_dt'],
                          'symbol': self.__zoushi_list[-1]['symbol']}

        return result

    def __construct_zoushi(self):
        length = len(self.__input_fds)

        if length < 3:
            return self.__zoushi_list

        for i in range(0, length):
            self._tmp_fds.append(self.__input_fds[i])
            tmp_length = len(self._tmp_fds)

            if tmp_length < 4:
                continue

            if tmp_length % 2 == 0:
                if self._tmp_fds[0]['direction'] == 'down' \
                        and self._tmp_fds[-1]['high'] > self._tmp_fds[-3]['low']:
                    self.__zoushi_list.append(self.__build_zoushi(self._tmp_fds[:-1]))
                    del self._tmp_fds[:-1]

                elif self._tmp_fds[0]['direction'] == 'up' \
                        and self._tmp_fds[-1]['low'] < self._tmp_fds[-3]['high']:
                    self.__zoushi_list.append(self.__build_zoushi(self._tmp_fds[:-1]))
                    del self._tmp_fds[:-1]

            elif tmp_length % 2 == 1:
                if self._tmp_fds[0]['direction'] == 'down' \
                        and self._tmp_fds[-1]['low'] > self._tmp_fds[-3]['low']:
                    self.__zoushi_list.append(self.__build_zoushi(self._tmp_fds[:-2]))
                    del self._tmp_fds[0:-2]
                elif self._tmp_fds[0]['direction'] == 'up' \
                        and self._tmp_fds[-1]['high'] < self._tmp_fds[-3]['high']:
                    self.__zoushi_list.append(self.__build_zoushi(self._tmp_fds[:-2]))
                    del self._tmp_fds[0:-2]

        self.__handle_left_fds()


    def __enhanced_construct_zoushi(self):
        length = len(self.__input_fds)

        if length < 3:
            return self.__zoushi_list
        for i in range(0, length):
            self._tmp_fds.append(self.__input_fds[i])
            tmp_length = len(self._tmp_fds)

            if tmp_length < 3:
                continue
            elif tmp_length == 6:
                if self._tmp_fds[0]['direction'] == 'down':
                    if self._tmp_fds[5]['low'] > self._tmp_fds[2]['high']:
                        self.__zoushi_list.append(self.__construct_3fds_zoushi(self._tmp_fds[0:2]))
                        del self._tmp_fds[0:2]
                        continue
                elif self._tmp_fds[0]['direction'] == 'up':
                    if self._tmp_fds[5]['high'] < self._tmp_fds[2]['low']:
                        self.__zoushi_list.append(self.__construct_3fds_zoushi(self._tmp_fds[0:2]))
                        del self._tmp_fds[0:2]
                        continue
            elif tmp_length == 8:
                if self._tmp_fds[0]['direction'] == 'down':
                    if self._tmp_fds[5]['high'] > self._tmp_fds[2]['low']:
                        self.__zoushi_list.append(self.__construct_3fds_zoushi(self._tmp_fds[0:2]))
                        del self._tmp_fds[0:2]
                        continue
                elif self._tmp_fds[0]['direction'] == 'up':
                    if self._tmp_fds[5]['low'] < self._tmp_fds[2]['high']:
                        self.__zoushi_list.append(self.__construct_3fds_zoushi(self._tmp_fds[0:2]))
                        del self._tmp_fds[0:2]
                        continue
            elif tmp_length == 9:
                self.__zoushi_list.append(self.__construct_single_up_or_down_zoushi(self._tmp_fds))

    def get_zoushi_list(self):
        return self.__zoushi_list.copy()

    def get_tmp_list(self):
        return self._tmp_fds.copy()

    def getAnalysisResult(self):
        return self._judge_buy_or_sell_points()
