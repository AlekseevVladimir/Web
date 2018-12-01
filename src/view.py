import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from dataprocessor import drawMap, drawTrains, moveTrains, position_is_node
from parse import Parse
from map import Map, PostType
from serverinteraction import Socket
from time import time as timer
from enum import Enum
import networkx as nx
import random

TIMEOUT = 10


class MapLayer(Enum):
	ZERO_LAYER = 0
	FIRST_LAYER = 1


class PrettyWidget(QWidget):
	def __init__(self):
		super(PrettyWidget, self).__init__()
		self.server_interation = Socket()
		self.button_sign_in = ['sign_in']
		self.button_logout = ['logout']
		self.trains = None
		self.isSignIn = False
		#self.train_buttons = None
		self.initUI()


	def initUI(self):
		font = QFont()
		font.setPointSize(16)
		self.setGeometry(100, 100, 800, 600)
		self.setMinimumSize(500, 300)
		self.center()
		self.setWindowTitle('Graph viewer')

		grid = QGridLayout()
		self.setLayout(grid)
		self.create_vertical_group_box(self.button_sign_in)

		self.button_layout = QVBoxLayout()
		self.button_layout.addWidget(self.vertical_group_box)

		self.figure = plt.figure()
		self.canvas = FigureCanvas(self.figure)
		grid.addWidget(self.canvas, 0, 1, 9, 9)
		grid.addLayout(self.button_layout, 0, 0)

		self.show()

	def create_vertical_group_box(self, buttons):
		self.vertical_group_box = QGroupBox()

		layout = QVBoxLayout()
		for i in buttons:
			button = QPushButton(i)
			button.setObjectName(i)
			layout.addWidget(button)
			layout.setSpacing(10)
			self.vertical_group_box.setLayout(layout)
			button.clicked.connect(self.submitCommand)

	def submitCommand(self):
		eval('self.' + str(self.sender().objectName()) + '()')

	def initial_map(self):
		self.update()
		self.figure.clf()
		drawMap(self.map.graph, self.map.town, self.map.market, self.map.storage)
		print(self.server_interation.getmap(MapLayer.FIRST_LAYER.value))
		response, json_map = self.server_interation.getmap(MapLayer.FIRST_LAYER.value)
		if not response:
			self.trains = json_map["trains"]
			trains, self.train_buttons = Parse.parseTrains(json_map["trains"], self.map.graph)
			if trains:
				drawTrains(trains)
		self.canvas.draw()
		self.canvas.flush_events()

	def update_map(self):
		self.update()
		self.figure.clf()
		drawMap(self.map.graph, self.map.town, self.map.market, self.map.storage)
		print(self.server_interation.getmap(MapLayer.FIRST_LAYER.value))
		response, json_map = self.server_interation.getmap(MapLayer.FIRST_LAYER.value)
		if not response:
			self.trains = json_map["trains"]
			trains, self.train_buttons = Parse.parseTrains(json_map["trains"], self.map.graph)
			if trains: drawTrains(trains)
		self.canvas.draw()

	def update(self):
		map_layer_first = self.server_interation.getmap(MapLayer.FIRST_LAYER.value)[1]
		train = map_layer_first["trains"][0]
		is_node = position_is_node(nx.get_edge_attributes(self.map.graph, "idx").items(),nx.get_edge_attributes(self.map.graph, "weight").items()
								   ,train['line_idx'], train['position'])
		if is_node[0] and (is_node[1] in self.map.town or is_node[1] in self.map.market):
			if is_node[1] in self.map.town:
				idx_market = 0#random.randint(0, len(self.map.market)-1)#need def, which calculated most efficence market
				self.shortest_path = nx.shortest_path(self.map.graph, source= self.map.town[0], target=self.map.market[idx_market])
				res = moveTrains(map_layer_first['trains'], self.map.graph,
								 self.shortest_path[self.shortest_path.index(is_node[1]) + 1], 1)
				self.server_interation.move(res[0], res[1], res[2])
			else:
				idx_market = is_node[1]
				self.shortest_path = nx.shortest_path(self.map.graph, source=idx_market,
													  target=self.map.town[0])
				res = moveTrains(map_layer_first['trains'], self.map.graph,
								 self.shortest_path[self.shortest_path.index(is_node[1]) + 1], 1)
				self.server_interation.move(res[0], res[1], res[2])
		elif is_node[0]:
			res = moveTrains(map_layer_first['trains'], self.map.graph,
								 self.shortest_path[self.shortest_path.index(is_node[1]) + 1], 1)
			self.server_interation.move(res[0], res[1], res[2])



	def menu(self):
		self.vertical_group_box.setParent(None)
		self.create_vertical_group_box(self.button_logout)
		self.button_layout.addWidget(self.vertical_group_box)

	def sign_in(self):
		data, is_ok = QInputDialog.getText(self, "Sign in", "Input name")
		if is_ok:
			if not self.server_interation:
				self.server_interation = Socket()
			self.menu()
			self.server_interation.login(str(data))
			self.map = Map(self.server_interation.getmap(MapLayer.ZERO_LAYER.value), self.server_interation.getmap(MapLayer.FIRST_LAYER.value))
			self.initial_map()
			self.isSignIn = True

	def logout(self):
		self.figure.clf()
		self.canvas.draw_idle()
		self.server_interation.logout()
		self.isSignIn = False

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())
	def isSign(self):
		return self.isSignIn


if __name__ == '__main__':
	# server = Socket()
	# server.login("Dima")
	# json = server.getmap(MapLayer.FIRST_LAYER.value)
	isFirstSignIn = True
	app = QApplication(sys.argv)
	app.aboutToQuit.connect(app.deleteLater)
	app.setStyle(QStyleFactory.create("gtk"))
	screen = PrettyWidget()

	while True:
		QtWidgets.qApp.processEvents()
		if screen.isSignIn and isFirstSignIn:
			counter = timer()
			isFirstSignIn = False
		if screen.isSignIn and int(timer() - counter) >= TIMEOUT :
			counter = timer()
			screen.update_map()
			#drawMap(screen.graph)
			trains = Parse.parseTrains(screen.trains, screen.map.graph)[0]
			if trains:
				drawTrains(trains)
			print("-----------UPDATED------------")
	screen.show()
	sys.exit(app.exec_())
