# vim: set expandtab sw=4 ts=4 sts=4 foldmethod=indent:
import os
import datetime
import logging

sessions = []

def initialize():
    logger = logging.getLogger('nsim.dummy')
    logger.debug('Module initialized')

def getCommands():
	commands = []
	commands.append({'name': 'sum', 'description': 'sum(int, int)'})
	commands.append({'name': 'session-open', 'description': ''})
	commands.append({'name': 'session-close', 'description': ''})
	return commands;

def getInfoChannels():
	channels = []
	channels.append({'name': 'sysinfo', 'description': 'System information'})
	channels.append({'name': 'sessions', 'description': 'Dumy sessions status'})
	return channels;

def getInfoChannel(name):
	lines = []

	if name == 'sysinfo':
		lines.append('cwd: %s' % os.getcwd());
		lines.append('pid: %d' % os.getpid());
		
		times = os.times()
		lines.append('user time: %f' % times[0]);
		lines.append('system time: %f' % times[1]);
		result  = { "data" : lines }

	elif name == 'sessions':
		lines.append('sessions: %d' % len(sessions));
		result  = { "data" : lines }

	return result

def processCommand(cmd, params):
	if cmd == 'sum':
		result = { "return": "ok", "result": 23333 }

	elif cmd == 'session-open':
		if len(params) > 0:
			sessionId = params[0]
			if sessionId in sessions:
				result = { "return": "error", 'description': 'Session (%s) is already open' % sessionId }
			else:
				sessions.append(sessionId)
				result = { "return": "ok" }
		else:
			result = { "return": "error", 'description': 'Missing session id' }

	elif cmd == 'session-close':
		result = { "return": "ok" }

	else:
		result = { "return": "error", "description": 'Unknown command'}

	return result;
