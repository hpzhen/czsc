import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from datetime import datetime

from czsc import CZSC
from czsc.data.local_mongo import local_mongo
from czsc.signals import cxt_third_buy_V230228


class MultiThreadCulculator:

    def __init__(self, start: str, end: str, freq: str):
        self.maximum_thread_number = 3
        self.db = local_mongo()
        self.start = start
        self.end = end
        self.freq = freq

    def __calculate_singal(self, c: CZSC) -> OrderedDict:
        s = OrderedDict({"symbol": c.symbol, "dt": c.bars_raw[-1].dt, "close": c.bars_raw[-1].close})
        # 倒0，特指未确认完成笔
        # 倒1，倒数第1笔的缩写，表示第N笔
        # 倒2，倒数第2笔的缩写，表示第N-1笔
        # 倒3，倒数第3笔的缩写，表示第N-2笔
        # 以此类推
        # for i in range(1, 3):
        #     s.update(get_s_three_bi(c, i))
        s.update(cxt_third_buy_V230228(c))
        return s

    def calculate_signals(self, code: str):
        bars = self.db.get_kline_period([code], self.start, self.end, self.freq)
        c = CZSC(bars, get_signals=self.__calculate_singal)
        if c.signals[f'日线_D1_三买辅助V230228'].find(f'三买') >= 0:
            print(c.signals)
        print(threading.currentThread().getName() + " :handled stock code: " + code)

    def do_job(self):
        stock_list = self.db.get_stock_list().pop("code").to_list()[:200]

        with ThreadPoolExecutor(max_workers=self.maximum_thread_number) as t:
            all_tasks = [t.submit(self.calculate_signals, str(code)) for code in stock_list]
        wait(all_tasks, return_when=ALL_COMPLETED)


if __name__ == '__main__':
    # print("start time:" + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    start = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    worker = MultiThreadCulculator("2022-01-01", "2022-06-30", "D")
    worker.do_job()
    print("start time:" + start)
    print("end time: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))