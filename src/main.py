import json
import networkx as nx
import matplotlib.pyplot as plt


def parse(json_file):
	graph = nx.Graph()
	graph.add_nodes_from([i['idx'] for i in json_file['points']])
	graph.add_weighted_edges_from([(i['points'][0], i['points'][1], i['length']) for i in json_file['lines']])
	return graph, json_file["idx"]


def createFigures(graph, graph_idx):
	plt.figure(graph_idx)
	pos = nx.spring_layout(graph, iterations=200)
	pos = nx.kamada_kawai_layout(graph, weight=None, pos=pos)
	labels = nx.get_edge_attributes(graph, 'weight')
	nodeSize = 200
	nx.draw(graph, pos, with_labels=True, nodecolor='r', edge_color='b', node_size=nodeSize, font_size=8)
	nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
	
def parseMap(graph):
	pos = nx.kamada_kawai_layout(graph, weight=None)
	labels = nx.get_edge_attributes(graph, 'weight')
	nodeSize = 200
	nx.draw(graph, pos, with_labels=True, nodecolor='r', edge_color='b', node_size=nodeSize, font_size=8)
	nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)


def main():
	while True:
		print("choose graph:\n1:small graph\n2:big graph\n3:custom graph\n4:custom graph 2\n5:custom graph 3\n0 to exit")
		choice=int(input())
		if choice==1:
			graph, graph_idx=parse(json.load(open('test_graphs/small_graph.json')))
			createFigures(graph, graph_idx)
		elif choice==2:
			graph, graph_idx=parse(json.load(open('test_graphs/big_graph.json')))
			createFigures(graph, graph_idx)
		elif choice==3:
			graph, graph_idx=parse(json.load(open('test_graphs/custom_graph.json')))
			createFigures(graph, graph_idx)
		elif choice==4:
			graph, graph_idx=parse(json.load(open('test_graphs/custom_graph2.json')))
			createFigures(graph, graph_idx)
		elif choice==5:
			graph, graph_idx=parse(json.load(open('test_graphs/custom_graph3.json')))
			createFigures(graph, graph_idx)
		elif choice==0:
			break
		plt.show()


if __name__ == '__main__':
	main()