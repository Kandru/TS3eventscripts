from ts3tools import ts3tools

name = 'core.TS3events'
base = None

def setup(ts3base):
    global base
    base = ts3base
    base.register_callback(name, 'ts3.receivedevent', receivedevent)

def receivedevent(data):
    event = parse_raw_event(data)

    if event["ev_type"] == 'notifycliententerview':
        event.pop("ev_type", None)
        event_clientjoined(event)
    elif event["ev_type"] == 'notifyclientleftview':
        event.pop("ev_type", None)
        event_clientleft(event)

def parse_raw_event(msg):
    splitted = msg.split(" ")
    
    new = {'ev_type': splitted[0]}
    # because in the new dict the event name already exists, we remove it from the splitted list
    splitted.pop(0)
    # parsing arguments
    for arg in splitted:
        one = arg.split('=', 1)
        if len(one) == 2:
            new[ts3tools.escape_text(one[0])] = ts3tools.escape_text(one[1])
        else:
            new[ts3tools.escape_text(one[0])] = None
    return new

def event_clientjoined(user):
   global base
   base.execute_callback('ts3.clientjoined', user)

def event_clientmove(user):
    pass

def event_clientleft(user):
    global base
    base.execute_callback('ts3.clientleft', user)
