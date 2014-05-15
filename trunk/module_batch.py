# vim: set expandtab sw=4 ts=4 sts=4 foldmethod=indent:
import logging
import os
import glob

nsim = None
scriptsPath = os.getcwd() 
print "module", scriptsPath

def initialize(ns):
    global scriptsPath
    nsim = ns
    logger = logging.getLogger('nsim.batch')
    logger.debug('Module initialized')
    scriptsPath = os.getcwd() 
     
def getCommands():
    commands = []
    commands.append({'name': 'dir', 'description': 'dir path=fs-path - Set scripts directory'})
    commands.append({'name': 'status', 'description': 'Get status of batch module'})
    commands.append({'name': 'run', 'description': 'run file=path-to-json-file'})
    return commands;

def cmdDir(data):
    global scriptsPath
    result = { "return": "ok" }

    if 'path' in data:
        path = data['path']
        if os.path.isdir(path):
            scriptsPath = path
        else:
            result = { "return": "error", "description": "Invalid path" }
    else:
        result = { "return": "error", "description": "Incorrect arguments" }

    return result

def cmdScripts(data):
    global scriptsPath
    print scriptsPath
    result = { "return": "ok" }
    result["scripts"] = [] 
    searchPath = os.path.join(scriptsPath, '*.json')
    scripts = glob.glob(searchPath)
    for s in scripts:
        result["scripts"].append(os.path.basename(s))

    return result

def cmdStatus(data):
    global scriptsPath

    result = { "return": "ok" }
    result['dir'] = scriptsPath

    return result

def processRequest(data):
    if 'cmd' in data:
        if data['cmd'] == 'status':
            result = cmdStatus(data);
        elif data['cmd'] == 'dir':
            result = cmdDir(data);
        elif data['cmd'] == 'scripts':
            result = cmdScripts(data);
        else:
            result = { "return": "error", "description": 'Unknown command'}
    else:
        result = { 'return': 'error', 'description': 'Unknown request type'}

    return result;
