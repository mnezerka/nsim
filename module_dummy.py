import os
import datetime

def initialize():
	print "Dummpy module initialized"

def getCommands():
	commands = []
	commands.append({'name': 'sum', 'description': 'sum(int, int)'})
	return commands;

def getInfoChannels():
	channels = []
	channels.append({'name': 'sysinfo', 'description': 'System information'})
	return channels;

def getInfoChannel(name):
	lines = []
	lines.append('cwd: %s' % os.getcwd());
	lines.append('pid: %d' % os.getpid());
	lines.append('uid: %d' % os.getuid());
	
	times = os.times()
	print times
	lines.append('user time: %f' % times[0]);
	lines.append('system time: %f' % times[1]);

	result  = { "data" : lines }
	return result;

def processCommand(cmd):
	result = { "return": "ok", "result": 23333 }
	return result;
