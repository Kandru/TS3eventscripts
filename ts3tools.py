import configparser

# static definitions
escapeText = [
    (' ', '\s'),
    ('|', '\p')
    #('/', '\/')
    ]

unescapeText = [
    (' ', '\s'),
    ('|', '\p'),
    ('/', '\/'),
    ('', '\n'),
    ('', '\r')]

class ts3tools:

    def escape_text(msg):
        for search, replace in escapeText:
            msg = msg.replace(search, replace)
        return msg

    def unescape_text(msg):
        for search, replace in unescapeText:
            msg = msg.replace(replace, search)
        return msg

    def parse_raw_event(msg):
        splitted = msg.split(" ")

        new = {'ev_type': splitted[0]}
        # because in the new dict the event name already exists, we remove it from the splitted list
        splitted.pop(0)
        # parsing arguments
        for arg in splitted:
            one = arg.split('=', 1)
            if len(one) == 2:
                new[ts3tools.unescape_text(one[0])] = ts3tools.unescape_text(one[1])
            else:
                new[ts3tools.unescape_text(one[0])] = None
        return new

    def parse_raw_answer(msg):
        msg = msg.replace('\n', ' ')
        splitted = msg.split(' ')

        new = {}
        for arg in splitted:
            one = arg.split('=', 1)
            if len(one) == 2:
                new[ts3tools.unescape_text(one[0])] = ts3tools.unescape_text(one[1])
            else:
                new[ts3tools.unescape_text(one[0])] = None
        return new

    def set_nickname(base, nickname, socket=False):
        if socket is False:
            return base.send_receive(
                'clientupdate client_nickname=' + ts3tools.escape_text(nickname))
        else:
            return base.get_event_socket().send(
                'clientupdate client_nickname=' + ts3tools.escape_text(nickname))

    # config schema (for docs later):
    # configs/
    # configs/[plugin_name].ini                 -> global plugin config
    # configs/[instance_id]/[plugin_name].ini   -> instance-only plugin config
    def get_global_config(plugin_name):
        """
        Returns the global config of a plugin identified by file name. If the config isn't existing, return nothing (None).
        Note: You can only have one config at one time, but that's not a problem. INI-Files can be categorized with sections.

        @plugin_name    name of the plugin (unique plugin name)
        """
        config = configparser.ConfigParser()
        if config.read('configs/' + plugin_name + '.ini') == []:
            config = None
        return config

    def get_instance_config(base, plugin_name):
        """
        Returns the instance-only config of a plugin identified by file name. If the config isn't existing, return nothing (None).
        Note: You can only have one config at one time, but that's not a problem. INI-Files can be categorized with sections.

        @base           ts3base object (for finding out instance name)
        @plugin_name    name of the plugin (unique plugin name)
        """
        config = configparser.ConfigParser()
        if config.read('configs/' + base.config['id'] + '/' + plugin_name + '.ini') == []:
            config = None
        return config

class TS3_DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    The subindex can set that only one difference (one value in sub dictionary) are calculated.

    Grabbed biggest part from: https://github.com/hughdbrown/dictdiffer
    """
    def __init__(self, current_dict, past_dict, subindex=None):
        self.subindex = subindex
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        if self.subindex is None:
            return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
        else:
            return set(o for o in self.intersect if self.past_dict[o][self.subindex] != self.current_dict[o][self.subindex])

    def unchanged(self):
        if self.subindex is None:
            return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])
        else:
            return set(o for o in self.intersect if self.past_dict[o][self.subindex] == self.current_dict[o][self.subindex])
