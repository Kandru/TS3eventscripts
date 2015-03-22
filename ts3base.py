import os
import threading
import time
from functools import partial
from collections import defaultdict
from pluginbase import PluginBase
from ts3socket import ts3socket
from ts3tools import ts3tools
from myexception import MyException
from threading import Thread

# For easier usage calculate the path relative to here.
here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)


class ts3base(threading.Thread):

    def __init__(self, config):
        # init threading
        threading.Thread.__init__(self)
        
        # set config for whole class
        self.config = config
        
        # debug message
        self.debprint('instance initialized')
        
        # init callbacks
        self.callbacks = defaultdict(dict)
        
        # identifier + package name for pluginbase
        identifier = config['id']
        package = 'ts3eventscripts' + identifier
        
        # init pluginbase
        self.pluginbase = PluginBase(package=package)
        # init pluginsource
        self.pluginsource = self.pluginbase.make_plugin_source(
            # two plugin directories: global plugins in plugins/, instance only plugins in directory named with the instance name
            searchpath=[get_path('./plugins/' + self.config['id']), get_path('./plugins')], identifier=identifier)
        
        # init ts3 connection
        self.ts3_init()
        # init all plugins
        self.plugin_init()

    def ts3_init(self):
        # init ts3 query socket
        self.ts3socket = ts3socket(
            self.config['ip'],
            self.config['port'],
            self.config['sid'],
            self.config['user'],
            self.config['pass'])
        # debug message
        self.debprint('socket initialized')

    def plugin_init(self):
        # debug message
        self.debprint('loading plugins')
        for plugin_name in self.pluginsource.list_plugins():
            plugin = self.pluginsource.load_plugin(plugin_name)
            plugin.setup(self, self.ts3socket)

    def register_callback(self, plugin, key, function):
        self.callbacks[key][plugin + '_' + function.__name__] = function
        # debug message
        self.debprint(
            'plugin ' +
            plugin +
            ' -> (func)' +
            function.__name__ +
            ' -> (callback)' +
            key)

    def execute_callback(self, key, values):
        if key in self.callbacks:
            for index, func in self.callbacks[key].items():
                t = Thread(target=func, args=(values,))
                t.start()

    def debprint(self, msg):
        print(self.config['id'] + ' - ' + msg)

    def run(self):
        try:
            # set nickname
            ts3tools.set_nickname(self.ts3socket, self.config['name'])
            while 1:
                # loop callback
                self.execute_callback('ts3.loop', {})
                # sleep a half second
                time.sleep(0.5)
        except MyException as e:
            print(str(e))
            exit()
