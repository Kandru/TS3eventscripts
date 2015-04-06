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
    # to parse raw date from ts3socket
    def parse_raw_data(self, msg, multiple=True):
        channels = msg.split("error")
        channels = channels[0].split("|")
        new = {}
        for channel in channels:
            splitted = channel.split(" ")
            details = {}
            # parsing arguments
            for arg in splitted:
                one = arg.split('=', 1)
                if len(one) == 2:
                    details[ts3tools.unescape_text(one[0])] = ts3tools.unescape_text(one[1])
                else:
                    details[ts3tools.unescape_text(one[0])] = None
            if 'cid' in details:
                if multiple is True:
                    new[details['cid']] = details
                else:
                    return details
        return new

    # get channel list
    def channellist(self, flags='-topic -flags -voice -limits -icon'):
        global channellist, nextChannellist
        if nextChannellist <= time.time():
            channellist = self.parse_raw_data(base.send_receive('channellist ' + flags))
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
        return self.parse_raw_data(base.send_receive('channelcreate channel_name=' + ts3tools.escape_text(name) + properties))

    # edit specific channel
    def channeledit(self, cid, propertiesdict=[]):
        # parse all properties
        properties = ''
        for item in propertiesdict:
            properties = properties + ' ' + item + '=' + ts3tools.escape_text(str(propertiesdict[item]))
        return self.parse_raw_data(base.send_receive('channeledit cid=' + str(cid) + ' ' + properties))
