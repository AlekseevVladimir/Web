import networkx as nx
from dataprocessor import position_is_node, moveTrains
from map import Map, PostType

class ManageAction(object):
	def __init__(self, map):
		self.map = map
	#for now work with one train
	def update_info(self, map_layer_first):
		self.train_info = []
		self.train_info.append(map_layer_first["trains"][0])
		self.town_info = []
		self.market_info = []
		self.storage_info = []
		for item in map_layer_first['posts']:
			if item['type'] == PostType.TOWN:
				self.town_info.append(item)
			elif item['type'] == PostType.MARKET:
				self.market_info.append(item)
			else:
				self.storage_info.append(item)
	def update_action(self, map_layer_first):
		self.update_info(map_layer_first)

		is_node = position_is_node(nx.get_edge_attributes(self.map.graph, "idx").items(),
								   nx.get_edge_attributes(self.map.graph, "weight").items()
								   , self.train_info[0]['line_idx'],
								   self.train_info[0]['position'])

		if is_node[0]:
			type_node = self.map.define_type_node(is_node[1])
			if type_node == PostType.TOWN:
				list_shortest_path = []
				list_shortest_path_length = []
				list_product_market = []
				for i in range(len(self.market_info)):
					list_shortest_path.append(nx.shortest_path(self.map.graph
								,source=self.map.town[0],target=self.map.market[i]))
					list_shortest_path_length.append(nx.shortest_path_length(
						self.map.graph, source=self.map.town[0],
						target=self.map.market[i]))
					list_product_market.append(self.market_info[i]["product"])
				index_eff_way = self.calculated_efficiency_way(list_shortest_path_length,
															   list_product_market)
				#need index_eff as index_way but edges doesn't work
				self.shortest_path = list_shortest_path[2]
			elif type_node == PostType.MARKET:
				self.shortest_path = self.shortest_path[::-1]
			index_target_point = self.shortest_path.index(is_node[1])+1
			print(self.shortest_path)
			target_point = self.shortest_path[index_target_point]
			return moveTrains(self.train_info,self.map.graph, target_point,1)
		else:
			return False



	def calculated_efficiency_way(self, list_shortest_path_length, list_product_market):
		max_value = -1
		max_index = -1
		for i in range(len(list_product_market)):
			if list_product_market[i]/list_shortest_path_length[i] > max_value:
				max_value = list_product_market[i]/list_shortest_path_length[i]
				max_index = i
		return max_index

