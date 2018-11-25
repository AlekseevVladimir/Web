import networkx as nx
import matplotlib.pyplot as plt

def parseMap(map):
	graph=nx.Graph()
	graph.add_nodes_from([i['idx'] for i in map['points']])
	graph.add_weighted_edges_from([(i['points'][0], i['points'][1], i['length']) for i in map['lines']])
	pos=nx.spring_layout(graph)
	pos=nx.kamada_kawai_layout(graph, pos=pos)
	return graph, pos, map["lines"]
	
	
def parseTrains(trains, pos, lines):
	graph=nx.Graph()
	buf=list()
	print("\n")
	print(trains)
	goodstype={1:"armor", 2:"products", None:"Empty"}
	buttons=list()
	for i in trains:
		string="Index:"+str(i["idx"])+"\nGoods:"+str(goodstype[i["goods_type"]])
		if i["goods_type"]!=None:
			string+=' '+str(i["goods"])
		buttons.append(string)
	print(buttons)
	linesWTrains=0
	for i in trains:
		if i["position"]!=0:
			linesWTrains=[x for x in lines if x["idx"]==i["line_idx"]]
			buf.append(i)
	trains=buf
	if trains:
		vec=[pos[x["points"][1]]-pos[x["points"][0]] for x in linesWTrains]
		for i in trains:
			trainPos={i["idx"]:[pos[y["points"][0]]+x/lines[i["line_idx"]]["length"]*i["position"] for x in vec
			for y in linesWTrains if i["line_idx"]==y["idx"]]}
		for i in trains:
			trainPos[i["idx"]]=list(trainPos[i["idx"]][0])
		for i in trains:
			graph.add_node(i["idx"], pos=trainPos[i["idx"]])
		return graph, buttons
	else:
		return 0, buttons
	#graph.add_nodes_from([(i["idx"], "pos"=1) for i in trains])
	
def drawTrains(trains):
	pos=nx.get_node_attributes(trains, "pos")
	nx.draw(trains, pos, node_color="blue", node_size=100)
	
def drawMap(graph, pos):
	labels = nx.get_edge_attributes(graph, 'weight')
	nodeSize = 200
	nx.draw(graph, pos, with_labels=True, nodecolor='r', edge_color='b', node_size=nodeSize, font_size=8)
	nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
	
	