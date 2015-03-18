#!/usr/bin/env python3
import time
import configparser
from ts3base import ts3base
from myexception import MyException

config = configparser.ConfigParser()
config.read('config.ini')

for key in config:
    if key.startswith('instance'):
        ts3 = ts3base({'id': config[key]['id'],
                       'ip': config[key]['ip'],
                       'port': int(config[key]['port']),
                       'sid': int(config[key]['sid']),
                       'user': config[key]['user'],
                       'pass': config[key]['pass'],
                       'name': config[key]['name'], })
        ts3.start()

try:
    while 1:
        # endless loop
        time.sleep(1)
except KeyboardInterrupt as e:
    print('exit...')
    exit()
except MyException as e:
    print(str(e))
    exit()
