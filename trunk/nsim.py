#!/usr/bin/python
# vim: set expandtab sw=4 ts=4 sts=4 foldmethod=indent:

import json
import time
import urlparse
import BaseHTTPServer
import os
import imp
import glob

PORT_NUMBER = 9999 
HOST_NAME = '127.0.0.1'
VERSION = '1.0'

mods = dict() 

class TraffikaHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def processCmdStatus(self):
        result = {"return" : "ok", "version": VERSION, "status": "running"}
        return result

    def processCmdModules(self):
        jsonModules = [] 
        for m in mods:
            if 'getInfoChannels' in dir(mods[m]):
                infoChannels = mods[m].getInfoChannels()
            else:
                infoChannels = []
            jsonModules.append({
                'name': mods[m].__name__,
                'infochannels': infoChannels})

        result = {"return" : "ok", "modules": jsonModules}

        return result


    def do_POST(self):
        self.do_GET()

    def do_GET(self):
        url = urlparse.urlparse(self.path)
        urlPathParts = url.path.split('/')
        if len(urlPathParts) != 2:
            self.send_error(404, 'file not found')
            return

        target = 'rsim.html' 
        if len(urlPathParts[1].strip()) > 0:
            target = urlPathParts[1].strip()

        if target in ['rsim.html', 'jquery-1.11.0.min.js', 'rsim.js']:
            # load index page
            f = open(os.path.join(os.curdir, target))
            self.send_response(200)
            self.send_header('Content-Type','text/html')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return

        elif target == 'soap':
            try:
                contentLength = int(self.headers.getheader('content-length'))
                postBody = self.rfile.read(contentLength)
                data = json.loads(postBody)
                result  = {"return" : "ok"}

                # get module
                if 'module' in data:
                    module = data['module'];
                else:
                    module = None;

                # process commands
                if 'cmd' in data:
                    if data['cmd'] == 'status':
                        result = self.processCmdStatus() 
                    if data['cmd'] == 'modules':
                        result = self.processCmdModules() 

                #process info channels
                if 'channel' in data:
                    if module in mods:
                        mod = mods[module]
                        if 'getInfoChannel' in dir(mod):
                            result = mod.getInfoChannel(data['channel']);
                            result['return'] = 'ok'
                            result['module'] = module
                            result['channel'] = data['channel'] 
                
                jsonResponse = json.dumps(result)

                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type','application/json')
                self.send_header('Content-Length', len(jsonResponse))
                self.send_header('Expires', '-1')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Pragma', 'no-cache')
                self.end_headers()

                self.wfile.write(jsonResponse)
                self.wfile.flush()
                self.connection.shutdown(1)
                return
                 
            except IOError:
                self.send_error(404, 'file not found')

def run():

    # load dynamic modules
    modules = glob.glob('module_*.py')
    for module in modules:
        moduleName, moduleExt = os.path.splitext(module)
        moduleObj =__import__(moduleName)
        if 'initialize' in dir(moduleObj):
            moduleObj.initialize()
            mods[moduleName] = moduleObj

    server_address = (HOST_NAME, PORT_NUMBER)
    httpd = BaseHTTPServer.HTTPServer(server_address, TraffikaHTTPRequestHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)

if __name__ == '__main__':
    run()