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
        """
        Creates a new instance of ts3base and initializes all neccessary parameters
        """
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
        self.identifier = config['id']
        self.package = 'ts3eventscripts' + self.identifier
        # init pluginbase
        self.pluginbase = PluginBase(package=self.package)
        # lock for command socket send & receive method
        self.sendlock = Lock()
        # init ts3 connection
        self.ts3_init()
        # load user plugins
        self.plugin_load()
        for plugin in self.pluginsource.list_plugins():
            self.debprint(plugin)
        # init all plugins
        self.plugin_init()

    def ts3_init(self):
        """
        Initialization of the ts3eventscript sockets for teamspeak3
        """
        # init ts3 query socket (command socket)
        self.command_socket = ts3socket(
            self.config['ip'],
            int(self.config['port']),
            int(self.config['sid']),
            self.config['user'],
            self.config['pass'])
        # debug message
        self.debprint('command socket initialized')

        # init event socket for event thread
        self.event_socket = ts3socket(
            self.config['ip'],
            int(self.config['port']),
            int(self.config['sid']),
            self.config['user'],
            self.config['pass'])
        # send register commands
        self.event_socket.send('servernotifyregister event=server')
        self.event_socket.send('servernotifyregister event=textprivate')
        self.event_socket.send('servernotifyregister event=textserver')
        # init event thread
        self.event_thread = Thread(target=self.event_process)
        self.event_thread.daemon = True
        self.event_thread.start()
        self.debprint('initialized event socket in thread')

    def plugin_load(self):
        """
        Load plugins specified from a user
        """
        paths = []
        for path in os.listdir(get_path('./plugins/')):
            paths.append('./plugins/' + path)
        self.pluginsource = self.pluginbase.make_plugin_source(
            # core plugins are loaded for any instance. Other plugins are handled later on
            searchpath=paths, identifier=self.identifier)

    def plugin_init(self):
        """
        Init plugins for this instance
        """
        self.debprint('loading plugins')
        plugins = self.config['plugins'].split(',')
        # load core plugins first
        for plugin_name in self.pluginsource.list_plugins():
            author = plugin_name.split('_', 1)[0]
            if author == 'core':
                plugin = self.pluginsource.load_plugin(plugin_name)
                plugin.setup(self) # pass ts3base instance to plugin
        # load user plugins next
        for plugin_name in self.pluginsource.list_plugins():
            if plugin_name in plugins:
                plugin = self.pluginsource.load_plugin(plugin_name)
                plugin.setup(self) # pass ts3base instance to plugin

    def event_process(self):
        """
        The event process is called in the event thread. It's the socket receiver.
        When received an event, execute a callback named "ts3.receivedevent" with raw event data
        """
        while 1:
            event = self.event_socket.receive()
            self.execute_callback('ts3.receivedevent', event)

    def get_event_socket(self):
        """
        Get the event socket
        """
        return self.event_socket

    def get_command_socket(self):
        """
        Get the command socket
        """
        return self.command_socket

    def send_receive(self, cmd):
        """
        Locks (so that other plugins must wait before doing something), sends the specified command and waits for answer message.
        Uses the command socket only!
        """
        with self.sendlock:
            self.command_socket.send(cmd)
            return self.command_socket.recv_all()

    def register_callback(self, plugin, key, function):
        """
        Register a new callback
        """
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
        """
        Execute all plugin callbacks from a specific type in a separate thread
        """
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
        self.classes[key] = plugin(self)
        self.debprint(
            'plugin ' +
            key +
            ' registered class ' +
            plugin.__name__)

    def debprint(self, msg):
        """
        Prints a debug message to the console
        """
        print(self.config['id'] + ' - ' + msg)

    def run(self):
        """
        Main class to keep ts3base.py running forever
        """
        try:
            # set nickname to instance id to identify itself (set some id's)
            ts3tools.set_nickname(self, self.config['id'])
            answer = ts3tools.parse_raw_answer(self.send_receive('clientfind pattern=' + self.config['id']))
            self.clid = answer['clid']
            # debug message
            self.debprint('The bot has the following client id: ' + self.clid)

            # set nickname
            ts3tools.set_nickname(self, self.config['name'])

            # execute start event
            self.execute_callback('ts3.start', {})

            while 1:
                # loop callback
                self.execute_callback('ts3.loop', {})
                # sleep a half second
                time.sleep(0.5)
        except MyException as e:
            print(str(e))
            exit()
