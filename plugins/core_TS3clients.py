from ts3tools import ts3tools
import time

name = 'core.TS3clients'
base = None

# get a centralized clientlist to avoid spamming server commands for clientlists every second
nextClientlistInterval = 2
nextClientlist = 0
clientlist = {}
nextGrouplistInterval = 30
nextGrouplist = 0
grouplist = {}

def setup(ts3base):
    global base
    base = ts3base
    # register class to ts3eventscripts
    base.register_class(name, core_TS3clients)

class core_TS3clients:
    def __init__(self, ts3base):
        pass

    # get list of connected clients
    def clientlist(self, flags='-uid -away -voice -times -groups -info -icon -country'):
        global clientlist, nextClientlist
        if nextClientlist <= time.time():
            clientlist = ts3tools.parse_raw_data(base.send_receive('clientlist ' + flags), 'clid')
            nextClientlist = time.time() + nextClientlistInterval
        return clientlist

    # get list of groups
    def grouplist(self):
        global grouplist, nextGrouplist
        if nextGrouplist <= time.time():
            grouplist = ts3tools.parse_raw_data(base.send_receive('servergrouplist'), 'sgid')
            nextGrouplist = time.time() + nextGrouplistInterval
        return grouplist

    def clientmove(self, clid, cid):
        clidstring = ''
        if isinstance(clid, list):
            i = False
            for one in clid:
                if i is False:
                    clidstring += one
                    i = True
                else:
                    clidstring += '|' + one
        else:
            clidstring = clid
        return ts3tools.parse_raw_data(base.send_receive('clientmove clid=' + clidstring + ' cid=' + cid))

    def clientinfo(self, clid):
        query = base.send_receive('clientinfo clid=' + clid)
        parsed = ts3tools.parse_raw_answer(query)
        return parsed

    def client_add_servergroup(self, sgid, cldbid):
        query = base.send_receive('servergroupaddclient sgid=' + sgid + ' cldbid=' + cldbid)
        parsed = ts3tools.parse_raw_answer(query)
        return parsed

    def client_del_servergroup(self, sgid, cldbid):
        query = base.send_receive('servergroupdelclient sgid=' + sgid + ' cldbid=' + cldbid)
        parsed = ts3tools.parse_raw_answer(query)
        return parsed
