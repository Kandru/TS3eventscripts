import os
from http.server import HTTPServer, CGIHTTPRequestHandler
from jinja2 import Template

"""
Need: sudo pip3 install jinja2
"""

class ts3http():
    def __init__(self, instances):
        print (instances)
        serv = HTTPServer(('', 8080), MyRequestHandler)
        serv.serve_forever()

class MyRequestHandler(CGIHTTPRequestHandler):
    def do_GET(self):
        try:
            path = './wwwroot/' + self.path.split('?')[0]
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                f = open('./wwwroot/index.html')
                tpl = Template(f.read())
                self.wfile.write(bytes(tpl.render(), 'UTF-8'))
                f.close()
                return
            elif '.html' in path:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                f = open(path)
                tpl = Template(f.read())
                self.wfile.write(bytes(tpl.render(), 'UTF-8'))
                f.close()
                return
            else:
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
            # self.send_error(404, 'file not found: %s' % self.path)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            f = open('./wwwroot/templates/404.html')
            tpl = Template(f.read())
            self.wfile.write(bytes(tpl.render(), 'UTF-8'))
            f.close()

    def do_POST(self):
        self.do_GET()
