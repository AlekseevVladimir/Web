import json
import networkx as nx
import matplotlib.pyplot as plt
import socket


def parse(json_file):
    graph = nx.Graph();
    graph.add_nodes_from([i['idx'] for i in json_file['points']])
    graph.add_weighted_edges_from([(i['points'][0], i['points'][1], i['length']) for i in json_file['lines']])
    return graph, json_file["idx"]


def createFigures(graph):
    plt.figure(graph[1])
    pos = nx.spring_layout(graph[0])
    labels = nx.get_edge_attributes(graph[0], 'weight')
    nodeSize = 200
    nx.draw(graph[0], pos, with_labels=True, nodecolor='r', edge_color='b', node_size=nodeSize, font_size=8)
    nx.draw_networkx_edge_labels(graph[0], pos, edge_labels=labels)


def main():
    createFigures(parse(json.load(open('Graphs_JSON/small_graph.json'))))
    createFigures(parse(json.load(open('Graphs_JSON/big_graph.json'))))
    createFigures(parse(json.load(open('Graphs_JSON/custom_graph.json'))))
    createFigures(parse(json.load(open('Graphs_JSON/custom_graph2.json'))))
    createFigures(parse(json.load(open('Graphs_JSON/custom_graph3.json'))))
    plt.show()
    # SERVER_ADDR = 'wgforge-srv.wargaming.net'
    # SERVER_PORT = 443
    # sock = socket.socket()
    # sock.connect((SERVER_ADDR,SERVER_PORT))
    # sock.send(1)
    # print(sock.recv(4))
    # sock.close


if __name__ == '__main__':
    main()