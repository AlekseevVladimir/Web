import networkx as nx
import matplotlib.pyplot as plt

<<<<<<< HEAD
class PostType(object):
    TOWN = 1
    MARKET = 2
    STORAGE = 3
=======
>>>>>>> upstream/master

LOADPERTURN=8
class WorldMap(object):
	def __init__(self, map_layer_zero, map_layer_one):
		self.lines=dict()
		self.lines_length=dict()
		self.parse_map(map_layer_zero, map_layer_one)
		
	
	def parse_map(self, map_layer_zero, map_layer_one):
		self.graph = nx.Graph()
		self.graph.add_nodes_from([i['idx'] for i in map_layer_zero['points']])
		self.graph.add_weighted_edges_from([(i['points'][0], 
										i['points'][1], i['length']) 
										for i in map_layer_zero['lines']])
		for i in map_layer_zero["lines"]:
			self.lines[i["idx"]]=i["points"]
			self.lines_length[i["idx"]]=i["length"]
		pos = nx.spring_layout(self.graph)
		self.pos = nx.kamada_kawai_layout(self.graph, pos=pos)
		town, market, storage = define_post_type(map_layer_one["posts"])
		points_idx=list(self.pos.keys())
		self.color_Map=list()
		for i in points_idx:
			if i in town:
				self.color_Map.append("green")
			elif i in market:
				self.color_Map.append("red")
			elif i in storage:
				self.color_Map.append("pink")
			else:
				self.color_Map.append("gray")
	
	
	def draw_map(self):
		labels = nx.get_edge_attributes(self.graph, 'weight')
		NODESIZE = 200
		nx.draw(self.graph, self.pos, with_labels=True, node_color=self.color_Map, 
				node_size = NODESIZE, font_size= 8)
		nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=labels)

<<<<<<< HEAD
		
		
def check_trains(map_layer_one, routes, Map, waiting_time):
	trains=map_layer_one["trains"]
	train=trains[0]
	posts=map_layer_one["posts"]
	for i in posts:
		if i["type"]==PostType.TOWN:
			town=i
	cur_position=dict()
	for i in trains:
		if i["position"]==(Map.lines_length[i["line_idx"]]):
			cur_position[i["idx"]]=Map.lines[i["line_idx"]][1]
		elif i["position"]==0:
			cur_position[i["idx"]]=Map.lines[i["line_idx"]][0]
		else:
			cur_position[i["idx"]]=-1
	line_idx=0
	speed=0
	train_idx=0
	print(routes)
	if routes:
		if routes[train["idx"]][1][0]==cur_position[train["idx"]]:
			del routes[train["idx"]][1][0]
			if not len(routes[train["idx"]][1]):
				if cur_position[train["idx"]]!=town["point_idx"]:
					routes= calculate_routes(trains, posts, Map, PostType.TOWN, cur_position)
				else:
					routes, waiting_time=calculate_priorities(trains, posts, Map, cur_position)
		line_idx, speed, train_idx=move_trains(train, Map, routes[train["idx"]][1][0], 
											train["idx"], cur_position[train["idx"]])
	else:
		print("5")
		routes, waiting_time=calculate_priorities(trains, posts, Map, cur_position)
		line_idx, speed, train_idx=move_trains(train, Map, routes[train["idx"]][1][0], 
											train["idx"], cur_position[train["idx"]])	
	return line_idx, speed, train_idx, routes, waiting_time

	
	
def calculate_priorities(trains, posts, Map, cur_position):
	train=trains[0]
	for i in posts:
		if i["type"]==PostType.TOWN:
			town=i
	routes= calculate_routes(trains, posts, Map, PostType.MARKET, cur_position)
	waiting_time=dict()
	waiting_time[train["idx"]]=0
	food_is_necessary=False
	consumers=town["population"]
	if town["events"]:
		if town["events"][0]["type"]==3:
			consumers+=town["events"]["parasites_power"]
	waiting_time[train["idx"]]=0
	product_loss=consumers*(routes[1][0]*2+waiting_time[train["idx"]])
	if product_loss+10 >= town["product"]:
		return routes, waiting_time
	tmp=routes.copy()
	routes= calculate_routes(trains, posts, Map, PostType.STORAGE, cur_position)
	product_loss+=consumers*(routes[train["idx"]][0]*2+waiting_time[train["idx"]])
	if product_loss+10 >= town["product"]:
		return tmp, waiting_time
	return routes, waiting_time
	
	
	
