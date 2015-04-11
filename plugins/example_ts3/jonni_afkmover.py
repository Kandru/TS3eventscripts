from ts3tools import ts3tools

"""
jonni.afkMover
This plugin moves clients on special events like getting away or muting the speaker or microphone.
It's fully configurable via config file.
"""

name = 'jonni.afkmover'

base = None
config = None
core_TS3clients = None
core_TS3chat = None

afk_users = {}
move_status = []

def setup(ts3base):
    global base
    global config
    global core_TS3clients
    global core_TS3chat

    base = ts3base
    base.register_callback(name, 'ts3.client.away', event_away)
    base.register_callback(name, 'ts3.client.notaway', event_notaway)
    base.register_callback(name, 'ts3.client.mutedmic', event_mutedmic)
    base.register_callback(name, 'ts3.client.unmutedmic', event_unmutedmic)
    base.register_callback(name, 'ts3.client.mutedspeaker', event_mutedspeaker)
    base.register_callback(name, 'ts3.client.unmutedspeaker', event_unmutedspeaker)
    base.register_callback(name, 'ts3.client.move', event_client_move)
    base.register_callback(name, 'ts3.client.leave', event_client_leave)
    base.register_callback(name, 'ts3.chat.cmd.afk', chat_afk)

    core_TS3clients = base.get_class('core.TS3clients')
    core_TS3chat = base.get_class('core.TS3chat')

    config = ts3tools.get_instance_config(base, 'jonni.afkmover')
    if config is None:
        config = ts3tools.get_global_config('jonni.afkmover')

def afk(event, user):
    # only do something when the user isn't afk already
    clid = user['clid']
    cid = user['cid']
    if user['clid'] not in afk_users.keys():
        afk_users[clid] = {'old_channel': cid, 'matters': [event]}
        if event == 'away':
            move(user, config['AwayMove']['channel_id'])
        elif event == 'mutedmic':
            move(user, config['MicMuteMove']['channel_id'])
        elif event == 'mutedspeaker':
            move(user, config['SpeakerMuteMove']['channel_id'])
        elif event == 'command':
            move(user, config['CommandMove']['channel_id'])
        base.debprint('[jonni.afkMover] User ' + user['client_nickname'] + ' is now afk! He will be moved now.')
    else:
        if event not in afk_users[clid]['matters']:
            afk_users[clid]['matters'].append(event)

def unafk(event, user):
    # only do something when the user is afk
    if user['clid'] in afk_users.keys():
        clid = user['clid']
        # if the event matches the event the user is afk
        if event in afk_users[clid]['matters'] and len(afk_users[clid]['matters']) == 1:
            # delete the user from afk cache and move him
            if config['General']['moveback'] == 'true':
                move(user, afk_users[clid]['old_channel'])
            del afk_users[clid]
            base.debprint('[jonni.afkMover] User ' + user['client_nickname'] + ' isn\'t afk anymore!')
            return True
        elif event == 'all':
            del afk_users[clid]
            base.debprint('[jonni.afkMover] User ' + user['client_nickname'] + ' isn\'t afk anymore! (all)')
            # no move here, because the user want to be in the channel he went
        else:
            afk_users[clid]['matters'].remove(event)

def move(user, new_cid):
    # if the user is already in channel, we don't need to move him
    if user['cid'] != new_cid:
        move_status.append(user['clid'])
        core_TS3clients.clientmove(user['clid'], new_cid)

def event_away(user):
    if config['AwayMove']['enabled'] == 'true':
        afk('away', user)

def event_notaway(user):
    if config['AwayMove']['enabled'] == 'true':
        unafk('away', user)

def event_mutedmic(user):
    if config['MicMuteMove']['enabled'] == 'true':
        afk('mutedmic', user)

def event_unmutedmic(user):
    if config['MicMuteMove']['enabled'] == 'true':
        unafk('mutedmic', user)

def event_mutedspeaker(user):
    if config['SpeakerMuteMove']['enabled'] == 'true':
        afk('mutedspeaker', user)

def event_unmutedspeaker(user):
    if config['SpeakerMuteMove']['enabled'] == 'true':
        unafk('mutedspeaker', user)

def event_client_move(event):
    global move_status
    # this is a little fix for the problem that the plugin moves someone and then this someone get unafk
    if event['user']['clid'] in move_status:
        move_status.remove(event['user']['clid'])
    # if the user moves to another channel, maybe he is not afk?
    else:
        if config['General']['move_unafk'] == 'true':
            unafk('all', event['user'])

def event_client_leave(user):
    clid = user['clid']
    if clid in afk_users.keys():
        del afk_users[clid]

def chat_afk(event):
    global user_cache
    clid = event['sender']['clid']
    if clid not in afk_users.keys():
        user = core_TS3clients.clientinfo(event['sender']['clid'])
        user['clid'] = event['sender']['clid']
        afk('command', user)
        if config['General']['moveback'] == 'true':
            if config['General']['name'] != 'false':
                ts3tools.set_nickname(base, config['General']['name'], True)
            core_TS3chat.send_pm(base, clid, 'You\'re now AFK! Please type in [color=blue]!afk[/color] to come back! If so, you will be moved to your old channel automatically! ;-)', True)
        else:
            if config['General']['name'] != 'false':
                ts3tools.set_nickname(base, config['General']['name'], True)
            core_TS3chat.send_pm(base, clid, 'You\'re now AFK! Please type in [color=blue]!afk[/color] to come back!', True)
    else:
        user = core_TS3clients.clientinfo(event['sender']['clid'])
        user['clid'] = event['sender']['clid']
        unafk('command', user)
        if config['General']['moveback'] == 'true':
            if config['General']['name'] != 'false':
                ts3tools.set_nickname(base, config['General']['name'], True)
            core_TS3chat.send_pm(base, clid, 'You\'re now BACK! The server will move you back now! :-)', True)
        else:
            if config['General']['name'] != 'false':
                ts3tools.set_nickname(base, config['General']['name'], True)
            core_TS3chat.send_pm(base, clid, 'You\'re now BACK!', True)

class AfkMover_API:
    def __init__(self):
        pass
