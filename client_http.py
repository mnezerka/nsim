import httplib
import json

def httpRequest(host, path):

	print "Sending http request to host:", host, ", path:", path
	conn = httplib.HTTPConnection(host)
	conn.request("GET", path)
	r1 = conn.getresponse()
	print(r1.status, r1.reason)
	print r1.getheaders()
	data1 = r1.read()  # This will return entire content.
	print data1, len(data1)
	print json.loads(data1)

	conn.close()


httpRequest('127.0.0.1:9999', '/')
httpRequest('127.0.0.1:8080', '/learn_python/json2/php1/test1.php')
