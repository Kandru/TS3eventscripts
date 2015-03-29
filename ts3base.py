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
from threading import Lock

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
        # list of all classes (instances, objects, however)
        self.classes = {}

        # identifier + package name for pluginbase
        identifier = config['id']
        package = 'ts3eventscripts' + identifier

        # init pluginbase
        self.pluginbase = PluginBase(package=package)
        # init pluginsource
        self.pluginsource = self.pluginbase.make_plugin_source(
            # two plugin directories: global plugins in plugins/, instance only plugins in directory named with the instance name
            searchpath=[get_path('./plugins/' + self.config['id']), get_path('./plugins')], identifier=identifier)

        # lock for command socket send & receive method
        self.sendlock = Lock()

        # init ts3 connection
        self.ts3_init()
        # init all plugins
        self.plugin_init()

    def ts3_init(self):
        # init ts3 query socket (command socket)
        self.command_socket = ts3socket(
            self.config['ip'],
            self.config['port'],
            self.config['sid'],
            self.config['user'],
            self.config['pass'])
        # debug message
        self.debprint('command socket initialized')

        # init event socket for event thread
        self.event_socket = ts3socket(
            self.config['ip'],
            self.config['port'],
            self.config['sid'],
            self.config['user'],
            self.config['pass'])
        # send register commands
        self.event_socket.send('servernotifyregister event=server')
        # init event thread
        self.event_thread = Thread(target=self.event_process)
        self.event_thread.daemon = True
        self.event_thread.start()
        self.debprint('initialized event socket in thread')

    def plugin_init(self):
        # debug message
        self.debprint('loading plugins')
        for plugin_name in self.pluginsource.list_plugins():
            plugin = self.pluginsource.load_plugin(plugin_name)
            plugin.setup(self) # for advanced usage, add a socket as passed variable

    def event_process(self):
        """
        The event process is called in the event thread. It's the socket receiver.
        When received an event, execute a callback named "ts3.receivedevent" with raw event data
        """
        while 1:
            event = self.event_socket.receive()
            self.execute_callback('ts3.receivedevent', event)

    def get_event_socket(self):
        return self.event_socket

    def get_command_socket(self):
        return self.command_socket

    def send_receive(self, cmd):
        """
        Locks (so that other plugins must wait before doing something), sends the specified command and waits for answer message.
        Uses the command socket only!
        """
        with self.sendlock:
            self.command_socket.send(cmd)
            return self.command_socket.receive()

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
                t.daemon = True
                t.start()

    def get_class(self, pluginname):
        """
        If avaiable, returns a dictionary with name of the plugin (index is "plugin")
        and the function used to call the given method (index is "function").
        """
        if pluginname in self.classes.keys():
            return self.classes[pluginname]
        else:
            return None

    def get_class_list(self):
        """
        Returns a list (names only) with all classes registered here.
        The names can be used to get the class with get_class()
        """
        return self.classes.keys()

    def register_class(self, key, plugin):
        """
        Registers a class which can be used from plugins.
        -> classes can be used from plugins to communicate with each other
        """
        self.classes[key] = plugin()
        self.debprint(
            'plugin ' +
            key +
            ' registered class ' +
            plugin.__name__)

    def debprint(self, msg):
        print(self.config['id'] + ' - ' + msg)

    def run(self):
        try:
            # get clid from bot so we can identify him later
            ts3tools.set_nickname(self.command_socket, self.config['id'])
            # later, clientfind comes from core_TS3clients
            answer = ts3tools.parse_raw_answer(self.send_receive('clientfind pattern=' + self.config['id']))
            self.clid = answer['clid']
            # debug message
            self.debprint('The bot has the following client id: ' + self.clid)

            # set nickname
            ts3tools.set_nickname(self.command_socket, self.config['name'])
            while 1:
                # loop callback
                self.execute_callback('ts3.loop', {})
                # sleep a half second
                time.sleep(0.5)
        except MyException as e:
            print(str(e))
            exit()
