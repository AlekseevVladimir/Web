import networkx as nx
import matplotlib.pyplot as plt

class PostType(object):
    TOWN = 1
    MARKET = 2
    STORAGE = 3

LOADPERTURN=8
# trains-json_map["trains"] map-граф, содержащий карту
# функция возвращает список вершин, в которые поезд может отправиться в данный момент
#def getMoveOptions(trains, trainIdx, map):
#	print("asd")
#	print(dijkstra_path_length(map, 18, 21))
#	#trainIdx = int(trainIdx)
#	#train = [i for i in trains if trainIdx == i["idx"]][0]
#	#options = list()
#	#connectedPoints = map.edges()
#	#lines = {v: k for k, v in nx.get_edge_attributes(map, "idx").items()}
#	#length = nx.get_edge_attributes(map, "weight")
#	#if train["position"] != 0 and train["position"] != length[lines[train["line_idx"]]]:
#	#	options = lines[train["line_idx"]]
#	#elif train["position"] == 0:
#	#	for i in connectedPoints:
#	#		if lines[train["line_idx"]][0] == i[0]:
#	#			options.append(i[1])
#	#		elif lines[train["line_idx"]][0] == i[1]:
#	#			options.append(i[0])
#	#else:
#	#	for i in connectedPoints:
#	#		if lines[train["line_idx"]][1] == i[0]:
#	#			options.append(i[1])
#	#		elif lines[train["line_idx"]][1] == i[1]:
#	#			options.append(i[0])
#	return options

#def check_trains(map_layer_first, routes, map):
#	trains=map_layer_first["trains"]
#	lineIdx=0
#	speed=0
#	trainIdx=0
#	print("ROUTES")
#	print(routes)
#	if trains[0]["speed"]==0 and routes[1][1]:
#		lineIdx, speed, trainIdx=moveTrains(trains, map, routes[1][1][0], trains[0]["idx"])
#		del routes[1][1][0]
#	elif not routes:
#		lineIdx=-1
#	return lineIdx, speed, trainIdx, routes


#def check_trains(map_layer_first, routes, map, cur_position, waiting_time):
#	trains=map_layer_first["trains"]
#	train=trains[0]
#	lineIdx=0
#	speed=0
#	trainIdx=0
#	if train["speed"]==0 and routes[train["idx"]][1][0]==cur_position[train["idx"]]:
#		lineIdx, speed, trainIdx=moveTrains(trains, map, routes[train["idx"]][1][0], train["idx"])
#		del routes[train["idx"]][1][0]
#	elif not len(routes[train["idx"]][1]) and waiting_time[train["idx"]]:
#		waiting_time[train["idx"]]-=1
#	return lineIdx, speed, trainIdx, routes, waiting_time


def check_trains(map_layer_first, routes, map, waiting_time):
	trains=map_layer_first["trains"]
	train=trains[0]
	lines = {v: k for k, v in nx.get_edge_attributes(map, "idx").items()}
	length = nx.get_edge_attributes(map, "weight")
	for i in map_layer_first["posts"]:
		if i["type"]==PostType.TOWN:
			town=i
	cur_position=dict()
	for i in trains:
		if i["position"]==(length[lines[i["line_idx"]]]):
			cur_position[i["idx"]]=lines[i["line_idx"]][1]
		elif i["position"]==0:
			cur_position[i["idx"]]=lines[i["line_idx"]][0]
		else:
			cur_position[i["idx"]]=-1
	
	lineIdx=0
	speed=0
	trainIdx=0
	print("CURPOS")
	print(waiting_time)
	if routes:
		if len(routes[train["idx"]][1]):
			if train["speed"]==0:
				lineIdx, speed, trainIdx=moveTrains(trains, map, routes[train["idx"]][1][0], train["idx"])
			if routes[train["idx"]][1][0]==cur_position[train["idx"]]:
				del routes[train["idx"]][1][0]
		elif waiting_time[train["idx"]]:
			waiting_time[train["idx"]]-=1
		elif cur_position[train["idx"]]!=town["point_idx"]:
			print("CASE")
			routes= calculate_routes(map_layer_first, map, PostType.TOWN, cur_position)
		else:
			routes=0
	else:
		routes, waiting_time=calculate_priorities(map_layer_first, map, cur_position)
	return lineIdx, speed, trainIdx, routes, waiting_time

