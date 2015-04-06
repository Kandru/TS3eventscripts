import configparser

# static definitions
escapeText = [
    (' ', '\s'),
    ('|', '\p'),
    ('/', '\/')]

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
        if socket == False:
            return base.send_receive(
                'clientupdate client_nickname=' + ts3tools.escape_text(nickname))
        else:
            return base.get_event_socket().send(
                'clientupdate client_nickname=' + ts3tools.escape_text(nickname))

    ## config schema (for docs later):
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