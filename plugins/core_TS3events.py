from ts3tools import ts3tools

name = 'core.TS3events'
base = None

def setup(ts3base, config):
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

def event_clientmove(user):
    pass

def event_clientleft(user):
    global base
    base.execute_callback('ts3.clientleft', user)
