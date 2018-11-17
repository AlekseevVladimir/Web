import socket
import struct
import json
import select
import drawer
from enum import Enum

def main():
	sock = socket.socket()
	sock.connect(('wgforge-srv.wargaming.net', 443))
	data = login(sock)
	print(data)
	print("\n")
	data = getmap(sock, 0)
	print(data)
	print("\n")
	data = getmap(sock,10)
	print(data)
	print("\n")
	# print(data["trains"])
	# print(data)
	# map_l1 = getmap(sock, 1)
	# map_l0 = getmap(sock, 0)
	# # map_l10=getmap(sock, 10)
	# # print(action(sock, 6, ''))
	# print(map_l0["lines"])
	# nextturn(sock)
	# move(sock, 5, 1, 1)
	# nextturn(sock)
	# print(map_l1["trains"])
	# getplayerinfo(sock)
	move(sock,1, 1, 1)
	data = getmap(sock,1)
	print(data)
	upgrade(sock, 1, 1)
	data = getmap(sock,0)
	print(data)
	drawer.main(data)
	logout(sock)
	
	sock.close()
 
 
class Action(Enum):
	LOGIN = 1
	LOGOUT = 2
	MOVE = 3
	UPGRADE = 4
	TURN = 5
	PLAYER = 6
	MAP = 10

class Result(Enum):
	OKEY = 0
	BAD_COMMAND = 1
	RESOURCE_NOT_FOUND = 2
	ACCESS_DENIED = 3
	NOT_READY = 4
	TIMEOUT = 5
	INTERNAL_SERVER_ERROR = 500

def action(sock, tmp, string):
	bytes = tmp.to_bytes(4, byteorder='little') + len(string).to_bytes(4, byteorder='little') + string.encode()
	print(bytes)
	sock.send(bytes)
	response = sock.recv(4)
	if response:
		response = struct.unpack('L', response)[0]
	else:
		return -1
	print(response)
	if response != Result.OKEY.value:
		while True:
			ready, a, b = select.select([sock], [], [], 10)
			if len(ready)==0: break
			sock.recv(1)
		errorReport(response)
		return -1
	datalen = sock.recv(4)
	datalen = struct.unpack('L', datalen)[0]
	if datalen:
		# print(datalen)
		sock.settimeout(10)
		data = sock.recv(datalen)
		datalen -= len(data)
		while datalen > 0:
			data += sock.recv(datalen)
			datalen -= len(data)
		data = data.decode('utf8').replace("\n", '').replace(" ", '')
		data = json.loads(data)
		return data

def login(sock):
	print("enter username: ")
	name = input()
	string = json.dumps({"name": name})
	data = action(sock, Action.LOGIN.value, string)
	return data

def player(sock):
	data = action(sock, Action.PLAYER.value, '')
	return data
 
def logout(sock):
	return action(sock,Action.LOGOUT.value, '')
 
def getmap(sock, layer):
	string = json.dumps({"layer": layer})
	data = action(sock, Action.MAP.value, string)
	return data
 
def nextturn(sock):
	#bytes = int(Action.TURN.value).to_bytes(4, byteorder='little')
	#sock.send(bytes)
	action(sock, Action.TURN.value, '')
 
def move(sock, line_idx, speed, train_idx):
	string = json.dumps({"line_idx": line_idx, "speed": speed, "train_idx": train_idx})
	data=action(sock, Action.MOVE.value, string)
	#bytes = int(Action.MOVE.value).to_bytes(4, byteorder='little') + len(string).to_bytes(4, byteorder='little') + string.encode()
	#sock.send(bytes)
def upgrade(sock, posts, trains):
	posts=[posts]
	trains=[trains]
	string = json.dumps({"posts": posts, "trains": trains})
	print(string)
	data=action(sock, Action.UPGRADE.value, string)
	
def errorReport(code):
	if code == Result.BAD_COMMAND.value:
		print("Bad command")
	elif code == Result.RESOURCE_NOT_FOUND.value:
		print("Resource not found")
	elif code == Result.ACCESS_DENIED.value:
		print("Access denied")
	elif code == Result.NOT_READY.value:
		print("Not ready")
	elif code == Result.TIMEOUT.value:
		print("Timeout")
	else:
		print("Internal server error")
main()