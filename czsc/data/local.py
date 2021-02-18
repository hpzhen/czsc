import numpy
from QUANTAXIS import DATABASE, datetime, QA_fetch_stock_day_adv, QA_util_to_json_from_pandas, QA_util_log_info, \
    QA_util_date_valid, QA_util_code_tolist
import pandas as pd



def QA_fetch_stock_week(code, start, end, format='pd', collections=DATABASE.stock_week):
    start = str(start)[0:10]
    end = str(end)[0:10]
    code = QA_util_code_tolist(code)

    if QA_util_date_valid(end):
        cursor = collections.find({
            'code': {'$in': code}, "date": {
                "$lte": end,
                "$gte": start}}, {"_id": 0}, batch_size=10000)

        res = pd.DataFrame([item for item in cursor])
        try:
            res = res.assign(date=pd.to_datetime(
                res.date)).drop_duplicates((['date', 'code'])).query('vol>1')
            res['code'] = res['code'].astype(str)
            # res = res.ix[:, ['code', 'open', 'high', 'low',
            #                  'close', 'volume', 'amount', 'date', 'mv', 'liquidity_mv']]
        except:
            res = None
        if format in ['P', 'p', 'pandas', 'pd']:
            res.rename({'date': 'dt', 'code': 'symbol'}, axis=1, inplace=True)

            res = res[['symbol', 'dt', 'open', 'close', 'high', 'low', 'vol']]
            return res
        elif format in ['json', 'dict']:
            return QA_util_to_json_from_pandas(res)
        # 多种数据格式
        elif format in ['n', 'N', 'numpy']:
            return numpy.asarray(res)
        elif format in ['list', 'l', 'L']:
            return numpy.asarray(res).tolist()
        else:
            print(
                "QA Error QA_fetch_stock_day format parameter %s is none of  \"P, p, pandas, pd , json, dict , n, N, numpy, list, l, L, !\" " % format)
            return None
    else:
        QA_util_log_info(
            'QA Error QA_fetch_stock_day data parameter start=%s end=%s is not right' % (start, end))



def get_local_day_kline(symbol, end, start):
    df = QA_fetch_stock_day_adv(symbol, start=start, end=end).to_pd().reset_index()
    df.rename({'date': 'dt', 'volume': 'vol', 'code': 'symbol'}, axis=1, inplace=True)

    df = df[['symbol', 'dt', 'open', 'close', 'high', 'low', 'vol']]

    return df





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
    # res = get_local_kline(['000001'], "2020-11-30", "30min", start="2020-11-25")
    res = get_local_day_kline('000001', '2019-12-31', '2019-01-01')
    print(res)