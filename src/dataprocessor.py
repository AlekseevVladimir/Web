import networkx as nx
import matplotlib.pyplot as plt

def parsemap(map):
	graph=nx.Graph()
	graph.add_nodes_from([i['idx'] for i in map['points']])
	graph.add_weighted_edges_from([(i['points'][0], i['points'][1], i['length']) for i in map['lines']])
	pos=nx.spring_layout(graph)
	pos=nx.kamada_kawai_layout(graph, pos=pos)
	return graph, pos, map["lines"]
	
	
def parsetrains(trains, pos, lines):
	graph=nx.Graph()
	for i in trains:
		linesWTrains=[x for x in lines if x["idx"]==i["line_idx"]]
	vec=[pos[x["points"][1]]-pos[x["points"][0]] for x in linesWTrains]
	for i in trains:
		trainPos={i["idx"]:[pos[y["points"][0]]+x/lines[i["line_idx"]]["length"]*i["position"] for x in vec
		for y in linesWTrains if i["line_idx"]==y["idx"]]}
	for i in trains:
		trainPos[i["idx"]]=list(trainPos[i["idx"]][0])
	for i in trains:
		graph.add_node(i["idx"], pos=trainPos[i["idx"]])
	return graph
	
def drawTrains(trains):
	pos=nx.get_node_attributes(trains, "pos")
	nx.draw(trains, pos, node_color="blue", node_size=100)
	
	