import socket
import select
from myexception import MyException

# Buffer size
BUFFER_SIZE = 8192


class ts3socket:

    def __init__(self, ip, port, sid, user, password):
        self.ip = ip
        self.port = port
        self.sid = sid
        self.user = user
        self.password = password
        self.connect()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))
        try:
            msg = self.receive()
            if msg.startswith('TS3'):
                if 'Welcome' not in msg:
                    self.receive()
                self.send('use %s\n\r' % (self.sid, ))
                if not self.receive().endswith('msg=ok\n\r'):
                    raise MyException("ServerID not found")
                self.send('login ' + self.user + ' ' + self.password)
                if not self.receive().endswith('msg=ok\n\r'):
                    raise MyException("username/password wrong")
            else:
                raise MyException("this isn't a TS3-Server, right?")
        except (socket.error, socket.timeout):
            self.disconnect()

    def send(self, msg):
        return self.sock.send((msg + '\n').encode())

    def disconnect(self):
        self.sock.close()

    def receive(self):
        return self.sock.recv(BUFFER_SIZE).decode()

    def recv_all(self):
        total_data = []
        while True:
            read_sockets, write_sockets, error_sockets = select.select([self.sock], [], [], 0.1)
            if read_sockets:
                data = self.sock.recv(BUFFER_SIZE).decode()
                if not data:
                    break
                total_data.append(data)
            else:
                break
        return ''.join(total_data)
