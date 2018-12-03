import networkx as nx
import matplotlib.pyplot as plt
from map import Map



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


# trains-граф, возвращаемый parseTrains, отрисовывает поезда
def drawTrains(trains):
	NODESIZE = 100
	pos = nx.get_node_attributes(trains, "pos")
	nx.draw(trains, pos, node_color="blue", node_size=NODESIZE)


# map-граф, возвращаемый parseMap, отрисовывает карту
def drawMap(graph, town, market, storage):
	pos = nx.get_node_attributes(graph, "pos")
	labels = nx.get_edge_attributes(graph, 'weight')
	NODESIZE = 200
	nx.draw(graph,pos, with_labels=True, node_color='gray', node_size = NODESIZE, font_size= 8)
	nx.draw_networkx_nodes(graph, pos, nodelist=town, node_color='green', node_size=NODESIZE)
	nx.draw_networkx_nodes(graph, pos, nodelist=market, node_color='red', node_size=NODESIZE)
	nx.draw_networkx_nodes(graph, pos, nodelist=storage, node_color='pink', node_size=NODESIZE)
	nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)

def position_is_node(edges_idx, edges_weight, line_idx, position):
	start = None
	end = None
	idx = None
	weight = None
	for k,v in edges_idx:
		if v == line_idx:
			start, end = k
			break
	for k,v in edges_weight:
		if k == (start, end):
			weight = v
			break
	if position == 0:
		return (True, start)
	elif position == weight:
		return (True, end)
	else:
		return (False, -1)