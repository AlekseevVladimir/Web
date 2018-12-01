import networkx as nx
import matplotlib.pyplot as plt
from parse import Parse

class PostType(object):
	TOWN = 1
	MARKET = 2
	STORAGE = 3


#первый слой map json
def define_post_type(map_layer_first):
	town_idx = []
	market_idx = []
	storage_idx = []
	for i in map_layer_first["posts"]:
		if i["type"] == PostType.TOWN:
			town_idx.append(i["point_idx"])
		elif i["type"] == PostType.MARKET:
			market_idx.append(i["point_idx"])
		elif i["type"] == PostType.STORAGE:
			storage_idx.append(i["idx"])
	return town_idx, market_idx, storage_idx

class Map(object):

	def __init__(self, json_map_layer_zero, json_map_layer_first):
		self.graph = Parse.parseMap(json_map_layer_zero[1])
		self.town, self.market, self.storage = define_post_type(json_map_layer_first[1])
		self.without_type = [x for x in self.graph.nodes if not x in self.town
							 if not x in self.market if not x in self.storage]
