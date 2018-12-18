import networkx as nx
import matplotlib.pyplot as plt

class PostType(object):
    TOWN = 1
    MARKET = 2
    STORAGE = 3

LOADPERTURN=8

class WorldMap(object):
	def __init__(self, map_layer_zero, map_layer_one):
		self.lines=dict()
		self.lines_connected_to_points=dict()
		self.lines_length=dict()
		self.parse_map(map_layer_zero, map_layer_one)
		
	
	def parse_map(self, map_layer_zero, map_layer_one):
		self.graph = nx.Graph()
		self.graph.add_nodes_from([i['idx'] for i in map_layer_zero['points']])
		self.graph.add_weighted_edges_from([(i['points'][0], 
										i['points'][1], i['length']) 
										for i in map_layer_zero['lines']])
		for i in map_layer_zero["lines"]:
			if i["points"][0] in self.lines_connected_to_points.keys():
				self.lines_connected_to_points[i["points"][0]].append(i["idx"])
			else:
				self.lines_connected_to_points[i["points"][0]]=list()
				self.lines_connected_to_points[i["points"][0]].append(i["idx"])
			if i["points"][1] in self.lines_connected_to_points.keys():
				self.lines_connected_to_points[i["points"][1]].append(i["idx"])
			else:
				self.lines_connected_to_points[i["points"][1]]=list()
				self.lines_connected_to_points[i["points"][1]].append(i["idx"])
			self.lines[i["idx"]]=i["points"]
			self.lines_length[i["idx"]]=i["length"]
		pos = nx.spring_layout(self.graph)
		self.pos = nx.kamada_kawai_layout(self.graph, pos=pos, weight=None)
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

	



def check_upgrades(this_player, Map):
	trains=this_player["trains"]
	town=this_player["town"]
	res=town["armor"]
	cur_position=dict()
	trains_list=list()
	for i in trains:
		if i["position"]==(Map.lines_length[i["line_idx"]]):
			cur_position[i["idx"]]=Map.lines[i["line_idx"]][1]
		elif i["position"]==0:
			cur_position[i["idx"]]=Map.lines[i["line_idx"]][0]
		else:
			cur_position[i["idx"]]=-1
	posts_list=list()
	for train in trains:
		if train["next_level_price"]<=(res-40) and train["idx"]<=3 and train["level"]!=3 and train["level"]<=town["level"] and cur_position[train["idx"]]==town["point_idx"]:
			res-=train["next_level_price"]
			trains_list.append(train["idx"])
	if (res-40)>=town["next_level_price"]:
		res-=town["next_level_price"]
		posts.append(town["idx"])
	for train in trains:
		if train["next_level_price"]<=(res-40) and train["level"]!=3 and train["level"]<=town["level"] and cur_position[train["idx"]]==town["point_idx"]:
			res-=train["next_level_price"]
			trains_list.append(train["idx"])
	
	return posts_list, trains_list
	
		
