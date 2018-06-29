from fcoin import Fcoin
import ConfigParser
import os

cf = ConfigParser.ConfigParser()
try:
    cf.read("../fcoin.conf")
    key = cf.get('api', 'key')
    secret = cf.get('api', 'secret')
except Exception:
    print 'please check the config file exist'
    exit(1)

fcoin = Fcoin()

print(fcoin.get_symbols())

print(fcoin.get_currencies())

fcoin.auth(key, secret)

print(fcoin.get_balance())