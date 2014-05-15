# vim: set expandtab sw=4 ts=4 sts=4 foldmethod=indent:
import logging

def initialize(nsim):
    logger = logging.getLogger('nsim.dummy')
    logger.debug('Module initialized')

def getCommands():
    commands = []
    commands.append({'name': 'sum', 'description': 'sum p1=int p2=int'})
    return commands;

def processRequest(data):
    if 'cmd' in data:
        if data['cmd'] == 'sum':
            if 'p1' in data and 'p2' in data:
                try:
                    p1 = int(data['p1'])
                except:
                    p1 = 0   
                try:
                    p2 = int(data['p2'])
                except:
                    p2 = 0   
                result = { "return": "ok"}
                result['result'] = p1 + p2 
            else:
                result = { "return": "error", "description": "Incorrect set of arguments" }
        else:
            result = { "return": "error", "description": 'Unknown command'}
    else:
        result = { 'return': 'error', 'description': 'Unknown request type'}


    return result;
