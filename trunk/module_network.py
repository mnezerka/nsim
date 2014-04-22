
def initialize():
	print "Network module initialized"

def getCommands():
	commands = dict()
	return commands;

def getInfoChannels():
	channels = []
	channels.append({'name': 'netstat', 'description': 'Netstat output (netstat -an)'})
	channels.append({'name': 'xyz', 'description': 'xyz desc'})
	return channels;

def getInfoChannel(name):
	result  = { "active-connections" : 23 }
	return result;
