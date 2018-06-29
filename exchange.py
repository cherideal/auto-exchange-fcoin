from fcoin import Fcoin
import ConfigParser
import os

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
#print 'symbols:%s' %symbols

def change2ft(currency, available):
    for symbol_info in symbols:
        if currency != symbol_info['quote_currency']:
            continue

        symbol = symbol_info['name']
        tick = fcoin.get_market_ticker(symbol)

        cur_price = tick['data']['ticker'][0]
        print 'currency:%s, symbol:%s, available:%s, cur_price:%s' % (currency, symbol, available, cur_price)

        break

def change2base(currency, available):
    for symbol_info in symbols:
        if currency == symbol_info['base_currency']:
            if symbol_info['quote_currency'] in base_coin:
                symbol = symbol_info['name']
            else:
                continue

            tick = fcoin.get_market_ticker(symbol)

            cur_price = tick['data']['ticker'][0]
            print 'currency:%s, symbol:%s, available:%s, cur_price:%s' % (currency, symbol, available, cur_price)

            result = fcoin.sell(symbol, cur_price, available)
            print result

            break

def main():
    balances = fcoin.get_balance()

    #print 'balances:%s' %balances
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



