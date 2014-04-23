import socket
import json

data = {'method':'add', 'params': [3, 60]}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 9999))
s.send("GET /")
result = s.recv(1024)
print result
s.close()


