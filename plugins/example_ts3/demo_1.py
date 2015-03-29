from ts3tools import ts3tools
import time

# plugin name (must be unique!)
name = 'demo_1'

# initial method (called from ts3eventscripts)
def setup(ts3base, config):
    # get ts3base, it's needed for nearly everything
    global base
    base = ts3base

    # get chat helper
    global chathelper
    chathelper = base.get_class('ts3.ChatHelper')

    # register plugin functions as callbacks
    
    ## ts3.loop executes every half second
    base.register_callback(name, 'ts3.loop', loop)
    
    ## ts3.clientjoined executes if a client connects
    base.register_callback(name, 'ts3.clientjoined', event_clientjoined)
    
    ## ts3.chat.msg executes if a client writes a message to you
    base.register_callback(name, 'ts3.chat.msg', event_chat)
    
    ## ts3.chat.cmd.ping executes when a client writes "!ping" to the bot
    base.register_callback(name, 'ts3.chat.cmd.ping', cmd_ping)
    
    ## ts3.start executes on ts3eventscripts start
    base.register_callback(name, 'ts3.start', event_start)

def loop(values):
    # send debug message every half second which contains the time
    base.debprint(time.strftime("%H:%M:%S", time.gmtime()))

def event_start(values):
    # let the bot write "This is a test message!" every 5 seconds,
    # you can see that in console!

    ## sleep 5 seconds
    ## (yes, you can sleep without problems because of threading!)
    time.sleep(5)
       
    ## send a text message to server (send_sm means "send server message")
    ## note: this is sent through command socket
    chathelper.send_sm(base, ts3tools.escape_text('This is a test message!'))
    
    ## make it loop endless
    ## (yes, you can do that, too! the Thread is still alive!)
    event_start({})

def event_clientjoined(values):
    # sends a text message (especially a question) to every connecting user
    
    ## simplify some values
    id = values['clid']

    ## set the nickname to Pony to make it easier for the user
    ts3tools.set_nickname(base, 'Pony', True)
    
    ## send a message, in this case a question
    chathelper.send_pm(base, id, ts3tools.escape_text("What's my name?"), True)

def event_chat(values):
    # if the user answers right (in this case with a text message contains "Pony"), answer him that he is correct
    # if not, slap him with words!
    
    ## simplify some values
    id = values['invokerid']
    msg = values['msg']
    
    ## set the nickname to Pony
    ts3tools.set_nickname(base, 'Pony', True)
    
    ## answer to the user
    ## note: you have to use SOCKET_EVENT if you want to let someone chat with the bot because only SOCKET_EVENT is waiting for chat commands!
    if msg == "Pony":
        chathelper.send_pm(base, id, ts3tools.escape_text("Yes, that's right! You are the best!"), True)
    else:
        chathelper.send_pm(base, id, ts3tools.escape_text("I think you don't know me yet. Why I asked you..."), True)
    
def cmd_ping(values):
    # sends back a pong if someone sends command "!ping"
    
    ## simplify some values
    sender = values['sender'] # note: sender indices: id, uid, name
    args = values['args'] # type: sorted list

    ## set name to "HardcorePlayer"
    ts3tools.set_nickname(base, 'HardcorePlayer', True)
    ## send back a "pong"
    chathelper.send_pm(base, sender['id'], 'Pong! ;-)', True)
    