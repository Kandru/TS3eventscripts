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
