from ts3tools import ts3tools

name = 'jonni.userTracker'

base = None
db = None


def setup(ts3base):
    global base
    base = ts3base

    base.register_callback(name, 'ts3.start', startup)
    base.register_callback(name, 'ts3.clientjoined', event_clientjoined)
    base.register_class(name, UserTracker)


def startup(bla):
    global db
    db = base.get_class('core.TS3db')

    db.create_table(
        name, [['uid', 'VARCHAR(30)'], ['dbid', 'INT'], ['last_name', 'TEXT']], 'users')


def event_clientjoined(values):
    uid = values['client_unique_identifier']
    last_name = values['client_nickname']
    dbid_raw = base.send_receive('clientgetdbidfromuid cluid=' + uid)
    dbid_parsed = ts3tools.parse_raw_answer(dbid_raw)
    dbid = dbid_parsed['cldbid']

    if db.execute('SELECT * FROM `' + db.get_table_name(name, 'users') + '` WHERE `uid` = "' + uid + '";'):
        answer = db.fetch_one()
        if answer is None:
            db.execute('INSERT INTO `' + db.get_table_name(name, 'users') + '` (`uid`, `dbid`, `last_name`) VALUES ("' + uid + '", ' + dbid + ', "' + last_name + '");')
            db.fetch_one()
        else:
            answer_dbid = answer[2]
            answer_name = answer[3]
            if answer_dbid != dbid:
                db.execute('UPDATE `' + db.get_table_name(name, 'users') + '` SET dbid = "' + dbid + '";')
                db.fetch_one()
            if answer_name != last_name:
                db.execute('UPDATE `' + db.get_table_name(name, 'users') + '` SET last_name = "' + last_name + '";')
                db.fetch_one()

def event_clientleft():
    pass

class UserTracker:

    def __init__(self, ts3base):
        pass
