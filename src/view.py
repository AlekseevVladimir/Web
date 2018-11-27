import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from dataprocessor import parseMap, draw_map, parseTrains, drawTrains, moveTrains
from serverinteraction import Socket
from dataprocessor import getMoveOptions
from time import time as timer
from enum import Enum


class MapLayer(Enum):
	ZERO_LAYER = 0
	FIRST_LAYER = 1


class PrettyWidget(QWidget):
	def __init__(self):
		super(PrettyWidget, self).__init__()
		self.server_interation = Socket()
		self.button_sign_in = ['sign_in']
		self.buttons_authorized_user = ['logout', 'Move', 'upgrade', 'player']
		self.buttonOk = ['OK']
		self.graph = None
		self.trains = None
		self.train_buttons = None
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
			draw_map(self.graph)
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
		draw_map(self.graph)
		response, json_map = self.server_interation.getmap(MapLayer.FIRST_LAYER.value)
		if not response:
			self.trains = json_map["trains"]
			trains, self.train_buttons = parseTrains(json_map["trains"], self.graph)
			if trains: drawTrains(trains)
		self.canvas.draw()

	def menu(self):
		self.vertical_group_box.setParent(None)
		self.create_vertical_group_box(self.buttons_authorized_user)
		self.button_layout.addWidget(self.vertical_group_box)

	def sign_in(self):
		data, is_ok = QInputDialog.getText(self, "Sign in", "Input name")
		if is_ok:
			if not self.server_interation:
				self.server_interation = Socket()
			self.menu()
			self.server_interation.login(str(data))
			self.initial_map()

	def Move(self):

		self.vertical_group_box.setParent(None)
		self.textVertex = QLabel()
		self.textVertex.setText('Выберите вершину')
		self.button_layout.addWidget(self.textVertex)
		self.vertexComboBox = QComboBox()
		for i in getMoveOptions(self.trains, 1, self.graph):
			self.vertexComboBox.addItem(str(i))
		self.button_layout.addWidget(self.vertexComboBox)

		self.textTrain = QLabel()
		self.textTrain.setText('Выберите поезд')
		self.button_layout.addWidget(self.textTrain)
		self.trainComboBox = QComboBox()
		for i in self.trains:
			count = 1
			self.trainComboBox.addItem(str(count))
			count = count + 1
		self.button_layout.addWidget(self.trainComboBox)
		self.create_vertical_group_box(self.buttonOk)
		self.button_layout.addWidget(self.vertical_group_box)

	# outputVertex- вершина выбранная пользователем,outputTrain - (индекс поезда-1) в массиве trains выбранный пользователем
	def OK(self):
		outputVertex = self.vertexComboBox.currentText()
		outputTrain = self.trainComboBox.currentText()
		self.trainComboBox.setParent(None)
		self.vertexComboBox.setParent(None)
		self.trainComboBox.setParent(None)
		self.vertexComboBox.setParent(None)
		self.textTrain.setParent(None)
		self.textVertex.setParent(None)
		print(outputVertex)
		print(outputTrain)
		lineIdx, speed, trainIdx = moveTrains(self.trains, self.graph, int(outputVertex), int(outputTrain))
		print(lineIdx, speed, trainIdx)
		self.server_interation.move(int(lineIdx), int(speed), int(trainIdx))
		self.menu()


	def logout(self):
		self.figure.clf()
		self.canvas.draw_idle()
		self.server_interation.logout()

	# self.close()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())


if __name__ == '__main__':
	timeout = 10
	counter = timer()
	app = QApplication(sys.argv)
	app.aboutToQuit.connect(app.deleteLater)
	app.setStyle(QStyleFactory.create("gtk"))
	screen = PrettyWidget()
	while True:
		QtWidgets.qApp.processEvents()
		# print(timer() - counter)
		if int(timer() - counter) == timeout:
			counter = timer()
			# print("asd")
			screen.update_map()
			draw_map(screen.graph)
			# print(screen.trains)
			trains = parseTrains(screen.trains, screen.graph)[0]
			print(trains)
			if trains:
				drawTrains(trains)
	screen.show()

	sys.exit(app.exec_())
