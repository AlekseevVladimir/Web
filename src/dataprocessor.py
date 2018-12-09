import networkx as nx
import matplotlib.pyplot as plt

class PostType(object):
    TOWN = 1
    MARKET = 2
    STORAGE = 3

LOADPERTURN=8
class WorldMap(object):
	def __init__(self, Map_layer_zero, Map_layer_one):
		self.lines=dict()
		self.lines_length=dict()
		self.parse_Map(Map_layer_zero, Map_layer_one)
		self.drawMap()
		
	
	def parse_Map(self, Map_layer_zero, Map_layer_one):
		self.graph = nx.Graph()
		self.graph.add_nodes_from([i['idx'] for i in Map_layer_zero['points']])
		self.graph.add_weighted_edges_from([(i['points'][0], 
										i['points'][1], i['length']) 
										for i in Map_layer_zero['lines']])
		for i in Map_layer_zero["lines"]:
			self.lines[i["idx"]]=i["points"]
			self.lines_length[i["idx"]]=i["length"]
		pos = nx.spring_layout(self.graph)
		self.pos = nx.kamada_kawai_layout(self.graph, pos=pos)
		town, market, storage = define_post_type(Map_layer_one)
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
	
	def drawMap(self):
		labels = nx.get_edge_attributes(self.graph, 'weight')
		NODESIZE = 200
		nx.draw(self.graph, self.pos, with_labels=True, node_color=self.color_Map, node_size = NODESIZE, font_size= 8)
		nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=labels)

def check_trains(Map_layer_first, routes, Map, waiting_time):
	trains=Map_layer_first["trains"]
	train=trains[0]
	for i in Map_layer_first["posts"]:
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
	
	lineIdx=0
	speed=0
	trainIdx=0
	print(routes)
	if routes:
		if routes[train["idx"]][1][0]==cur_position[train["idx"]]:
			del routes[train["idx"]][1][0]
			if len(routes[train["idx"]][1]):
				lineIdx, speed, trainIdx=moveTrains(trains, Map, routes[train["idx"]][1][0], train["idx"])
			elif cur_position[train["idx"]]!=town["point_idx"]:
				routes= calculate_routes(Map_layer_first, Map, PostType.TOWN, cur_position)
				lineIdx, speed, trainIdx=moveTrains(trains, Map, routes[train["idx"]][1][0], train["idx"])
			else:
				routes, waiting_time=calculate_priorities(Map_layer_first, Map, cur_position)
				lineIdx, speed, trainIdx=moveTrains(trains, Map, routes[train["idx"]][1][0], train["idx"])	
	else:
		print("5")
		routes, waiting_time=calculate_priorities(Map_layer_first, Map, cur_position)
		lineIdx, speed, trainIdx=moveTrains(trains, Map, routes[train["idx"]][1][0], train["idx"])	
	return lineIdx, speed, trainIdx, routes, waiting_time

def calculate_priorities(Map_layer_first, Map, cur_position):
	trains=Map_layer_first["trains"]
	train=trains[0]
	for i in Map_layer_first["posts"]:
		if i["type"]==PostType.TOWN:
			town=i
	routes= calculate_routes(Map_layer_first, Map, PostType.MARKET, cur_position)
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
	routes= calculate_routes(Map_layer_first, Map, PostType.STORAGE, cur_position)
	product_loss+=consumers*(routes[train["idx"]][0]*2+waiting_time[train["idx"]])
	if product_loss+10 >= town["product"]:
		return tmp, waiting_time
	return routes, waiting_time
	
