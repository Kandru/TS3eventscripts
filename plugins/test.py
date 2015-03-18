from ts3tools import ts3tools
import time

# plugin name (must be unique!)
name = 'test'
socket = None
app2 = None

# pluginbase help: http://pluginbase.pocoo.org/

# setup - initial plugin load


def setup(app, ts3socket):
    # set socket
    global socket
    global app2
    app2 = app
    socket = ts3socket
    # register plugin function as callback
    app.register_callback(name, 'ts3.loop', test)


def test(values):
    # global app2
    # time.sleep(5)
    # socket.send('sendtextmessage targetmode=2 target=1 msg=' +
    #            ts3tools.escape_text('dies ist ein test'))
    # app2.execute_callback(name + '.test', {})
