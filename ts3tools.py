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

    def set_nickname(socket, nickname):
        return socket.send(
            'clientupdate client_nickname=' + ts3tools.escape_text(nickname))
    
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