def calculate_routes(Map_layer_first, Map, target_type, cur_position):
	towns, markets, storages=define_post_type(Map_layer_first)
	tmp=Map.graph.copy()
	for i in Map_layer_first["posts"]:
		if i["type"]==PostType.TOWN:
			town=i
	trains=Map_layer_first["trains"]
	routes=dict()
	if target_type!=PostType.TOWN:
		target=calculate_target(Map_layer_first, Map, target_type, cur_position)
		if target_type==PostType.STORAGE:
			for i in markets:
				tmp.remove_node(i)
		else:
			for i in storages:
				tmp.remove_node(i)
	else:
		target=town["point_idx"]
	for i in trains:
		routes[i["idx"]]=list(nx.single_source_dijkstra(tmp, cur_position[i["idx"]], target=target))
		routes[i["idx"]][1]=routes[i["idx"]][1][1:]
	return routes
	
def calculate_target(Map_layer_first, Map, target_type, cur_position):
	trains=Map_layer_first["trains"]
	posts=Map_layer_first["posts"]
	targets_by_indexes=dict()
	for i in posts:
		if i["type"]==target_type:
			targets_by_indexes[i["point_idx"]]=i
	posts=define_post_type(Map_layer_first)
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

	
def test(Map_layer_first, Map):
	towns, markets, storages=define_post_type(Map_layer_first)
	market_routes=dict()
	storage_routes=dict()
	
	
	
# trains-json_Map["trains"], Map-граф, содержащий карту
# targetPoint-точка назначения, trainIdx-индекс выбранного поезда
def moveTrains(trains, Map, targetPoint, trainIdx):
	targetPoint = int(targetPoint)
	speed=0
	trainIdx = int(trainIdx)
	train = [i for i in trains if trainIdx == i["idx"]][0]
	lineIdx = train["line_idx"]
	if train["position"] == 0:
		currentPoint = Map.lines[train["line_idx"]][0]
	else:
		currentPoint = Map.lines[train["line_idx"]][1]
	if targetPoint in Map.lines[train["line_idx"]]:
		if targetPoint == Map.lines[train["line_idx"]][0]:
			speed = -1
		else:
			speed = 1
	else:
		for i in Map.lines.items():
			if i[1] == [currentPoint, targetPoint]:
				speed = 1
				lineIdx = i[0]
				break
			elif i[1] == [targetPoint, currentPoint]:
				speed = -1
				lineIdx = i[0]
				break
	return lineIdx, speed, train["idx"]


# json_data-нулевой слой карты, функция преобразует карту из формата json в граф, возвращает полученный граф



# trains-json_Map["trains"], Map-граф, содержащий карту
# возвращает граф, содержащий поезда и список кнопок для каждого поезда
def parseTrains(trains, Map):
	graph = nx.Graph()
	#lines = {v: k for k, v in nx.get_edge_attributes(Map, "idx").items()}
	#length = nx.get_edge_attributes(Map, "weight")
	if trains:
		vec = [Map.pos[Map.lines[i["line_idx"]][1]] - Map.pos[Map.lines[i["line_idx"]][0]] for i in trains]
		for i in trains:
			trainPos = {
				i["idx"]: [Map.pos[Map.lines[i["line_idx"]][0]] + vec[0] 
				/ Map.lines_length[i["line_idx"]]
				* i["position"]]}
		for i in trains:
			trainPos[i["idx"]] = list(trainPos[i["idx"]][0])
		for i in trains:
			graph.add_node(i["idx"], pos=trainPos[i["idx"]])
		return graph
	else:
		return 0


# trains-граф, возвращаемый parseTrains, отрисовывает поезда
def drawTrains(trains):
	NODESIZE = 100
	pos = nx.get_node_attributes(trains, "pos")
	nx.draw(trains, pos, node_color="blue", node_size=NODESIZE)


# Map-граф, возвращаемый parseMap, отрисовывает карту



#первый слой Map json
def define_post_type(Map_layer_first):
	town_idx = []
	market_idx = []
	storage_idx = []
	for i in Map_layer_first["posts"]:
		if i["type"] == PostType.TOWN:
			town_idx.append(i["point_idx"])
		elif i["type"] == PostType.MARKET:
			market_idx.append(i["point_idx"])
		elif i["type"] == PostType.STORAGE:
			storage_idx.append(i["point_idx"])
	return town_idx, market_idx, storage_idx