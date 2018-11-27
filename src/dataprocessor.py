import networkx as nx
import matplotlib.pyplot as plt


# trains-json_map["trains"] map-граф, содержащий карту
# функция возвращает список вершин, в которые поезд может отправиться в данный момент
def getMoveOptions(trains, trainIdx, map):
	trainIdx = int(trainIdx)
	train = [i for i in trains if trainIdx == i["idx"]][0]
	options = list()
	connectedPoints = map.edges()
	lines = {v: k for k, v in nx.get_edge_attributes(map, "idx").items()}
	length = nx.get_edge_attributes(map, "weight")
	if train["position"] != 0 and train["position"] != length[lines[train["line_idx"]]]:
		options = lines[train["line_idx"]]
	elif train["position"] == 0:
		for i in connectedPoints:
			if lines[train["line_idx"]][0] == i[0]:
				options.append(i[1])
			elif lines[train["line_idx"]][0] == i[1]:
				options.append(i[0])
	else:
		for i in connectedPoints:
			if lines[train["line_idx"]][1] == i[0]:
				options.append(i[1])
			elif lines[train["line_idx"]][1] == i[1]:
				options.append(i[0])
	return options


# trains-json_map["trains"], map-граф, содержащий карту
# targetPoint-точка назначения, trainIdx-индекс выбранного поезда
def moveTrains(trains, map, targetPoint, trainIdx):
	targetPoint = int(targetPoint)
	trainIdx = int(trainIdx)
	train = [i for i in trains if trainIdx == i["idx"]][0]
	lineIdx = train["line_idx"]
	connectedPoints = map.edges()
	lines = {v: k for k, v in nx.get_edge_attributes(map, "idx").items()}
	print("TEST")
	print(train)
	print(lines[train["line_idx"]])
	print(lines)

	print(targetPoint)
	if train["position"] == 0:
		currentPoint = lines[train["line_idx"]][0]
	else:
		currentPoint = lines[train["line_idx"]][1]
	print(currentPoint)
	if targetPoint in lines[train["line_idx"]]:
		print("TEST1")
		if targetPoint == lines[train["line_idx"]][0]:
			speed = -1
		else:
			speed = 1
	else:
		for i in connectedPoints:
			if i[0] == currentPoint and i[1] == targetPoint:
				print("TEST2")
				speed = 1
				lineIdx = map.edges()[currentPoint, targetPoint]["idx"]
				break
			elif i[1] == currentPoint and i[0] == targetPoint:
				print("TEST3")
				speed = -1
				lineIdx = map.edges()[targetPoint, currentPoint]["idx"]
	return lineIdx, speed, train["idx"]


# json_data-нулевой слой карты, функция преобразует карту из формата json в граф, возвращает полученный граф
def parseMap(jsonData):
	graph = nx.Graph()
	graph.add_nodes_from([i['idx'] for i in jsonData['points']])
	graph.add_weighted_edges_from([(i['points'][0], i['points'][1], i['length']) for i in jsonData['lines']])
	valList = dict()
	for i in jsonData["lines"]:
		valList[tuple(i["points"])] = i["idx"]
	nx.set_edge_attributes(graph, valList, "idx")
	pos = nx.spring_layout(graph)
	pos = nx.kamada_kawai_layout(graph, pos=pos)
	valList = dict()
	for i in jsonData["points"]:
		valList[i["idx"]] = pos[i["idx"]]
	nx.set_node_attributes(graph, valList, "pos")
	return graph


# trains-json_map["trains"], map-граф, содержащий карту
# возвращает граф, содержащий поезда и список кнопок для каждого поезда
def parseTrains(trains, map):
	graph = nx.Graph()
	lines = {v: k for k, v in nx.get_edge_attributes(map, "idx").items()}
	length = nx.get_edge_attributes(map, "weight")
	goodstype = {1: "armor", 2: "products", None: "Empty"}
	buttons = list()
	for i in trains:
		string = "Index:" + str(i["idx"]) + "\nGoods:" + str(goodstype[i["goods_type"]])
		if i["goods_type"] != None:
			string += ' ' + str(i["goods"])
		buttons.append(string)
	pos = nx.get_node_attributes(map, "pos")
	if trains:
		vec = [pos[lines[i["line_idx"]][1]] - pos[lines[i["line_idx"]][0]] for i in trains]
		for i in trains:
			trainPos = {
				i["idx"]: [pos[lines[i["line_idx"]][0]] + x / length[tuple(lines[i["line_idx"]])] * i["position"] for x
						   in vec]}
		for i in trains:
			trainPos[i["idx"]] = list(trainPos[i["idx"]][0])
		for i in trains:
			graph.add_node(i["idx"], pos=trainPos[i["idx"]])
		return graph, buttons
	else:
		return 0, buttons


# trains-граф, возвращаемый parseTrains, отрисовывает поезда
def drawTrains(trains):
	NODESIZE = 100
	pos = nx.get_node_attributes(trains, "pos")
	nx.draw(trains, pos, node_color="blue", node_size=NODESIZE)


# map-граф, возвращаемый parseMap, отрисовывает карту
def drawMap(map):
	pos = nx.get_node_attributes(map, "pos")
	labels = nx.get_edge_attributes(map, 'weight')
	NODESIZE = 200
	nx.draw(map, pos, with_labels=True, nodecolor='r', edge_color='b', node_size=NODESIZE, font_size=8)
	nx.draw_networkx_edge_labels(map, pos, edge_labels=labels)