def calculate_priorities(map_layer_first, map, cur_position):
	trains=map_layer_first["trains"]
	train=trains[0]
	for i in map_layer_first["posts"]:
		if i["type"]==PostType.TOWN:
			town=i
	routes= calculate_routes(map_layer_first, map, PostType.MARKET, cur_position)
	waiting_time=dict()
	waiting_time[train["idx"]]=0
	food_is_necessary=False
	print(routes)
	consumers=town["population"]
	if town["events"]:
		print(town["events"])
		if town["events"][0]["type"]==3:
			consumers+=town["events"]["parasites_power"]
	waiting_time[train["idx"]]=train["goods_capacity"]//LOADPERTURN
	product_loss=consumers*(routes[1][0]*2+waiting_time[train["idx"]])
	if product_loss >= town["product"]:
		food_is_necessary=True
	print("IIIIII2")
	print(food_is_necessary)
	if not food_is_necessary:
		routes= calculate_routes(map_layer_first, map, PostType.STORAGE, cur_position)
	
	return routes, waiting_time
	
def calculate_routes(map_layer_first, map, target_type, cur_position):
	towns, markets, storages=define_post_type(map_layer_first)
	tmp=map.copy()
	for i in map_layer_first["posts"]:
		if i["type"]==PostType.TOWN:
			town=i
	trains=map_layer_first["trains"]
	routes=dict()
	if target_type!=PostType.TOWN:
		target, cur_position=calculate_target(map_layer_first, map, target_type, cur_position)
		if target_type==PostType.STORAGE:
			for i in markets:
				print("IIIIII2")
				print(i)
				tmp.remove_node(i)
		else:
			for i in storages:
				print("IIIIII")
				print(target_type)
				tmp.remove_node(i)
	else:
		target=town["point_idx"]
	for i in trains:
		routes[i["idx"]]=list(nx.single_source_dijkstra(tmp, cur_position[i["idx"]], target=target))
		routes[i["idx"]][1]=routes[i["idx"]][1][1:]
	return routes
	
def calculate_target(map_layer_first, map, target_type, cur_position):
	lines = {v: k for k, v in nx.get_edge_attributes(map, "idx").items()}
	length = nx.get_edge_attributes(map, "weight")
	trains=map_layer_first["trains"]
	posts=map_layer_first["posts"]
	targets_by_indexes=dict()
	for i in posts:
		if i["type"]==target_type:
			targets_by_indexes[i["point_idx"]]=i
	#print("TEST")
	#print(nx.single_source_dijkstra(map, cur_position, target=16))
	posts=define_post_type(map_layer_first)
	routes=dict()
	prev_profitness=0
	profitness=0
	for i in trains:
		if cur_position[i["idx"]]!=-1:
			for j in posts[target_type-1]:
				if target_type==PostType.MARKET:
					goods_amount=targets_by_indexes[j]["product"]
				else:
					goods_amount=targets_by_indexes[j]["armor"]
				tmp=nx.single_source_dijkstra(map, cur_position[i["idx"]], target=j)
				if tmp[0]:
					profitness=((goods_amount
								+ targets_by_indexes[j]["replenishment"]
								* tmp[0]) 
								/ tmp[0])
				if profitness>prev_profitness:
					#tmp=nx.single_source_dijkstra(map, cur_position, target=j)
					target=j
					prev_profitness=profitness
	#print(routes[i["idx"]][1][1:])
	return target, cur_position
	#train_most_close_point=[x for x in trains if lines[trains["line_idx"]]]

# trains-json_map["trains"], map-граф, содержащий карту
# targetPoint-точка назначения, trainIdx-индекс выбранного поезда
def moveTrains(trains, map, targetPoint, trainIdx):
	targetPoint = int(targetPoint)
	speed=0
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
				i["idx"]: [pos[lines[i["line_idx"]][0]] + x / length[tuple(lines[i["line_idx"]])]
						   * i["position"] for x in vec]}
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
def drawMap(graph, map_layer_first):
	pos = nx.get_node_attributes(graph, "pos")
	#print(map_layer_first)
	#print("POS")
	#print(pos)
	#print("NODES")
	#print(nx.nodes(graph))
	town, market, storage = define_post_type(map_layer_first)
	#print(storage)
	labels = nx.get_edge_attributes(graph, 'weight')
	NODESIZE = 200
	#print(type_posts)
	nx.draw(graph,pos, with_labels=True, node_color='gray', node_size = NODESIZE, font_size= 8)
	nx.draw_networkx_nodes(graph, pos, nodelist=town, node_color='green', node_size=NODESIZE)
	nx.draw_networkx_nodes(graph, pos, nodelist=market, node_color='red', node_size=NODESIZE)
	nx.draw_networkx_nodes(graph, pos, nodelist=storage, node_color='pink', node_size=NODESIZE)
	nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)


#первый слой map json
def define_post_type(map_layer_first):
	#print("testmaplayer")
	#print(map_layer_first)
	town_idx = []
	market_idx = []
	storage_idx = []
	for i in map_layer_first["posts"]:
		if i["type"] == PostType.TOWN:
			town_idx.append(i["point_idx"])
		elif i["type"] == PostType.MARKET:
			market_idx.append(i["point_idx"])
		elif i["type"] == PostType.STORAGE:
			storage_idx.append(i["point_idx"])
	return town_idx, market_idx, storage_idx