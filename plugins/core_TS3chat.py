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
config = None
chathelper = None

command_help = {}

def setup(ts3base):
    global base
    global command_socket
    global event_socket
    global chathelper
    global config
    base = ts3base
    command_socket = base.get_command_socket()
    event_socket = base.get_event_socket()
    config = ts3tools.get_global_config(name)
    chathelper = ChatHelper(base)
    base.register_class(name, ChatHelper)
    base.register_callback(name, 'ts3.start', event_start)
    base.register_callback(name, 'ts3.receivedevent', event_receivedevent)
    base.register_callback(name, 'ts3.clientjoined', event_clientjoined)

def event_start(event):
    if config['Welcome']['force_user'] != 'false':
        ts3tools.set_nickname(base, config['Welcome']['force_user'], True)

def event_receivedevent(data):
    event = ts3tools.parse_raw_event(data)

    if (event["ev_type"] == 'notifytextmessage') and (event['invokerid'] != base.clid):
        if event["targetmode"] == '1':
            event.pop("ev_type", None)
            # event --> chat_msg --> chat_cmd
            chat_msg(event)

def chat_msg(event):
    if event['msg'].startswith(config['General']['command_prefix']):
        chat_cmd(event)
    else:
        base.execute_callback('ts3.chat.msg', event)

def chat_cmd(event):
    cmd = {}
    # index id for old plugins, please let it there
    cmd['sender'] = {'id': event['invokerid'], 'clid': event['invokerid'], 'uid': event['invokeruid'], 'name': event['invokername']}
    cmd['args'] = event['msg'].split(' ')
    cmd['command'] = cmd['args'][0]
    cmd['args'].pop(0)

    if cmd['command'] != config['General']['command_prefix'] + 'help':
        # delete first character (command_prefix)
        base.execute_callback('ts3.chat.cmd.' + cmd['command'][1:], cmd)
    else:
        chat_help(cmd)
    # debug message
    base.debprint('core_TS3chat: received chat command ' + cmd['command'] + ' from ' + cmd['sender']['name'] + ' with args ' + str(cmd['args']))

def chat_help(event):
    clid = event['sender']['clid']
    if event['args'] == []:
        count = len(command_help)
        message = '\\n[b]Help - Command list - (' + str(count) + '):[/b]\\nType in [color=blue]' + config['General']['command_prefix'] + 'help [command][/color] for more information about a command.\\n-----------------------------------------------------------------------------------------------------------\\n \\n'
        if count != 0:
            for command, values in command_help.items():
                whitespaces = 20-(2+len(command))
                message += '    [color=blue]' + config['General']['command_prefix'] + command + '[/color]' + (whitespaces * ' ') + '- ' + values['title'] + '\\n'
        else:
            message += 'No commands here yet. :-(\\n'
    else:
        command = ''.join(event['args'])
        if command in command_help:
            print(command_help[command])
            message = '[b]' + config['General']['command_prefix'] + command + '[/b]: ' + command_help[command]['desc']
        else:
            message = 'Sorry, command not found :-(\\n'
    chathelper.send_pm(base, clid, message, socket=True)

def event_clientjoined(user):
    # send welcome message, if enabled
    if config['Welcome']['enabled'] == 'true':
        chathelper.send_pm(base, user["clid"], ts3tools.escape_text(config['Welcome']['message']), True)

class ChatHelper:
    def __init__(self, ts3base):
        self.base = ts3base

    def add_command_help(self, command, title, desc):
        command_help[command] = {'title': title, 'desc': desc}

    def send_pm(self, base, clid, msg, socket=False):
        """
        Sends a private message to given user.
        """
        if socket is False:
            return base.send_receive(
               'sendtextmessage targetmode=1 msg=' + ts3tools.escape_text(msg) + ' target=' + clid)
        else:
            return base.get_event_socket().send(
                'sendtextmessage targetmode=1 msg=' + ts3tools.escape_text(msg) + ' target=' + clid)

    def send_sm(self, base, msg, socket=False):
        """
        Sends a server message (all users can see it in the server tab).
        """
        if socket is False:
            return base.send_receive('sendtextmessage targetmode=3 msg=' + ts3tools.escape_text(msg))
        else:
            return base.get_event_socket().send('sendtextmessage targetmode=3 msg=' + ts3tools.escape_text(msg))
