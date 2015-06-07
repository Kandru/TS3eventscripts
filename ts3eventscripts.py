#!/usr/bin/env python3
import time
import configparser
from ts3base import ts3base
from ts3http import ts3http
from threading import Thread
from myexception import MyException

config = configparser.ConfigParser()
config.read('config.ini')

# start ts3 instances
for key in config:
    if key.startswith('instance'):
        ts3 = ts3base(config[key])
        ts3.daemon = True
        ts3.start()
# start webinterface
t = Thread(target=ts3http, args=())
t.daemon = True
t.start()

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
