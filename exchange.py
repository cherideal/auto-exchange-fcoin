from fcoin import Fcoin
import ConfigParser
import os
import math

cf = ConfigParser.ConfigParser()
try:
    cf.read("../fcoin.conf")
    key = cf.get('api', 'key')
    secret = cf.get('api', 'secret')
except Exception:
    print 'please check the config file <fcoin.conf> in parent direction'
    exit(1)

fcoin = Fcoin()
fcoin.auth(key, secret)
base_coin = ['ft', 'eth', 'btc', 'usdt']
symbols = fcoin.get_symbols()

order_limit = {'zileth':10, 'omgeth':0.1, 'icxeth':0.1,
               'btmusdt':1, 'bchusdt':0.001, 'aeeth':1,
               'ltcusdt':0.001, 'zrxeth':1, 'xrpusdt':1,
               'bnbusdt':0.1, 'gtcft':1, 'zipeth':200,
               'etcusdt':0.001, 'ftbtc':3, 'fteth':3, 'ftusdt':3}

amount_limit = {'ftbtc':8, 'fteth':8, 'ftusdt':2}
def cut_other_decimal(value, decimal):
    values = str(value).split('.')
    res = values[0]
    if len(values) > 1 and decimal > 0:
        right = values[1][0: decimal]
        res = res + '.' + right
    return float(res)

def change2ft(currency, available):
    for symbol_info in symbols:
        if currency != symbol_info['quote_currency'] or 'ft' != symbol_info['base_currency']:
            continue

        symbol = symbol_info['name']
        amount_decimal = amount_limit[symbol]
        price_decimal = int(symbol_info['price_decimal'])

        tick = fcoin.get_market_ticker(symbol)
        cur_price = tick['data']['ticker'][0]

        available_reverse = float(available) / float(cur_price)
        cur_price = round(float(cur_price), price_decimal)
        amount = cut_other_decimal(available_reverse, int(amount_decimal))

        print 'buy currency:%s, symbol:%s, available:%s, amount:%s, cur_price:%s, amount_decimal:%s, price_decimal:%s' \
              % (currency, symbol, available, amount, cur_price, amount_decimal, price_decimal)
        limit = order_limit[symbol]
        if limit <= amount:
            result = fcoin.buy(symbol, cur_price, amount)
            print result

        break


def change2base(currency, available):
    for symbol_info in symbols:
        if currency == symbol_info['base_currency']:
            if symbol_info['quote_currency'] in base_coin:
                symbol = symbol_info['name']
                amount_decimal = int(symbol_info['amount_decimal'])
                price_decimal = int(symbol_info['price_decimal'])
            else:
                continue

            tick = fcoin.get_market_ticker(symbol)
            cur_price = tick['data']['ticker'][0]

            cur_price = round(float(cur_price), price_decimal)
            amount = cut_other_decimal(available, int(amount_decimal))

            print 'sell currency:%s, symbol:%s, available:%s, amount:%s, cur_price:%s, amount_decimal:%s, price_decimal:%s' \
                  % (currency, symbol, available, amount, cur_price, amount_decimal, price_decimal)

            limit = order_limit[symbol]
            if limit <= amount:
                result = fcoin.sell(symbol, cur_price, amount)
                print result

            break

def main():
    balances = fcoin.get_balance()

    datas = balances['data']
    if datas:
        for data in datas:
            currency = data['currency']
            available = data['available']
            if currency not in base_coin:
                change2base(currency, available)

        for data in datas:
            currency = data['currency']
            available = data['available']

            if currency != 'ft' and currency in base_coin:
                change2ft(currency, available)

if __name__ == "__main__":
    main()



