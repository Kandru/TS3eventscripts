from ts3tools import ts3tools
from ts3tools import TS3_DictDiffer
import time
# [TODO: thinking about deleting the TS3events core plugin and therefore add all events to the special core plugins (channel, clients, ...) (because of clientlist problem, go down)]

name = 'core.TS3events'
base = None
core_TS3clients = None

last_clientlist = None

def setup(ts3base):
    global base
    global core_TS3clients
    base = ts3base

    base.register_callback(name, 'ts3.start', process)
    base.register_callback(name, 'ts3.receivedevent', receivedevent)
    core_TS3clients = base.get_class('core.TS3clients')

def process(values):
    """
    Makes client list processes to execute callbacks which aren't bind to event notififies.
    It starts on plugin startup, so the callbacks only execute after the startup event.
    """
    global last_clientlist
    # [TODO: interval workarounds]
    while 1:
        # get actual clientlist
        new_clientlist = core_TS3clients.clientlist()
        if last_clientlist is not None:
            # let the class parse the changes (for this time, check only if the channel id of the client changes)
            checker = TS3_DictDiffer(new_clientlist, last_clientlist, 'cid')
            changed = checker.changed()
            if checker.changed() != set():
                # the channel id of someone have changed! execute the callbacks with the given users
                for user in changed:
                    # if the user isn't joined at this moment, we can execute it without fear
                    if user in last_clientlist.keys():
                        event_clientmoved(new_clientlist[user], last_clientlist[user]['cid'], new_clientlist[user]['cid'])
        # set the last query to the actual, because we finished the process now
        last_clientlist = new_clientlist
        time.sleep(0.5)

def receivedevent(data):
    event = ts3tools.parse_raw_event(data)

    if event["ev_type"] == 'notifycliententerview':
        event.pop("ev_type", None)
        event_clientjoined(event)
    elif event["ev_type"] == 'notifyclientleftview':
        event.pop("ev_type", None)
        event_clientleft(event)

def event_clientjoined(user):
    global base
    base.execute_callback('ts3.clientjoined', user)
    base.debprint('[Event] ts3.clientjoined -> Client entered the server!')

def event_clientmoved(user, old_cid, new_cid):
    global base
    # [TODO: maybe its better to let execute callbacks with more than one argument ;)]
    data = {}
    data['user'] = user
    data['old_cid'] = old_cid
    data['new_cid'] = new_cid
    base.execute_callback('ts3.clientmoved', data)
    base.debprint('[Event] ts3.clientmove -> Client entered other channel or was moved by someone!')

def event_clientleft(user):
    global base
    base.execute_callback('ts3.clientleft', user)
    base.debprint('[Event] ts3.clientleft -> Client left the server!')