def check_trains(map_layer_one, routes, Map, waiting_time, this_player):
	trains=map_layer_one["trains"]
	my_trains=this_player["trains"]
	
	town=this_player["town"]
	posts=map_layer_one["posts"]
	cur_position=dict()
	for i in my_trains:
		if i["position"]==(Map.lines_length[i["line_idx"]]):
			cur_position[i["idx"]]=Map.lines[i["line_idx"]][1]
		elif i["position"]==0:
			cur_position[i["idx"]]=Map.lines[i["line_idx"]][0]
		else:
			cur_position[i["idx"]]=-1
	line_idx=dict()
	speed=dict()
	trains_on_line=dict()
	for train in trains:
		if not (train["line_idx"] in trains_on_line.keys()):
			trains_on_line[train["line_idx"]]=list()
			
		trains_on_line[train["line_idx"]].append(train)
			
	if not routes:
		routes=dict()
		
			
	
		
	for train in my_trains:
		if train["idx"] in routes:
			if routes[train["idx"]][1][0]==cur_position[train["idx"]]:
				del routes[train["idx"]][1][0]
			if not len(routes[train["idx"]][1]) or cur_position[train["idx"]]==town["point_idx"]:
				del routes[train["idx"]]
				
		
	
	for train in my_trains:
		if not (train["idx"] in routes.keys()) or cur_position[train["idx"]]!=-1:
			routes, waiting_time=calculate_priorities(train, trains, posts, 
														Map, cur_position[train["idx"]], 
														routes, line_idx, town, trains_on_line)
		
			if train["idx"]in routes.keys() and not (train["idx"] in speed.keys()):
				line_idx[train["idx"]], speed[train["idx"]]=move_trains(train, 
																	Map, routes[train["idx"]][1][0], 
																train["idx"], cur_position[train["idx"]])
	for train in my_trains: 
		if (train["position"]==(Map.lines_length[train["line_idx"]]-1) or
						(train["position"]==1)):
			flag=False
			for i in Map.lines_connected_to_points[routes[train["idx"]][1][0]]:
				if i in trains_on_line.keys() and i!=train["line_idx"]:
					for j in trains_on_line[i]:
						if (j["speed"]==1 and j["position"]==Map.lines_length[j["line_idx"]]-1
											and Map.lines[j["line_idx"]][1]==routes[train["idx"]][1][0]
													or j["speed"]==-1 and j["position"]==1
													and Map.lines[j["line_idx"]][0]==routes[train["idx"]][1][0]):
							if not (j["idx"] in speed.keys()):
								flag=True								
								speed[train["idx"]]=0
								line_idx[train["idx"]]=train["line_idx"]
			if flag==False and train["speed"]==0:
				if train["position"]==1:
					speed[train["idx"]]=-1
					line_idx[train["idx"]]=train["line_idx"]
				elif train["position"]==(Map.lines_length[train["line_idx"]]-1):
					speed[train["idx"]]=1
					line_idx[train["idx"]]=train["line_idx"]
	
	for train in my_trains:
		if train["line_idx"] in trains_on_line.keys() and cur_position[train["idx"]]==-1:
			
			for i in trains_on_line[train["line_idx"]]:
				if not (train["idx"] in speed.keys()):
					speed[train["idx"]]=train["speed"]
				if not (i["idx"] in speed.keys()):
					speed[i["idx"]]=i["speed"]
						
				if (i["position"]==train["position"] + speed[train["idx"]] and cur_position[i["idx"]]==-1 and
											speed[train["idx"]]!=speed[i["idx"]] and i["idx"]!=train["idx"] and cur_position[i["idx"]]==-1):
					speed[train["idx"]]=speed[i["idx"]]
					line_idx[train["idx"]]=train["line_idx"]
				elif speed[train["idx"]]==0 and train["speed"]==0:
					if i["position"]==train["position"]+1 and speed[i["idx"]]!=0 and cur_position[i["idx"]]==-1:
						
						speed[train["idx"]]=speed[i["idx"]]
						line_idx[train["idx"]]=train["line_idx"]
					elif i["position"]==train["position"]-1 and speed[i["idx"]]!=0 and cur_position[i["idx"]]==-1:
						
						speed[train["idx"]]=speed[i["idx"]]
						line_idx[train["idx"]]=train["line_idx"]
						
	
	return line_idx, speed, routes
		
		
		
	

	
	
def calculate_priorities(train, trains, posts, Map, cur_position, routes, line_idx, town, trains_on_line):
	
	if cur_position != town["point_idx"] and (not (train["idx"] in routes.keys()) 
									or train["goods"]==train["goods_capacity"]):

		buf=calculate_routes(train, trains, posts, Map, PostType.TOWN, cur_position, 
													line_idx, town, trains_on_line)
		if buf:
			routes[train["idx"]]=buf
		return routes, 0
	elif train["goods_type"]==3:
		buf= calculate_routes(train, trains, posts, Map, PostType.STORAGE, 
							cur_position, line_idx, town, trains_on_line)
		if buf:
			routes[train["idx"]]=buf
		return routes, 0
	
	buf= calculate_routes(train, trains, posts, Map, PostType.MARKET, 
						cur_position, line_idx, town, trains_on_line)
	if buf:
		routes[train["idx"]]=buf
		if train["idx"]<=4:
			return routes, 0
	else:
		return routes, 0
	waiting_time=dict()
	waiting_time[train["idx"]]=0
	consumers=town["population"]
	if town["events"]:
		if town["events"][0]["type"]==3:
			consumers+=town["events"]["parasites_power"]
	waiting_time[train["idx"]]=0
	if routes[train["idx"]]:
		product_loss=consumers*((routes[train["idx"]][0] 
		+ nx.shortest_path_length(Map.graph, source=routes[train["idx"]][1][-1],
		target=town["point_idx"]))+waiting_time[train["idx"]]+25)
	
		if product_loss >= town["product"]:
			return routes, waiting_time
	tmp=routes.copy()
	buf= calculate_routes(train, trains, posts, Map, PostType.STORAGE, cur_position, line_idx, town, trains_on_line)
	if buf:
		routes[train["idx"]]=buf
	else:
		return routes, 0
	if routes[train["idx"]]:
		product_loss=consumers*((routes[train["idx"]][0] 
		+ nx.shortest_path_length(Map.graph, source=routes[train["idx"]][1][-1],
		target=town["point_idx"]))+waiting_time[train["idx"]]+15)
		if product_loss >= town["product"]:
			return tmp, waiting_time
	return routes, waiting_time
	
	
	
