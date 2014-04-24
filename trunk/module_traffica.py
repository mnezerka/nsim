
def initialize():
	print "Traffica module initialized"

def getInfoChannels():
	channels = []
	channels.append({'name': 'sessions', 'description': 'Traffica sessions'})
	return channels;

def getInfoChannel(name):
	lines = []
	lines.append('sessions: %d' % 0);
	result  = { "data" : lines }
	return result;
