import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from dataprocessor import WorldMap, parseTrains, drawTrains, moveTrains, define_post_type, calculate_priorities, check_trains
from serverinteraction import Socket
from time import time as timer
from enum import Enum
TICK=0
TIMEOUT = 6


class MapLayer(Enum):
	ZERO_LAYER = 0
	FIRST_LAYER = 1


class PrettyWidget(QWidget):
	TICK=0
	def __init__(self):
		super(PrettyWidget, self).__init__()
		self.server_interation = Socket()
		self.button_sign_in = ['sign_in']
		self.button_logout = ['logout']
		self.routes=0
		#self.buttonOk = ['OK']
		self.graph = None
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

	def initial_map(self):
		self.figure.clf()
		response, json_map = self.server_interation.getmap(0)
		if not response:
			response, json_map1 = self.server_interation.getmap(MapLayer.FIRST_LAYER.value)
			self.WorldMap = WorldMap(json_map, json_map1)
			
		if not response:
			self.trains = json_map1["trains"]
			trains = parseTrains(json_map1["trains"], self.WorldMap)
			if trains:
				drawTrains(trains)
		self.canvas.draw()
		self.canvas.flush_events()

	def update_map(self):
		self.figure.clf()
		response, json_map = self.server_interation.getmap(MapLayer.FIRST_LAYER.value)
		print(json_map["posts"][0])
		self.WorldMap.drawMap()
		lineIdx, speed, trainIdx, self.routes, self.waiting_time=check_trains(json_map, self.routes, self.WorldMap, self.waiting_time)
		if lineIdx:
			self.server_interation.move(lineIdx, speed, trainIdx)
		self.TICK+=1
		if not response:
			self.trains = json_map["trains"]
			
			print(self.trains)
			print(self.TICK)
			trains = parseTrains(json_map["trains"], self.WorldMap)
			if trains: 
				drawTrains(trains)
		self.canvas.draw()
		self.server_interation.nextTurn()

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


def main():
	# server = Socket()
	# server.login("Dima")
	# json = server.getmap(MapLayer.FIRST_LAYER.value)

	counter = timer()
	app = QApplication(sys.argv)
	app.aboutToQuit.connect(app.deleteLater)
	app.setStyle(QStyleFactory.create("gtk"))
	screen = PrettyWidget()
	while True:
		#print(int(timer() - counter))
		QtWidgets.qApp.processEvents()
		if int(timer() - counter) >= TIMEOUT and screen.isSignIn:
			counter = timer()
			screen.update_map()
			#drawMap(screen.graph)
		#	trains = parseTrains(screen.trains, screen.graph)[0]
			#if trains:
			#	drawTrains(trains)
			print("-----------UPDATED------------")
	screen.show()
	sys.exit(app.exec_())

	
	
	
	
#if __name__ == '__main__':
#	timeout = TIMEOUT
#	counter = timer()
#	app = QApplication(sys.argv)
#	app.aboutToQuit.connect(app.deleteLater)
#	app.setStyle(QStyleFactory.create("gtk"))
#	screen = PrettyWidget()
#	while True:
#		QtWidgets.qApp.processEvents()
#		if int(timer() - counter) == timeout:
#			counter = timer()
#			screen.update_map()
#			drawMap(screen.graph)
#			trains = parseTrains(screen.trains, screen.graph)[0]
#			if trains:
#				drawTrains(trains)
#			print("-----------UPDATED------------")
#	screen.show()
#	sys.exit(app.exec_())
#