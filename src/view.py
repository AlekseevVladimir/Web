import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from dataprocessor import parseMap, drawMap, parseTrains, drawTrains, moveTrains, define_post_type
from serverinteraction import Socket
from time import time as timer
from enum import Enum

TIMEOUT = 1


class MapLayer(Enum):
	ZERO_LAYER = 0
	FIRST_LAYER = 1


class PrettyWidget(QWidget):
	def __init__(self):
		super(PrettyWidget, self).__init__()
		self.server_interation = Socket()
		self.button_sign_in = ['sign_in']
		self.button_logout = ['logout']
		#self.buttonOk = ['OK']
		self.graph = None
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
		self.figure.clf()
		response, json_map = self.server_interation.getmap(0)
		if not response:
			self.graph = parseMap(json_map)
			drawMap(self.graph, self.server_interation.getmap(MapLayer.FIRST_LAYER.value))
		response, json_map = self.server_interation.getmap(MapLayer.FIRST_LAYER.value)
		if not response:
			self.trains = json_map["trains"]
			trains, self.train_buttons = parseTrains(json_map["trains"], self.graph)
			if trains:
				drawTrains(trains)
		self.canvas.draw()
		self.canvas.flush_events()

	def update_map(self):
		self.figure.clf()
		drawMap(self.graph, self.server_interation.getmap(MapLayer.FIRST_LAYER.value))
		response, json_map = self.server_interation.getmap(MapLayer.FIRST_LAYER.value)
		if not response:
			self.trains = json_map["trains"]
			trains, self.train_buttons = parseTrains(json_map["trains"], self.graph)
			if trains: drawTrains(trains)
		self.canvas.draw()

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


if __name__ == '__main__':
	# server = Socket()
	# server.login("Dima")
	# json = server.getmap(MapLayer.FIRST_LAYER.value)

	counter = timer()
	app = QApplication(sys.argv)
	app.aboutToQuit.connect(app.deleteLater)
	app.setStyle(QStyleFactory.create("gtk"))
	screen = PrettyWidget()
	while screen.isSignIn:
		QtWidgets.qApp.processEvents()
		if int(timer() - counter) == TIMEOUT:
			counter = timer()
			screen.update_map()
			#drawMap(screen.graph)
			trains = parseTrains(screen.trains, screen.graph)[0]
			if trains:
				drawTrains(trains)
			print("-----------UPDATED------------")
	screen.show()
	sys.exit(app.exec_())
