#!/usr/bin/env python3
import time
import configparser
from ts3base import ts3base
from ts3http import ts3http
from threading import Thread
from myexception import MyException

config = configparser.ConfigParser()
config.read('config.ini')
instances = {}

# start ts3 instances
for key in config:
    if key != 'DEFAULT':
        config[key]['id'] = key
        instances[key] = ts3base(config[key])
        instances[key].daemon = True
        instances[key].start()
# start webinterface
t = Thread(target=ts3http, args=(instances))
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