def calculate_routes(trains, posts, Map, target_type, cur_position):
	towns, markets, storages=define_post_type(posts)
	tmp=Map.graph.copy()
	for i in posts:
		if i["type"]==PostType.TOWN:
			town=i
	routes=dict()
	if target_type!=PostType.TOWN:
		target=calculate_target(trains, posts, Map, target_type, cur_position)
		if target_type==PostType.STORAGE:
			for i in markets:
				tmp.remove_node(i)
		else:
			for i in storages:
				tmp.remove_node(i)
=======
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
>>>>>>> upstream/master
	else:
		target=town["point_idx"]
	for i in trains:
		routes[i["idx"]]=list(nx.single_source_dijkstra(tmp, cur_position[i["idx"]], target=target))
		routes[i["idx"]][1]=routes[i["idx"]][1][1:]
	return routes
	
	
	
def calculate_target(trains, posts, Map, target_type, cur_position):
	targets_by_indexes=dict()
	for i in posts:
		if i["type"]==target_type:
			targets_by_indexes[i["point_idx"]]=i
	posts=define_post_type(posts)
	prev_profitness=0
	profitness=0
	for i in trains:
		for j in posts[target_type-1]:
			if target_type==PostType.MARKET:
				goods_amount=targets_by_indexes[j]["product"]
			else:
				goods_amount=targets_by_indexes[j]["armor"]
			tmp=nx.single_source_dijkstra(Map.graph, cur_position[i["idx"]], target=j)
			if tmp[0]:
				goods_amount = goods_amount + targets_by_indexes[j]["replenishment"] * tmp[0]
				if goods_amount>i["goods_capacity"]:
					goods_amount=i["goods_capacity"]
				profitness=goods_amount / tmp[0]
			if profitness>prev_profitness:
				target=j
				prev_profitness=profitness
	return target

	
	
def move_trains(train, Map, target_point, train_idx, cur_position):
	target_point = int(target_point)
	train_idx = int(train_idx)
	line_idx = train["line_idx"]
	if target_point in Map.lines[train["line_idx"]]:
		if target_point == Map.lines[train["line_idx"]][0]:
			speed = -1
		else:
			speed = 1
	else:
<<<<<<< HEAD
		for i in Map.lines.items():
			if i[1] == [cur_position, target_point]:
				speed = 1
				line_idx = i[0]
				break
			elif i[1] == [target_point, cur_position]:
				speed = -1
				line_idx = i[0]
				break
	return line_idx, speed, train["idx"]
	
	
	
def parse_trains(trains, Map):
	graph = nx.Graph()
	if trains:
		vec = [Map.pos[Map.lines[i["line_idx"]][1]] 
				- Map.pos[Map.lines[i["line_idx"]][0]] for i in trains]
		for i in trains:
			train_pos = {
				i["idx"]: [Map.pos[Map.lines[i["line_idx"]][0]] + vec[0] 
				/ Map.lines_length[i["line_idx"]]
				* i["position"]]}
=======
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
>>>>>>> upstream/master
		for i in trains:
			train_pos[i["idx"]] = list(train_pos[i["idx"]][0])
		for i in trains:
			graph.add_node(i["idx"], pos=train_pos[i["idx"]])
		return graph
	else:
		return 0


		
def draw_trains(trains):
	NODESIZE = 100
	pos = nx.get_node_attributes(trains, "pos")
	nx.draw(trains, pos, node_color="blue", node_size=NODESIZE)


<<<<<<< HEAD
	
def define_post_type(posts):
	town_idx = []
	market_idx = []
	storage_idx = []
	for i in posts:
		if i["type"] == PostType.TOWN:
			town_idx.append(i["point_idx"])
		elif i["type"] == PostType.MARKET:
			market_idx.append(i["point_idx"])
		elif i["type"] == PostType.STORAGE:
			storage_idx.append(i["point_idx"])
	return town_idx, market_idx, storage_idx
=======
# map-граф, возвращаемый parseMap, отрисовывает карту
def drawMap(map):
	pos = nx.get_node_attributes(map, "pos")
	labels = nx.get_edge_attributes(map, 'weight')
	NODESIZE = 200
	nx.draw(map, pos, with_labels=True, nodecolor='r', edge_color='b', node_size=NODESIZE, font_size=8)
	nx.draw_networkx_edge_labels(map, pos, edge_labels=labels)
>>>>>>> upstream/master
