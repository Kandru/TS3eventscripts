import os
from http.server import HTTPServer, CGIHTTPRequestHandler
from jinja2 import Template

"""
Need: sudo pip3 install jinja2
"""
instances = None

class ts3http():
    def __init__(self, inst):
        global instances
        instances = inst
        serv = HTTPServer(('', 8080), MyRequestHandler)
        serv.serve_forever()

class MyRequestHandler(CGIHTTPRequestHandler):
    def do_GET(self):
        global instances
        print(instances)
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
            elif self.path.split('/')[1] in instances:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                f = open('./wwwroot/instance.html')
                tpl = Template(f.read())
                self.wfile.write(bytes(tpl.render(instance=instances[self.path.split('/')[1]]), 'UTF-8'))
                f.close()
                return
            elif '/assets/' in self.path:
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
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                f = open('./wwwroot/templates/404.html')
                tpl = Template(f.read())
                self.wfile.write(bytes(tpl.render(), 'UTF-8'))
                f.close()
        except IOError:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            # self.end_headers()
            f = open('./wwwroot/templates/404.html')
            tpl = Template(f.read())
            self.wfile.write(bytes(tpl.render(), 'UTF-8'))
            f.close()

    def do_POST(self):
        self.do_GET()
