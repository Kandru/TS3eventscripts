from ts3tools import ts3tools

name = 'core.TS3events'
base = None

def setup(ts3base):
    global base
    base = ts3base
    base.register_callback(name, 'ts3.receivedevent', receivedevent)

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

def event_clientmove(user):
    base.debprint('[Event] ts3.clientmove -> Client entered other channel or was moved by someone!')

def event_clientleft(user):
    global base
    base.execute_callback('ts3.clientleft', user)
    base.debprint('[Event] ts3.clientleft -> Client left the server!')
