from fcoin import Fcoin
import sys
import os
import socket
import ConfigParser
import threading
import Queue
import pickle

OP_BUY = 1
OP_SELL = -1
OP_NONE = 0

cf = ConfigParser.ConfigParser()
try:
    cf.read("fcoin.conf")
    key = cf.get('api', 'key')
    secret = cf.get('api', 'secret')
    symbol = cf.get('brush', 'symbol')
    currency = cf.get('brush', 'currency')
    addr = cf.get('peer', 'addr')
    server_port = cf.get('peer', 'server_port')
    peer_port = cf.get('peer', 'peer_port')
    actor = cf.get('peer', 'actor')
except Exception:
    print('please check the config file <fcoin.conf> in parent direction')
    exit(1)

fcoin = Fcoin()
fcoin.auth(key, secret)
symbols = fcoin.get_symbols()
send_queue = Queue.Queue(maxsize=1)
recv_queue = Queue.Queue(maxsize=1)
udp_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((addr, int(server_port)))
serial = 0

class Sender(threading.Thread):
    def run(self):
        while True:
            data_obj = send_queue.get()
            data = pickle.dumps(data_obj)
            udp_socket.sendto(data.encode('utf-8'), (ip, peer_port))
            print('send data=%s to address=%s' %(str(data_obj), ip))


class Receiver(threading.Thread):
    def run(self):
        while True:
            data, remote_address = udp_socket.recvfrom(4096)
            data_obj = pickle.loads(data.decode('utf-8'))
            print('recv data=%s, from address=%s' %(str(data_obj), remote_address))
            recv_queue.put(data_obj)


class Leader(threading.Thread):
    def run(self):
        while True:
            balances = fcoin.get_balance()
            datas = balances['data']
            base_amount, quote_amount = get_amount(symbol, datas)
            print ('amount = (%s, %s)' % (base_amount, quote_amount))
            if not base_amount and quote_amount:
                sleep(1)
                continue
            data.base_amount = base_amount
            data.quote_amount = quote_amount
            data.symbol = symbol
            data.serial = ++serial

            send_queue.put(data)
            while True:
                recv_data = recv_queue.get()
                if serial > recv_data.serial:
                    continue
                if serial < recv_data.serial:
                    break
                scalping(recv_data.operate, symbol, recv_data.price, recv_data.lots)
                break


class Follower(threading.Thread):
    def run(self):
        while True:
            recv_data = recv_queue.get()
            symbol = recv_data.symbol
            base_amount = data.base_amount
            quote_amount = data.quote_amount
            serial = recv_data.serial

            balances = fcoin.get_balance()
            datas = balances['data']
            cur_base_amount, cur_quote_amount = get_amount(symbol, datas)
            price = get_price(symbol)
            operate, lots = get_lots(price, base_amount, quote_amount, cur_base_amount, cur_quote_amount)

            send_data.operate = operate
            send_data.price = price
            send_data.lots = lots
            send_data.serial = serial

            send_queue.put(send_data)
            scalping(operate, price, lots)


def get_lots(price, base_amount, quote_amount, cur_base_amount, cur_quote_amount):
    lots = 0
    operate = OP_NONE
    if cur_base_amount >= base_amount:
        sell_lots = cur_base_amount
        if sell_lots < quote_amount * price:
            sell_lots = quote_amount * price

    if cur_quote_amount >= quote_amount:
        buy_lots = cur_quote_amount
        if buy_lots < cur_base_amount:
            buy_lots = cur_base_amount

    if sell_lots >= buy_lots and sell_lots:
        operate = OP_SELL
        lots = sell_lots

    if buy_lots >= sell_lots and buy_lots:
        operate = OP_BUY
        lots = buy_lots

    return operate, lots


def get_amount(symbol, datas):
    find = False
    base_amount, quote_amount = 0, 0
    for symbol_info in symbols:
        if symbol == symbol_info['name']:
            base_currency = symbol_info['base_currency']
            quote_currency = symbol_info['quote_currency']
            find = True

    if find:
        for data in datas:
            currency = data['currency']
            if base_currency == currency:
                base_amount = data['available']
            elif quote_currency == currency:
                quote_amount = data['available']

    return base_amount, quote_amount


def get_price(cur_symbol):
    tick = fcoin.get_market_ticker(cur_symbol)
    ticker = tick['data']['ticker']
    max_buy = ticker[2]
    min_sell = ticker[4]

    return (max_buy + min_sell) / 2


def main():
    sender = Sender()
    receiver = Receiver()
    sender.start()
    receiver.start()

    if 'leader' == actor:
        leader = Leader()
        leader.start()
    else:
        follower = Follower()
        follower.start()


if __name__ == "__main__":
    main()
