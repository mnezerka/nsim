#!/usr/bin/python
# vim: set expandtab sw=4 ts=4 sts=4 foldmethod=indent:
#
# TODO:
# - json script for reading commands structured into scenario
# - better loggin of http requests

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

class NSimRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def log_message(*arg):
        pass

    def do_POST(self):
        self.do_GET()

    def do_GET(self):
        self.server.nsim.logger.info('Http Request received %s', self.path)

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
            f = open(os.path.join(os.curdir, os.path.join(self.server.nsim.scriptPath, target)))
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
                result = self.server.nsim.processJsonRequest(data)
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

class NSim():

    VERSION = '1.0'

    def __init__(self):
        self.mods = dict() 
        self.scriptPath = os.path.dirname(os.path.realpath(__file__))
        self.remoteUrl = 'localhost:9999'
        self.logFile = 'nsim.log'

    def run(self):
        # parse command line arguments
        parser = OptionParser(usage="usage: %prog [options]")
        parser.add_option("-l", "--listen", dest="listenIP", default="127.0.0.1", help="IP address to listen for http requests")
        parser.add_option("-p", "--port", dest="listenPort", default="9999", help="port to listen for http requests")
        parser.add_option("-g", "--logfilepath", dest="logFilePath", default=None, help="path to directory to store logfile (if not specified, log file is created in current working directory")
        (options, args) = parser.parse_args()

        # initialize logging
        if not options.logFilePath is None and os.path.isdir(options.logFilePath):
            self.logFile = os.path.join(options.logFilePath, self.logFile)
        self.logger = logging.getLogger('nsim')
        self.logger.setLevel(logging.DEBUG)
        h = logging.handlers.RotatingFileHandler(filename=self.logFile, maxBytes=1048576, mode='w')
        #h = logging.StreamHandler()
        h.setLevel(logging.DEBUG)
        f = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%d/%m/%Y %H:%M:%S')
        h.setFormatter(f)
        self.logger.addHandler(h)
        self.logger.debug('Logging initialized')

        # load dynamic modules
        modules = glob.glob(self.scriptPath + '/module_*.py')
        for module in modules:
            moduleName, moduleExt = os.path.splitext(module)
            moduleName = os.path.basename(moduleName)
            moduleObj =__import__(moduleName)
            if 'initialize' in dir(moduleObj):
                moduleObj.initialize(self)
                moduleName = moduleName.replace('module_', '');
                self.mods[moduleName] = moduleObj

        serverAddress = (options.listenIP, int(options.listenPort))
        remoteUrl = "http://%s:%s/soap" % (options.listenIP, options.listenPort)

        httpd = BaseHTTPServer.HTTPServer(serverAddress, NSimRequestHandler)
        httpd.nsim = self
        print "Server Started - %s" % str(serverAddress)
        self.logger.info('Started')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        print "Server Stopped - %s" % str(serverAddress)
        self.logger.info('Stopped')

    def processJsonRequest(self, data):
        result = {"return" : "error", "description": "Unknown request type"}

        # first - check if request is processed by some module 
        if 'module' in data:
            module = data['module'];
            if module in self.mods:
                mod = self.mods[module]
                if 'processRequest' in dir(mod):
                    result = mod.processRequest(data) 
                else:
                    result['return'] = 'error'
                    result['description'] = 'Module does not support soap rpc'
            else:
                # unknown module 
                result['return'] = 'error'
                result['description'] = 'Unknown nsim module'

        # second - process request by nsim module
        else:
            # process commands
            if 'cmd' in data:
                if data['cmd'] == 'status':
                    result = self.processCmdStatus() 
                elif data['cmd'] == 'modules':
                    result = self.processCmdModules() 
                else:
                    # unknown command
                    result['return'] = 'error'
                    result['description'] = 'Unknown nsim command'
            else:
                result['return'] = 'error'
                result['description'] = 'Unknown request type'

        return result
         
    def processCmdStatus(self):
        result = {"return" : "ok"}
        result["version"] = NSim.VERSION;
        result["status"] = "running"
        result["url"] = self.remoteUrl 
        result["cwd"] = os.getcwd()
        result["log-file-path"] = self.logFile

        return result

    def processCmdModules(self):
        jsonModules = [] 
        for m in self.mods:
            if 'getCommands' in dir(self.mods[m]):
                commands = self.mods[m].getCommands()
            else:
                commands = []

            jsonModules.append({
                'name': m,
                'commands': commands})

        result = {"return" : "ok", "modules": jsonModules}

        return result


nsim = NSim()

if __name__ == '__main__':
    nsim.run()
