from ts3tools import ts3tools

# plugin name (must be unique!)
name = 'test2'
base = None

# setup - initial plugin load
def setup(ts3base):
    global base
    base = ts3base

    # register plugin function as callback
    #base.register_callback(name, 'ts3.loop', test)


def test(values):
    global base
    base.send_receive('sendtextmessage targetmode=2 target=1 msg=' + ts3tools.escape_text('nope'))
    base.execute_callback(name + '.test', {})
