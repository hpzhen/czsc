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

    def get_kline_period(self, symbol: List[str], start_date: str,
                         end_date: str, freq: str, fq=True) -> List[RawBar]:

        bars = []

        if (freq in ("day", "D", "d")):
            self.repo = self.database.get_collection('stock_day')
        elif (freq.lower().find("min")):
            self.repo = self.database.get_collection("stock_min")

        else:
            return None
        cursor = self.repo.find({
            'code': {'$in': symbol}, "date": {
                "$lte": end_date,
                "$gte": start_date}}, batch_size=100000)

        res = pd.DataFrame([item for item in cursor]).sort_values(by='date', ascending=True)

        for row in res.index:
            bars.append(RawBar(symbol=res.loc[row]['code'], dt=res.loc[row]['date'], id=row, freq=freq_map[freq],
                               open=round(res.loc[row]['open'], 2),
                               close=round(float(res.loc[row]['close']), 2),
                               high=round(float(res.loc[row]['high']), 2),
                               low=round(float(res.loc[row]['low']), 2),
                               vol=int(res.loc[row]['vol']), amount=int(float(res.loc[row]['amount']))))
        return bars


if __name__ == '__main__':
    db = local_mongo()
    db.get_kline_period(symbol=['000001'], start_date='2022-01-01', end_date='2022-01-22', freq='D')
