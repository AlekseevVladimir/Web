import socket
import struct
import json
import select
from enum import Enum


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


class Socket():
	url = 'wgforge-srv.wargaming.net'
	port = 443

	def __init__(self):
		print("sock init")
		self.sock = socket.socket()
		self.sock.connect((self.url, self.port))

	def __del__(self):
		print("destroyed")
		self.logout()
		self.sock.close()

	def inter(self, data):
		choice = data[0]
		if choice == Action.LOGIN.value:
			return self.login(data[1])
		elif choice == Action.LOGOUT.value:
			return self.logout()
		elif choice == Action.MOVE.value:
			return self.move(data[1], data[2], data[3])
		elif choice == Action.UPGRADE.value:
			return self.upgrade(data[1], data[2])
		elif choice == Action.TURN.value:
			return self.nextTurn()
		elif choice == Action.PLAYER.value:
			return self.player()
		elif choice == Action.MAP.value:
			return self.getmap(data[1])
		else:
			print("Unknown command")

	def action(self, tmp, string):
		TIMEOUT = 10
		DATAPACK = 4
		bytes = tmp.to_bytes(DATAPACK, byteorder='little') + len(string).to_bytes(DATAPACK,
																				  byteorder='little') + string.encode()
		self.sock.send(bytes)
		response = self.sock.recv(DATAPACK)
		if response:
			response = struct.unpack('L', response)[0]
		else:
			return response
		# print(response)
		if response != Result.OKEY.value:
			while True:
				ready, a, b = select.select([self.sock], [], [], TIMEOUT)
				if len(ready) == 0: break
				self.sock.recv(1)
			self.errorReport(response)
			return response
		datalen = self.sock.recv(DATAPACK)
		datalen = struct.unpack('L', datalen)[0]
		if datalen:
			# print("\nlen(data)\n")
			# print(datalen)
			self.sock.settimeout(TIMEOUT)
			data = self.sock.recv(datalen)
			while datalen > len(data):
				data += self.sock.recv(datalen)
			data = data.decode('utf8').replace("\n", '').replace(" ", '')
			# print(data)
			data = json.loads(data)
			return response, data
		return response

	def login(self, name):
		string = json.dumps({"name": name})
		return self.action(Action.LOGIN.value, string)

	def player(self):
		return self.action(Action.PLAYER.value, '')

	def logout(self):
		data = self.action(Action.LOGOUT.value, '')
		return data

	def getmap(self, layer):
		#print(layer)
		string = json.dumps({"layer": layer})
		return self.action(Action.MAP.value, string)

	def nextTurn(self):
		return self.action(Action.TURN.value, '')

	def move(self, line_idx, speed, train_idx):
		string = json.dumps({"line_idx": line_idx, "speed": speed, "train_idx": train_idx})
		return self.action(Action.MOVE.value, string)

	def upgrade(self, posts, trains):
		posts = [posts]
		trains = [trains]
		string = json.dumps({"posts": posts, "trains": trains})
		return self.action(Action.UPGRADE.value, string)

	def errorReport(self, code):
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