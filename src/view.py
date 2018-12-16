import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from dataprocessor import WorldMap, define_post_type, check_trains, parse_trains, draw_trains
from serverinteraction import Socket
from time import time as timer
from enum import Enum
TICK=0
TIMEOUT = 2


class MapLayer(Enum):
	ZERO_LAYER = 0
	FIRST_LAYER = 1


class PrettyWidget(QWidget):
	TICK=0
	def __init__(self):
		super(PrettyWidget, self).__init__()
		self.server_interaction = Socket()
		self.button_sign_in = ['sign_in']
		self.button_logout = ['logout']
		self.routes=0
		#self.buttonOk = ['OK']
		self.graph = None
		self.initialised=False
		self.trains = None
		self.isSignIn = False
		self.waiting_time=0
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

		
	def update_map(self):
		self.figure.clf()
		response_one, map_layer_one = self.server_interaction.getmap(MapLayer.FIRST_LAYER.value)
		#print(map_layer_one)
		if not self.initialised:
			response_zero, map_layer_zero = self.server_interaction.getmap(MapLayer.ZERO_LAYER.value)
			if not response_zero and not response_one:
				self.WorldMap = WorldMap(map_layer_zero, map_layer_one)
				self.initialised=True
		self.WorldMap.draw_map()
		
		response, self.this_player=self.server_interaction.player()
		#print(self.this_player["town"])
		line_idx, speed, self.routes=check_trains(
					map_layer_one, self.routes, self.WorldMap, self.waiting_time, self.this_player)
					
		
		#print(self.this_player["town"])
		for train in self.this_player["trains"]:
			if train["idx"] in line_idx.keys():
				self.server_interaction.move(line_idx[train["idx"]], speed[train["idx"]], train["idx"])
		self.TICK+=1
		if not response_one:
			#print(self.TICK)
			trains = parse_trains(map_layer_one["trains"], self.WorldMap)
			if trains: 
				draw_trains(trains)
		self.canvas.draw()
		self.server_interaction.next_turn()

	def menu(self):
		self.vertical_group_box.setParent(None)
		self.create_vertical_group_box(self.button_logout)
		self.button_layout.addWidget(self.vertical_group_box)

	def sign_in(self):
		data, is_ok = QInputDialog.getText(self, "Sign in", "Input name")
		if is_ok:
			if not self.server_interaction:
				self.server_interaction = Socket()
			self.menu()
			self.server_interaction.login(str(data))
			self.update_map()
			self.isSignIn = True

	def logout(self):
		self.figure.clf()
		self.canvas.draw_idle()
		self.server_interaction.logout()
		self.isSignIn = False

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())


if __name__ == '__main__':

	counter = timer()
	app = QApplication(sys.argv)
	app.aboutToQuit.connect(app.deleteLater)
	app.setStyle(QStyleFactory.create("gtk"))
	screen = PrettyWidget()
	while True:
		QtWidgets.qApp.processEvents()
		if int(timer() - counter) >= TIMEOUT and screen.isSignIn:
			counter = timer()
			screen.update_map()
			print("-----------UPDATED------------")
	screen.show()
	sys.exit(app.exec_())

	
	
	
	
