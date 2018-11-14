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
    pos = nx.spring_layout(graph)
    labels = nx.get_edge_attributes(graph, 'weight')
    nodeSize = 200
    nx.draw(graph, pos, with_labels=True, nodecolor='r', edge_color='b', node_size=nodeSize, font_size=8)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)


def main():
	graph, graph_idx=parse(json.load(open('Graphs_JSON/small_graph.json')))
	createFigures(graph, graph_idx)
	graph, graph_idx=parse(json.load(open('Graphs_JSON/big_graph.json')))
	createFigures(graph, graph_idx)
	graph, graph_idx=parse(json.load(open('Graphs_JSON/custom_graph.json')))
	createFigures(graph, graph_idx)
	graph, graph_idx=parse(json.load(open('Graphs_JSON/custom_graph2.json')))
	createFigures(graph, graph_idx)
	graph, graph_idx=parse(json.load(open('Graphs_JSON/custom_graph3.json')))
	createFigures(graph, graph_idx)
	plt.show()


if __name__ == '__main__':
    main()