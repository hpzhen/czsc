import os
from typing import List

import pandas as pd
import pymongo as pymongo

from czsc import RawBar
from czsc.data.jq import freq_map

DEFAULT_MONGO = os.getenv('MONGODB', 'localhost')
DEFAULT_DB_URI = 'mongodb://127.0.0.1:27017/'


def get_db():
    client = pymongo.MongoClient(DEFAULT_DB_URI)
    return client.get_database('quantaxis')


def list_dbs():
    client = pymongo.MongoClient()
    dbs = client.get_database('quantaxis')
    collection = dbs.get_collection('stock_day')
    cursor = collection.find({
        'code': {'$in': ['000001']}, "date": {
            "$lte": '2022-01-10',
            "$gte": '2022-01-01'}}, batch_size=100000)
    res = pd.DataFrame([item for item in cursor])

    print(res)


class local_mongo:

    def __init__(self):
        self.database = get_db()
        self.repo = None
        self.cursor = None

    def __get_day_kline(self, symbol, start_date, end_date):
        repo = self.database.get_collection('stock_day')
        self.cursor = repo.find({'code': {'$in': symbol}, "date": {
            "$lte": end_date,
            "$gte": start_date}}, batch_size=100000)
        return pd.DataFrame([item for item in self.cursor]).sort_values(by='date', ascending=True)

    def __convert_to_day_bars(self, res, freq):
        bars = []
        for row in res.index:
            bars.append(
                RawBar(symbol=res.loc[row]['code'], dt=res.loc[row]['date'], id=row, freq=freq_map[freq],
                       open=round(res.loc[row]['open'], 2),
                       close=round(float(res.loc[row]['close']), 2),
                       high=round(float(res.loc[row]['high']), 2),
                       low=round(float(res.loc[row]['low']), 2),
                       vol=int(res.loc[row]['vol']), amount=int(float(res.loc[row]['amount']))))
        return bars

    def __get_min_kline(self, symbol, start_date, end_date, freq):
        repo = self.database.get_collection("stock_min")
        self.cursor = repo.find({
            'code': {'$in': symbol}, "datetime": {
                "$lte": end_date,
                "$gte": start_date}, 'type': freq}, batch_size=100000)
        return pd.DataFrame([item for item in self.cursor]).sort_values(by='time_stamp', ascending=True)

    def __convert_to_min_bars(self, res, freq):
        bars = []
        for row in range(0, len(res)):
            bars.append(
                RawBar(symbol=res.loc[row]['code'], dt=res.loc[row]['datetime'], id=row, freq=freq_map[freq],
                       open=round(res.loc[row]['open'], 2),
                       close=round(float(res.loc[row]['close']), 2),
                       high=round(float(res.loc[row]['high']), 2),
                       low=round(float(res.loc[row]['low']), 2),
                       vol=int(res.loc[row]['vol']), amount=int(float(res.loc[row]['amount']))))
        return bars

    def get_kline_period(self, symbol: List[str], start_date: str,
                         end_date: str, freq: str, fq=True) -> List[RawBar]:
        bars = []

        if freq in ("day", "D", "d"):
            res = self.__get_day_kline(symbol, start_date, end_date)
            bars = self.__convert_to_day_bars(res, freq)
        elif freq.lower().find("min"):
            res = self.__get_min_kline(symbol, start_date, end_date, freq)
            bars = self.__convert_to_min_bars(res, freq)

        return bars

    def get_stock_list(self):
        repo = self.database.get_collection("stock_list")
        self.cursor = repo.find({}, batch_size=100000)
        return pd.DataFrame([item for item in self.cursor]).sort_values(by='code', ascending=True)



if __name__ == '__main__':
    db = local_mongo()

    # stock_list = db.get_stock_list()
    db.get_kline_period(symbol=['000001'], start_date='2022-01-01', end_date='2022-06-30', freq='D')

    # db.get_kline_period(symbol=['000001'], start_date='2022-01-05 00:00:00', end_date='2022-01-21 10:50:30',
    #                     freq='15min')
