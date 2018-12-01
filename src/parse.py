import networkx as nx

class Parse(object):
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