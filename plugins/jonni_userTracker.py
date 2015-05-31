"""
Plugin: jonni.userTracker
Tracks users in a MySQL database defined in the core.TS3db config.
Later there are some more tracked things like last visit, amount of time being on the server, ...
"""

import time

""" Changelog
-------------
2. kandru
- fixed UPDATE statements. Should now only update one user, not all
- fixed "answer_" variables. We should now use column names
- added "ts3.clientleft"
- added function "create_client"
- added timestamp and columns "ts_lastonline", "ts_lastchange", "ts_insert"
- added column "total_online" to measure total online time in seconds
- added ts3 instance information
- fixed typos
1. j0nnib0y - initial commit
"""



name = 'jonni.userTracker'

base = None
db = None


def setup(ts3base):
    global base
    base = ts3base

    base.register_callback(name, 'ts3.start', startup)
    base.register_callback(name, 'ts3.clientjoined', event_clientjoined)
    base.register_callback(name, 'ts3.clientleft', event_clientleft)
    base.register_class(name, UserTracker)


def startup(bla):
    global db
    db = base.get_class('core.TS3db')

    db.create_table(
        name, [['instance', 'VARCHAR(255)'], ['uid', 'VARCHAR(30)'], ['dbid', 'INT'], ['clid', 'INT'], ['last_name', 'TEXT'], ['total_online', 'INT'], ['ts_lastonline', 'INT'], ['ts_lastchange', 'INT'], ['ts_insert', 'INT']], 'users')

def event_clientjoined(values):
    uid = values['client_unique_identifier']
    last_name = values['client_nickname']
    dbid = values['client_database_id']
    clid = values['clid']
    timestamp = str(time.time())
    row = db.query('SELECT * FROM `' + db.get_table_name(name, 'users') + '` WHERE `uid` = "' + uid + '" AND `instance` = "' + base.identifier + '";', 'one')
    if row:
        if row is None:
            create_client(values)
        else:
            # set lastonline timestamp to now
            db.query('UPDATE `' + db.get_table_name(name, 'users') + '` SET ts_lastonline = "' + timestamp + '", ts_lastchange = "' + timestamp + '" WHERE `uid` = "' + uid + '" AND `instance` = "' + base.identifier + '";', wait=False)
            # if something has changed since last connect
            if row['dbid'] != dbid:
                db.query('UPDATE `' + db.get_table_name(name, 'users') + '` SET dbid = "' + dbid + '", ts_lastchange = "' + timestamp + '" WHERE `uid` = "' + uid + '" AND `instance` = "' + base.identifier + '";', wait=False)
            if row['last_name'] != last_name:
                db.query('UPDATE `' + db.get_table_name(name, 'users') + '` SET last_name = "' + last_name + '", ts_lastchange = "' + timestamp + '" WHERE `uid` = "' + uid + '" AND `instance` = "' + base.identifier + '";', wait=False)
            if row['clid'] != clid:
                db.query('UPDATE `' + db.get_table_name(name, 'users') + '` SET clid = "' + clid + '", ts_lastchange = "' + timestamp + '" WHERE `uid` = "' + uid + '" AND `instance` = "' + base.identifier + '";', wait=False)
    # [TODO: more details, statistics, ...]

def event_clientleft(values):
    clid = values['clid']
    timestamp = str(time.time())
    # set new online time after user has left the server
    row = db.query('SELECT * FROM `' + db.get_table_name(name, 'users') + '` WHERE `clid` = "' + clid + '" AND `instance` = "' + base.identifier + '";', 'one')
    if row:
        if row is not None:
            db.query('UPDATE `' + db.get_table_name(name, 'users') + '` SET total_online = total_online + "' + str(round(float(timestamp) - float(row['ts_lastonline']))) + '", ts_lastchange = "' + timestamp + '", clid = "' + clid + '" WHERE `clid` = "' + clid + '" AND `instance` = "' + base.identifier + '";', wait=False)

def create_client(values):
    uid = values['client_unique_identifier']
    last_name = values['client_nickname']
    dbid = values['client_database_id']
    clid = values['clid']
    timestamp = str(time.time())
    db.query('INSERT INTO `' + db.get_table_name(name, 'users') + '` (`instance`, `uid`, `dbid`, `clid`, `last_name`,`total_online`,`ts_lastonline`,`ts_lastchange`,`ts_insert`) VALUES ("' + base.identifier + '", "' + uid + '", "' + dbid + '", "' + clid + '", "' + last_name + '", "0", "' + timestamp + '", "' + timestamp + '", "' + timestamp + '");', wait=False)

class UserTracker:

    def __init__(self, ts3base):
        pass
