from ts3tools import ts3tools

name = 'core.TS3channel'
base = None

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
    def channellist(self, flags=''):
        return self.parse_raw_data(base.send_receive('channellist ' + flags))

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
        print('channelcreate channel_name=' + ts3tools.escape_text(name) + properties)
        return self.parse_raw_data(base.send_receive('channelcreate channel_name=' + ts3tools.escape_text(name) + properties))
