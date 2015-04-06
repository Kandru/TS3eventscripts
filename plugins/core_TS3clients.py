from ts3tools import ts3tools
import time

name = 'core.TS3clients'
base = None

# get a centralized clientlist to avoid spamming server commands for clientlists every second
nextClientlistInterval = 2
nextClientlist = 0
clientlist = {}

def setup(ts3base):
    global base
    base = ts3base
    # register class to ts3eventscripts
    base.register_class(name, core_TS3clients)

class core_TS3clients:
    def __init__(self, ts3base):
        pass

    # to parse raw date from ts3socket
    def parse_raw_data(self, msg, multiple=True):
        clients = msg.split("error")
        clients = clients[0].split("|")
        new = {}
        for client in clients:
            splitted = client.split(" ")
            details = {}
            # parsing arguments
            for arg in splitted:
                one = arg.split('=', 1)
                if len(one) == 2:
                    details[ts3tools.unescape_text(one[0])] = ts3tools.unescape_text(one[1])
                else:
                    details[ts3tools.unescape_text(one[0])] = None
            if 'clid' in details:
                if multiple is True:
                    new[details['clid']] = details
                else:
                    return details
        return new

    # get list of connected clients
    def clientlist(self, flags='-uid -away -voice -times -groups -info -icon -country'):
        global clientlist, nextClientlist
        if nextClientlist <= time.time():
            clientlist = self.parse_raw_data(base.send_receive('clientlist ' + flags))
            nextClientlist = time.time() + nextClientlistInterval
        return clientlist
