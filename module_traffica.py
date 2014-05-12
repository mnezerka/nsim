# vim: set expandtab sw=4 ts=4 sts=4 foldmethod=indent:

import logging

def initialize():
    logger = logging.getLogger('nsim.traffica')
    logger.debug('Module initialized')

def getInfoChannels():
    channels = []
    channels.append({'name': 'sessions', 'description': 'Traffica sessions'})
    return channels;

def getInfoChannel(name):
    lines = []
    lines.append('sessions: %d' % 0);
    result  = { "data" : lines }
    return result;
