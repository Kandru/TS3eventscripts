from ts3tools import ts3tools
import time

name = 'core.TS3channel'
base = None

# get a centralized channellist to avoid spamming server commands for channellists every second
nextChannellistInterval = 2
nextChannellist = 0
channellist = {}

def setup(ts3base):
    global base
    base = ts3base
    # register class to ts3eventscripts
    base.register_class(name, core_TS3channel)

class core_TS3channel:
    def __init__(self, ts3base):
        pass

    # get channel list
    def channellist(self, flags='-topic -flags -voice -limits -icon'):
        global channellist, nextChannellist
        if nextChannellist <= time.time():
            channellist = ts3tools.parse_raw_data(base.send_receive('channellist ' + flags), 'cid')
            nextChannellist = time.time() + nextChannellistInterval
        return channellist

    # delete specific channel
    def channeldelete(self, cid, force=1):
        return base.send_receive('channeldelete cid=' + str(cid) + ' force=' + str(force))

    # move specific channel
    def channelmove(self, cid, cpid, order=0):
        return base.send_receive('channelmove cid=' + str(cid) + ' cpid=' + str(cpid) + ' order=' + str(order))

    # create specific channel
    def channelcreate(self, name, propertiesdict=[]):
        # parse all properties
        properties = ''
        for item in propertiesdict:
            properties = properties + ' ' + item + '=' + ts3tools.escape_text(str(propertiesdict[item]))
        return ts3tools.parse_raw_data(base.send_receive('channelcreate channel_name=' + ts3tools.escape_text(name) + properties))

    # edit specific channel
    def channeledit(self, cid, propertiesdict=[]):
        # parse all properties
        properties = ''
        for item in propertiesdict:
            properties = properties + ' ' + item + '=' + ts3tools.escape_text(str(propertiesdict[item]))
        return ts3tools.parse_raw_data(base.send_receive('channeledit cid=' + str(cid) + ' ' + properties))
