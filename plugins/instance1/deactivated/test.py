from ts3tools import ts3tools
import time

# plugin name (must be unique!)
name = 'test'
base = None

# initial method (called from ts3eventscripts)
def setup(ts3base):
    global base
    # get ts3base, it's needed for nearly everything
    base = ts3base

    # register plugin function as callback
    #base.register_callback(name, 'ts3.loop', test)


def test(values):
    global app2
    time.sleep(5)
    base.send_receive('sendtextmessage targetmode=2 target=1 msg=' + ts3tools.escape_text('This is a test message!'))
    base.execute_callback(name + '.test', {})