def calculate_routes(train, trains, posts, Map, target_type, cur_position, line_idx, town, trains_on_line):
	towns, markets, storages=define_post_type(posts)
	tmp=Map.graph.copy()
	
	if cur_position==town["point_idx"]:
		if town["point_idx"]==Map.lines[Map.lines_connected_to_points[town["point_idx"]][1]][0]:
			second_point=Map.lines[Map.lines_connected_to_points[town["point_idx"]][1]][1]
			
			if (town["point_idx"], second_point) in tmp.edges():
				tmp.remove_edge(town["point_idx"], second_point)
		else:
			second_point=Map.lines[Map.lines_connected_to_points[town["point_idx"]][1]][0]
			if (second_point, town["point_idx"]) in tmp.edges():
				tmp.remove_edge(second_point, town["point_idx"])
	
	for i in line_idx.values():
		if tuple(Map.lines[i]) in tmp.edges() or tuple(Map.lines[i][::-1]) in tmp.edges():
			tmp.remove_edge(Map.lines[i][0], Map.lines[i][1])
	
	for i in Map.lines_connected_to_points[cur_position]:
		if i in trains_on_line.keys():
			for j in trains_on_line[i]:
				if cur_position!=town["point_idx"] and (cur_position==Map.lines[i][0] and j["speed"]!=1 and j["position"]!=Map.lines_length[j["line_idx"]]  ##проблема либо столкновения, либо не выезжают из города
				or cur_position==Map.lines[i][1] and j["speed"]!=-1 and j["position"]!=0):
					if tuple(Map.lines[i]) in tmp.edges():
						tmp.remove_edge(Map.lines[i][0], Map.lines[i][1])
					elif tuple(Map.lines[i][-1:0]) in tmp.edges():
						tmp.remove_edge(Map.lines[i][1], Map.lines[i][0])
	
	if target_type!=PostType.TOWN:
		target=calculate_target(train, trains, posts, tmp, target_type, cur_position)
		if target_type==PostType.STORAGE:
			for i in markets:
				tmp.remove_node(i)
		else:
			for i in storages:
				tmp.remove_node(i)
	else:
		if town["point_idx"]==Map.lines[Map.lines_connected_to_points[town["point_idx"]][0]][0]:
			second_point=Map.lines[Map.lines_connected_to_points[town["point_idx"]][0]][1]
			if (town["point_idx"], second_point) in tmp.edges():
				tmp.remove_edge(town["point_idx"], second_point)
		else:
			second_point=Map.lines[Map.lines_connected_to_points[town["point_idx"]][0]][0]
			if (second_point, town["point_idx"]) in tmp.edges():
				tmp.remove_edge(second_point, town["point_idx"])
		
		target=town["point_idx"]
	if target==-1:
		return 0
	if nx.has_path(tmp, cur_position, target):
		routes=list(nx.single_source_dijkstra(tmp, cur_position, target=target))
	else:
		routes=0
	
	if routes:
		routes[1]=routes[1][1:]
	
	return routes
	
	
	
def calculate_target(train, trains, posts, graph, target_type, cur_position):
	targets_by_indexes=dict()
	for i in posts:
		if i["type"]==target_type:
			targets_by_indexes[i["point_idx"]]=i
	posts=define_post_type(posts)
	prev_profitness=0
	profitness=0
	tmp=-1
	target=-1
	for j in posts[target_type-1]:
		if target_type==PostType.MARKET:
			goods_amount=targets_by_indexes[j]["product"]
		else:
			goods_amount=targets_by_indexes[j]["armor"]
		if nx.has_path(graph, cur_position, j):
			tmp=nx.single_source_dijkstra(graph, cur_position, target=j)
		else:
			continue
		if tmp[0]:
			goods_amount = goods_amount + targets_by_indexes[j]["replenishment"] * tmp[0]
			if goods_amount>train["goods_capacity"]:
				goods_amount=train["goods_capacity"]
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
		for i in Map.lines.items():
			if i[1] == [cur_position, target_point]:
				speed = 1
				line_idx = i[0]
				break
			elif i[1] == [target_point, cur_position]:
				speed = -1
				line_idx = i[0]
				break
	return line_idx, speed
	
	
	
def parse_trains(trains, Map):
	graph = nx.Graph()
	train_pos=dict()
	if trains:
		
		for i in trains:
			vec = (Map.pos[Map.lines[i["line_idx"]][1]] 
				- Map.pos[Map.lines[i["line_idx"]][0]])
			train_pos[i["idx"]] = (Map.pos[Map.lines[i["line_idx"]][0]] + vec
				/ Map.lines_length[i["line_idx"]]
				* i["position"])
		for i in trains:
			train_pos[i["idx"]] = list(train_pos[i["idx"]])
		for i in trains:
			graph.add_node(i["idx"], pos=train_pos[i["idx"]])
		return graph
	else:
		return 0


		
def draw_trains(trains):
	NODESIZE = 100
	pos = nx.get_node_attributes(trains, "pos")
	nx.draw(trains, pos, node_color="blue", node_size=NODESIZE)


	
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