from ts3tools import ts3tools
import MySQLdb as mdb
import time

""" Changelog
-------------
4. kandru - added queue to prevend query errors - TODO: automatically reconnect on network failure
3. kandru - changed pymysql to mysqlclient
2. kandru - changed python cursor to dict cursor (to use column names instead of numbers that can change and break things easier)
1. j0nnib0y - initial commit
"""

name = 'core.TS3db'

base = None
config = None
queue = {}
result_queue = {}


def setup(ts3base):
    global base
    base = ts3base
    base.register_class(name, core_TS3db)
    db = base.get_class('core.TS3db')
    base.register_callback(name, 'ts3.loop', db.queue_worker)


class core_TS3db:
    # [TODO: better methods for a better life without sql commands]

    def __init__(self, ts3base):
        """
        Initializes a TS3db object.
        """
        self.base = ts3base
        self.config = ts3tools.get_global_config(name)
        # placeholders
        self.connection = None
        self.cursor = None
        if self.connect():
            self.base.debprint('[MySQL] Database connection established to host "' + self.config['MySQL']['host'] + '"!')

    def connect(self):
        """
        Internal method: Connects to a MySQL server and initializes the cursor.
        Do not use it because it's called at database core init automatically!
        """
        try:
            mdb.threadsafety = 1
            self.connection = mdb.connect(self.config['MySQL']['host'], self.config[
                                              'MySQL']['user'], self.config['MySQL']['pass'], self.config['MySQL']['db'])
        except mdb.Error as e:
            self.base.debprint("[MySQL] Error %d: %s" % (e.args[0], e.args[1]))
            self.connection = False
            return False
        if self.connection is not False:
            return True
    # database schema
    # note: there are no global database tables because therefore you can use config files ;)
    # [instance_name]                       -> instance config
    # [instance_name]_[plugin_name]         -> general plugin table
    # [instance_name]_[plugin_name]_table   -> more plugin tables

    def get_table_name(self, plugin_name, table_name=None):
        """
        Constructor for table names.
        Please note that the table with the returned table name needn't to be in the database!
        """
        if table_name is not None:
            return (self.base.config['id'] + '_' + plugin_name.replace('.', '-') + '_' + table_name).lower()
        else:
            return (self.base.config['id'] + '_' + plugin_name.replace('.', '-')).lower()

    def create_table(self, plugin_name, columns, table_name=None):
        """
        If not exists, creates a table with given name and columns.

        @plugin_name    name of plugin (unique name)
        @columns        list of columns, each column is a list with two elements: the column name and the column type (e.g. [['one', 'INT'], ['two', 'TEXT'], ['three', 'VARCHAR(42)']])
        @(table_name)   name of the "sub" table
        """
        columnstring = ' (`id` INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (`id`)'
        for column in columns:
            columnstring += ', `' + column[0] + '` ' + column[1]
        columnstring += ')'
        if table_name is not None:
            try:
                self.query('CREATE TABLE IF NOT EXISTS `' + self.get_table_name(plugin_name, table_name) + '`' + columnstring + ';', wait=False)
                return True
            except mdb.Error as e:
                self.base.debprint(
                    '[MySQL] Error %d: %s' % (e.args[0], e.args[1]))
                return False
        else:
            try:
                self.query('CREATE TABLE IF NOT EXISTS `' + self.get_table_name(plugin_name) + '`' + columnstring + ';', wait=False)
                return True
            except mdb.Error as e:
                self.base.debprint(
                    '[MySQL] Error %d: %s' % (e.args[0], e.args[1]))
                return False

    def execute(self, command, type='all'):
        """
        Manually executes commands.
        Note: If you don't know how to do, please use the pre-formatted query method!
        """
        try:
            self.cursor = self.connection.cursor(mdb.cursors.DictCursor)
            self.cursor.execute(command)
            self.connection.commit()
            if type is 'all':
                tmp = self.cursor.fetchall()
            else:
                tmp = self.cursor.fetchone()
            self.cursor.close()
            return tmp
        except mdb.Error as e:
            self.base.debprint('[MySQL] Error: %d: %s' %
                               (e.args[0], e.args[1]))
            self.cursor.close()
            return False

    def query(self, command, type='all', wait=True):
        """
        Adds a query to the queue and waits until its finished.
        Optional you do not need to wait until the query is finished
        """
        global queue, result_queue
        tmp_queue = queue
        qid = time.time()
        while qid in tmp_queue:
            qid = time.time()
        tmp_queue[qid] = {'sql': command, 'type': type, 'wait': wait}
        if wait is True:
            while qid not in result_queue:
                pass
            tmp = result_queue[qid]
            del result_queue[qid]
            return tmp
        else:
            return True

    def queue_worker(self, event):
        """
        execute all queued events
        """
        global queue, rqueue
        qids = queue.copy()
        for qid in qids:
            tmp = self.execute(queue[qid]['sql'], queue[qid]['type'])
            if queue[qid]['wait'] is True:
                result_queue[qid] = tmp
            del queue[qid]
        if len(qids.keys()) > 0:
            self.base.debprint('[MySQL] Info: %s queries finished' % len(qids.keys()))
