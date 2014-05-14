#!/usr/bin/python
# vim: set expandtab sw=4 ts=4 sts=4 foldmethod=indent:

import json
import time
import urlparse
import BaseHTTPServer
import os
import imp
import glob
import logging
import logging.handlers
from optparse import OptionParser

VERSION = '1.0'

mods = dict() 
scriptPath = os.path.dirname(os.path.realpath(__file__))
remoteUrl = 'localhost:9999'

class NSimRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):


   # def log_message(format, ...):
   #     logger.debug(format)
   #     pass

    def processCmdStatus(self):
        result = {"return" : "ok", "version": VERSION, "status": "running"}
        return result

    def processCmdModules(self):
        jsonModules = [] 
        for m in mods:
            if 'getCommands' in dir(mods[m]):
                commands = mods[m].getCommands()
            else:
                commands = []

            jsonModules.append({
                'name': m,
                'commands': commands})

        result = {"return" : "ok", "modules": jsonModules}

        return result

    def do_POST(self):
        self.do_GET()

    def do_GET(self):
        logger.info('Http Request received %s', self.path)

        url = urlparse.urlparse(self.path)
        urlPathParts = url.path.split('/')
        if len(urlPathParts) != 2:
            self.send_error(404, 'file not found')
            return

        target = 'nsim.html' 
        if len(urlPathParts[1].strip()) > 0:
            target = urlPathParts[1].strip()

        if target in ['nsim.html', 'jquery-1.11.0.min.js', 'nsim.js']:
            # load index page
            f = open(os.path.join(os.curdir, os.path.join(scriptPath, target)))
            self.send_response(200)
            self.send_header('Content-Type','text/html')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return

        elif target == 'nsim-cfg.js':
            body = 'var remoteUrl = \'%s\'' % remoteUrl;
            self.send_response(200)
            self.send_header('Content-Type','text/javascript')
            self.end_headers()
            self.wfile.write(body)
            return

        elif target == 'soap':
            try:
                contentLength = int(self.headers.getheader('content-length'))
                postBody = self.rfile.read(contentLength)
                data = json.loads(postBody)
                result = {"return" : "ok"}

                # get module
                if 'module' in data:
                    module = data['module'];
                else:
                    module = None;

                # process commands
                if 'cmd' in data:

                    # first - check if command is processed by some module 
                    if module in mods:
                        mod = mods[module]
                        if 'processCommand' in dir(mod):
                            if 'params' in data:
                                params = data['params']
                            else:
                                params = []
                            result = mod.processCommand(data['cmd'], params) 
                        else:
                            result['return'] = 'error'
                            result['description'] = 'module does not support command execution'
                    # second - process command by nsim module
                    else:
                        if data['cmd'] == 'status':
                            result = self.processCmdStatus() 
                        elif data['cmd'] == 'modules':
                            result = self.processCmdModules() 
                        else:
                            # unknown command
                            result['return'] = 'error'
                            result['description'] = 'unknown nsim command'

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
    global remoteUrl

    # parse command line arguments
    # process command line arguments
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("-l", "--listen", dest="listenIP", default="127.0.0.1", help="IP address to listen for http requests")
    parser.add_option("-p", "--port", dest="listenPort", default="9999", help="port to listen for http requests")
    (options, args) = parser.parse_args()

    # load dynamic modules
    modules = glob.glob(scriptPath + '/module_*.py')
    for module in modules:
        moduleName, moduleExt = os.path.splitext(module)
        moduleName = os.path.basename(moduleName)
        moduleObj =__import__(moduleName)
        if 'initialize' in dir(moduleObj):
            moduleObj.initialize()
            moduleName = moduleName.replace('module_', '');
            mods[moduleName] = moduleObj

    serverAddress = (options.listenIP, int(options.listenPort))
    remoteUrl = "http://%s:%s/soap" % (options.listenIP, options.listenPort)

    httpd = BaseHTTPServer.HTTPServer(serverAddress, NSimRequestHandler)
    print time.asctime(), "Server Started - %s" % str(serverAddress)
    logger.info('Started')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stopped - %s" % str(serverAddress)
    logger.info('Stopped')

if __name__ == '__main__':
    # initialize logging
    logger = logging.getLogger('nsim')
    logger.setLevel(logging.DEBUG)
    h = logging.handlers.RotatingFileHandler(filename='nsim.log', maxBytes=1024, mode='w')
    #h = logging.StreamHandler()
    h.setLevel(logging.DEBUG)
    f = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%d/%m/%Y %H:%M:%S')
    h.setFormatter(f)
    logger.addHandler(h)

    logger.debug('Logging initialized')

    run()
