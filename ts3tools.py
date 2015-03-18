# static definitions
escapeText = [
    (' ', '\s'),
    ('|', '\p'),
    ('/', '\/')]


class ts3tools:

    def escape_text(msg):
        for search, replace in escapeText:
            msg = msg.replace(search, replace)
        return msg

    def set_nickname(socket, nickname):
        return socket.send(
            'clientupdate client_nickname=' + ts3tools.escape_text(nickname))
