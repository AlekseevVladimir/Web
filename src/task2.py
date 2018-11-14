import socket
import struct
import json
import task1
import select
def main():
	sock=socket.socket()
	sock.connect(('wgforge-srv.wargaming.net', 443))
	data=login(sock)
	print(data["trains"])
	#print(data)
	map_l1=getmap(sock, 1)
	map_l0=getmap(sock, 0)
	#map_l10=getmap(sock, 10)
	#print(action(sock, 6, ''))
	print(map_l0["lines"])
	nextturn(sock)
	move(sock, 5, 1, 1)
	nextturn(sock)
	print(map_l1["trains"])
	logout(sock)
	sock.close()

def action(sock, tmp, string):
	bytes=tmp.to_bytes(4, byteorder='little')+len(string).to_bytes(4, byteorder='little')+string.encode()
	sock.send(bytes)
	response=sock.recv(4)
	response=struct.unpack('L', response)[0]
	#print(response)
	if response!=0:
		while True:
			ready, a, b=select.select([sock],[],[],10)
			if len(ready)==0: break
			sock.recv(1)
		errorReport(response)
		return 0
	datalen=sock.recv(4)
	datalen=struct.unpack('L', datalen)[0]
	#print(datalen)
	sock.settimeout(10)
	data=sock.recv(datalen)
	datalen-=len(data)
	while datalen>0:
		data+=sock.recv(datalen)
		datalen-=len(data)
	data = data.decode('utf8').replace("\n", '').replace(" ", '')
	data=json.loads(data)
	return data
	
def logout(sock):
	bytes=int(2).to_bytes(4, byteorder='little')
	sock.send(bytes)
	
def getplayerinfo(sock):
	action(sock, 6, '')
	
def nextturn(sock):
	bytes=int(5).to_bytes(4, byteorder='little')
	sock.send(bytes)
	
def login(sock):
	print ("enter username")
	name=input()
	string=json.dumps({"name":name})
	#print(adict)
	#string='{"name":"'+name+'"}'
	data = action(sock,1,string)
	return data
	
def getmap(sock, layer):
	string=json.dumps({"layer":layer})
	data=action(sock, 10, string)
	#print(data)
	#task1.parse(data)
	return data

	
def move(sock, line_idx, speed, train_idx):
	string=json.dumps({"line_idx":line_idx, "speed":speed, "train_idx":train_idx})
	bytes=int(3).to_bytes(4, byteorder='little')+len(string).to_bytes(4, byteorder='little')+string.encode()
	sock.send(bytes)
	
def errorReport(code):
	if code==1:
		print("Bad command")
	elif code==2:
		print("Resource not found")
	elif code==3:
		print("Access denied")
	elif code==4:
		print("Not ready")
	elif code==5:
		printf("Timeout")
	else:
		print("Internal server error")
	
	
main()