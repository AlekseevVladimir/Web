import socket
import struct
import json
import task1
def main():
	sock=socket.socket()
	sock.connect(('wgforge-srv.wargaming.net', 443))
	data=login(sock)
	sock.close()

#def operation()
def action(sock, tmp, string):
	bytes=tmp.to_bytes(4, byteorder='little')+len(string).to_bytes(4, byteorder='little')+string.encode()
	sock.send(bytes)
	response=sock.recv(4)
	data=sock.recv(1024)
	return data
	

def login(sock):
	print ("enter username")
	name=input()
	string='{"name":"'+name+'"}'
	data = action(sock,1,string)
	return data
	
def getmap(sock, layer):
	string='{"layer":'+str(layer)+'}'

	data = action(sock,10,string)
	return data
	

	
	
main()