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

TIMEOUT = 10


class MapLayer(Enum):
	ZERO_LAYER = 0
	FIRST_LAYER = 1


class PrettyWidget(QWidget):
	def __init__(self):
		super(PrettyWidget, self).__init__()
		self.server_interation = Socket()
		self.button_sign_in = ['sign_in']
		self.buttons_authorized_user = ['logout', 'move_train', 'upgrade', 'player']
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

	def move_train(self):

		self.vertical_group_box.setParent(None)
		self.text_vertex = QLabel()
		self.text_vertex.setText('Выберите вершину')
		self.button_layout.addWidget(self.text_vertex)
		self.vertex_combo_box = QComboBox()
		for i in getMoveOptions(self.trains, 1, self.graph):
			self.vertex_combo_box.addItem(str(i))
		self.button_layout.addWidget(self.vertex_combo_box)

		self.text_train = QLabel()
		self.text_train.setText('Выберите поезд')
		self.button_layout.addWidget(self.text_train)
		self.train_combo_box = QComboBox()
		for i in self.trains:
			count = 1
			self.train_combo_box.addItem(str(count))
			count = count + 1
		self.button_layout.addWidget(self.train_combo_box)
		self.create_vertical_group_box(self.buttonOk)
		self.button_layout.addWidget(self.vertical_group_box)

	# outputVertex- вершина выбранная пользователем,outputTrain - (индекс поезда-1) в массиве trains выбранный пользователем
	def OK(self):
		output_vertex = self.vertex_combo_box.currentText()
		output_train = self.train_combo_box.currentText()
		self.train_combo_box.setParent(None)
		self.vertex_combo_box.setParent(None)
		self.train_combo_box.setParent(None)
		self.vertex_combo_box.setParent(None)
		self.text_train.setParent(None)
		self.text_vertex.setParent(None)
		#print(output_vertex)
		#print(output_train)
		line_idx, speed, train_idx = moveTrains(self.trains, self.graph, int(output_vertex), int(output_train))
		#print(line_idx, speed, train_idx)
		self.server_interation.move(int(line_idx), int(speed), int(train_idx))
		self.menu()


	def logout(self):
		self.figure.clf()
		self.canvas.draw_idle()
		self.server_interation.logout()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())


if __name__ == '__main__':
	timeout = TIMEOUT
	counter = timer()
	app = QApplication(sys.argv)
	app.aboutToQuit.connect(app.deleteLater)
	app.setStyle(QStyleFactory.create("gtk"))
	screen = PrettyWidget()
	while True:
		QtWidgets.qApp.processEvents()
		if int(timer() - counter) == timeout:
			counter = timer()
			screen.update_map()
			draw_map(screen.graph)
			trains = parseTrains(screen.trains, screen.graph)[0]
			if trains:
				drawTrains(trains)
			print("-----------UPDATED------------")
	screen.show()
	sys.exit(app.exec_())
