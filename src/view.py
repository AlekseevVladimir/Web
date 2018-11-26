import sys
import json
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from dataprocessor import parseMap, drawMap, parseTrains, drawTrains, positionNodes
from serverinteraction import Socket
from main import parse
import time


class PrettyWidget(QWidget):

	server = Socket()
	NumButtons = ['signIn', 'logout']

	def __init__(self):
		super(PrettyWidget, self).__init__()
		font = QFont()
		font.setPointSize(16)
		self.initUI()

	def initUI(self):

		self.setGeometry(100, 100, 800, 600)
		self.setMinimumSize(500,300)
		self.center()
		self.setWindowTitle('Graph viewer')

		grid = QGridLayout()
		self.setLayout(grid)
		self.createVerticalGroupBox()

		buttonLayout = QVBoxLayout()
		buttonLayout.addWidget(self.verticalGroupBox)

		self.figure = plt.figure()
		self.canvas = FigureCanvas(self.figure)
		grid.addWidget(self.canvas, 0, 1, 9, 9)
		grid.addLayout(buttonLayout, 0, 0)

		self.show()


	def createVerticalGroupBox(self):
		self.verticalGroupBox = QGroupBox()

		layout = QVBoxLayout()
		for i in  self.NumButtons:
			button = QPushButton(i)
			button.setObjectName(i)
			layout.addWidget(button)
			layout.setSpacing(10)
			self.verticalGroupBox.setLayout(layout)
			button.clicked.connect(self.submitCommand)

	def submitCommand(self):
		eval('self.' + str(self.sender().objectName()) + '()')

	# def big_graph(self):
	# 	self.figure.clf()
	# 	graph2, graph_idx = parse(json.load(open('../test_graphs/big_graph.json')))
	# 	createFigures(graph2, graph_idx)
	# 	self.canvas.draw_idle()
	#
	# def small_graph(self):
	# 	self.figure.clf()
	# 	graph, graph_idx = parse(json.load(open('../test_graphs/small_graph.json')))
	# 	createFigures(graph, graph_idx)
	# 	self.canvas.draw_idle()
	#
	# def custom_graph(self):
	# 	self.figure.clf()
	# 	#graph1, graph_idx = parse(json.load(open('../test_graphs/small_graph.json')))
	# 	#createFigures(graph1, graph_idx)
	# 	graph, graph_idx = parse(json.load(open('../test_graphs/custom_graph.json')))
	# 	createFigures(graph, graph_idx)
	# 	self.canvas.draw_idle()

	def graph_server(self):
		self.figure.clf()
		response, json_map = self.server.getmap(0)
		if not response:
			graph = parseMap(json_map)
			drawMap(graph)
		response, json_map = self.server.getmap(1)
		if not response:
			self.trains = json_map["trains"]
			trains, self.TrainButtons = parseTrains(json_map["trains"], graph)
			if trains: drawTrains(trains)
		self.canvas.draw()
		self.canvas.flush_events()

	def signIn(self):
		data, isOk = QInputDialog.getText(self, "Sign in", "Input name")
		if isOk:
			self.server.login(str(data))
			self.graph_server()

	def logout(self):
		self.figure.clf()
		self.canvas.draw_idle()
		self.server.logout()
		#self.close()


	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.aboutToQuit.connect(app.deleteLater)
	app.setStyle(QStyleFactory.create("gtk"))
	screen = PrettyWidget()

	screen.show()
	sys.exit(app.exec_())
