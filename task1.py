import json
import networkx as nx
import pydot
import matplotlib.pyplot as plt
def main():
	G=nx.Graph();
	print("Enter file name")
	fileName=input()
	data=json.load(open(fileName))
	for i in range(0, len(data["points"])):
		G.add_node(data["points"][i]["idx"])
	for j in range(0, len(data["lines"])):
		G.add_edge(data["lines"][j]["points"][0], data["lines"][j]["points"][1], length=data["lines"][j]["length"])
	pos=nx.spring_layout(G)
	labels=nx.get_edge_attributes(G, 'length')
	nodeSize=200
	nx.draw(G, pos, with_labels=True, nodecolor='r',edge_color='b', node_size=nodeSize, font_size=8)
	nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
	plt.show()
	
if __name__ == '__main__':
    main()