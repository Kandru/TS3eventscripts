import os
from http.server import HTTPServer, CGIHTTPRequestHandler


class ts3http():
    def __init__(self):
        serv = HTTPServer(('', 8080), MyRequestHandler)
        serv.serve_forever()

class MyRequestHandler(CGIHTTPRequestHandler):
    def do_GET(self):
        path = './wwwroot/' + self.path.split('?')[0]
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            f = open('./wwwroot/index.html')
            self.wfile.write(bytes(f.read(), 'UTF-8'))
            f.close()
        elif '.html' in path:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            f = open(path)
            self.wfile.write(bytes(f.read(), 'UTF-8'))
            f.close()
            return
        else:
            try:
                if '/assets/' in self.path:
                    fileName, fileExtension = os.path.splitext(path)
                    f = open(path, 'rb')
                    if fileExtension == '.png':
                        contentType = 'image/png'
                    elif fileExtension == '.jpg' or fileExtension == '.jpeg':
                        contentType = 'image/jpeg'
                    elif fileExtension == '.css':
                        contentType = 'text/css'
                    else:
                        contentType = 'text/html'
                    self.send_response(200)
                    self.send_header('Content-type', contentType)
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                    return
            except IOError:
                self.send_error(404, 'file not found: %s' % self.path)

    def do_POST(self):
        self.do_GET()
