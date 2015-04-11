from ts3tools import ts3tools
from ts3tools import TS3_DictDiffer
import time
# [TODO: thinking about deleting the TS3events core plugin and therefore add all events to the special core plugins (channel, clients, ...) (because of clientlist problem, go down)]

name = 'core.TS3events'
base = None
core_TS3clients = None

checked_keys = ['cid', 'client_input_muted', 'client_away', 'client_output_muted', 'client_is_recording']
last_clientlist = None

def setup(ts3base):
    global base
    global core_TS3clients
    base = ts3base

    base.register_callback(name, 'ts3.start', process)
    base.register_callback(name, 'ts3.receivedevent', receivedevent)
    core_TS3clients = base.get_class('core.TS3clients')

    # config = ts3tools.get_

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
            for key in checked_keys:
                check = check_for_update(new_clientlist, last_clientlist, key)
                if check is not None:
                    for user in check:
                        # if the user isn't joined at this moment, we can execute it without fear
                        if user in last_clientlist.keys():
                            # execute event for each thing
                            if key == 'cid':
                                event_clientmoved(new_clientlist[user], last_clientlist[user]['cid'], new_clientlist[user]['cid'])
                            elif key == 'client_input_muted':
                                event_client_mutedmic(new_clientlist[user])
                            elif key == 'client_away':
                                event_client_away(new_clientlist[user])
                            elif key == 'client_output_muted':
                                event_client_mutedspeaker(new_clientlist[user])
                            elif key == 'client_is_recording':
                                event_client_recording(new_clientlist[user])
        # set the last query to the actual, because we finished the process now
        last_clientlist = new_clientlist
        time.sleep(0.5)

def check_for_update(new_dict, old_dict, subkey):
    checker = TS3_DictDiffer(new_dict, old_dict, subkey)
    changed = checker.changed()
    if changed != set():
        return changed
    else:
        return None


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
    base.execute_callback('ts3.client.join', user)
    # for those who don't use the new event/callback style
    base.execute_callback('ts3.clientjoined', user)
    base.debprint('[Event] ts3.clientjoined -> Client entered the server!')

def event_clientmoved(user, old_cid, new_cid):
    global base
    # [TODO: maybe its better to let execute callbacks with more than one argument ;)]
    data = {}
    data['user'] = user
    data['old_cid'] = old_cid
    data['new_cid'] = new_cid
    base.execute_callback('ts3.client.move', data)
    # for those who don't use the new event/callback style
    base.execute_callback('ts3.clientmoved', data)
    base.debprint('[Event] ts3.clientmove -> Client entered other channel or was moved by someone!')

def event_clientleft(user):
    global base
    base.execute_callback('ts3.client.leave', user)
    # for those who don't use the new event/callback style
    base.execute_callback('ts3.clientleft', user)
    base.debprint('[Event] ts3.clientleft -> Client left the server!')

def event_client_mutedmic(user):
    if user['client_input_muted'] == '1':
        base.execute_callback('ts3.client.mutedmic', user)
        base.debprint('[Event] ts3.client.mutedmic -> Client muted his microphone!')
    else:
        base.execute_callback('ts3.client.unmutedmic', user)
        base.debprint('[Event] ts3.client.unmutedmic -> Client un-muted his microphone!')

def event_client_away(user):
    if user['client_away'] == '1':
        base.execute_callback('ts3.client.away', user)
        base.debprint('[Event] ts3.client.away -> Client is now away!')
    else:
        base.execute_callback('ts3.client.notaway', user)
        base.debprint('[Event] ts3.client.notaway -> Client isn\'t away now!')

def event_client_mutedspeaker(user):
    if user['client_output_muted'] == '1':
        base.execute_callback('ts3.client.mutedspeaker', user)
        base.debprint('[Event] ts3.client.mutedspeaker -> Client muted his speaker!')
    else:
        base.execute_callback('ts3.client.unmutedspeaker', user)
        base.debprint('[Event] ts3.client.unmutedspeaker -> Client un-muted his speaker!')

def event_client_recording(user):
    if user['client_is_recording'] == '1':
        base.execute_callback('ts3.client.startedrecording', user)
        base.debprint('[Event] ts3.client.startedrecording -> Client started recording!')
    else:
        base.execute_callback('ts3.client.stoppedrecording', user)
        base.debprint('[Event] ts3.client.stoppedrecording -> Client stopped recording!')
