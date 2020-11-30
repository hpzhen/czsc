from QUANTAXIS import DATABASE, datetime
import pandas as pd


def get_local_kline(symbol,  end, freq, start=None, count=None):
    dbReader = DATABASE.stock_min

    if start == 'all':
        start = '2000-01-01'
        end = str(datetime.date.today())

    start = str(start)[0:10]
    end = str(end)[0:10]

    if start == 'all':
        start = '2000-01-01'
        end = str(datetime.date.today())

    cursor = dbReader.find({
        'code': {'$in': symbol}, "date": {
            "$lte": end,
            "$gte": start}, 'type':freq}, {"_id": 0}, batch_size=100000)

    res = pd.DataFrame([item for item in cursor])
    try:
        res = res.assign(date=pd.to_datetime(
            res.datetime)).drop_duplicates((['datetime', 'code']))
        res['code'] = res['code'].astype(str)
        res.rename({'datetime': 'dt', 'volume': 'vol', 'code': 'symbol'}, axis=1, inplace=True)

        res = res[['symbol', 'dt', 'open', 'close', 'high', 'low', 'vol']]
        for col in ['open', 'close', 'high', 'low', 'vol']:
            res.loc[:, col] = res[col].apply(lambda x: round(float(x), 2))
        res.loc[:, "dt"] = pd.to_datetime(res['dt'])

    except:
        print('Error reading' + str(dbReader) + 'features from db')
        res = None
    return res

if __name__ == '__main__':
    res = get_local_kline(['000001'], "2020-11-30", "30min", start="2020-11-25")
    print(res)