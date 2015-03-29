from ts3tools import ts3tools

"""
core.TS3chat

Provides basic text chat events and therefore, it implements a command handler.
The command handler executes a command event if a chat message has a prefix (default is "!") defined in the chat configuration.
Command events are pre-formatted for other plugins with arguments etc.
"""

name = 'core.TS3chat'
base = None
command_socket = None
event_socket = None

# [TODO: config outsourcing in file]
config = {}
config['command_prefix'] = '!'

def setup(ts3base):
    global base
    global command_socket
    global event_socket
    global chathelper

    base = ts3base
    command_socket = base.get_command_socket()
    event_socket = base.get_event_socket()
    chathelper = ChatHelper()

    base.register_class('ts3.ChatHelper', ChatHelper)

    base.register_callback(name, 'ts3.receivedevent', event_receivedevent)
    base.register_callback(name, 'ts3.clientjoined', event_clientjoined)

def event_receivedevent(data):
    event = ts3tools.parse_raw_event(data)

    if (event["ev_type"] == 'notifytextmessage') and (event['invokerid'] != base.clid):
        if event["targetmode"] == '1':
            event.pop("ev_type", None)
            # event --> chat_msg --> chat_cmd
            chat_msg(event)

def chat_msg(event):
    if event['msg'].startswith(config['command_prefix']):
        chat_cmd(event)
    else:
        base.execute_callback('ts3.chat.msg', event)

def chat_cmd(event):
    cmd = {}
    cmd['sender'] = {   'id': event['invokerid'],
                        'uid': event['invokeruid'],
                        'name': event['invokername']}
    cmd['args'] = event['msg'].split(' ')
    cmd['command'] = cmd['args'][0]
    cmd['args'].pop(0)
    
    # delete first character (command_prefix)
    base.execute_callback('ts3.chat.cmd.' + cmd['command'][1:], cmd)
    # debug message
    base.debprint('core_TS3chat: received chat command ' + cmd['command'] + ' from ' + cmd['sender']['name'] + ' with args ' + str(cmd['args']))

def event_clientjoined(user):
    # [TODO: real welcome message]
    chathelper.send_pm(base, user["clid"], "Welcome to the Teamspeak server! Type in a command if you want.", True)

class ChatHelper:
    def __init__(self):
        pass

    def send_pm(self, base, user, msg, socket=False):
        if socket == False:
            return base.send_receive(
               'sendtextmessage targetmode=1 msg=' + msg + ' target=' + user)
        else:
            return base.get_event_socket().send(
                'sendtextmessage targetmode=1 msg=' + msg + ' target=' + user)