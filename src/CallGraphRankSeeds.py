from collections import OrderedDict
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import matplotlib.pyplot as plt
import networkx as nx
import json
import time
import os

inputFolder = 'data'
start_node = 'page_rank_entry_node'
dotFile = 'output/function-rank.dot'
seedsFile = 'data/funcs'
resultFolder = 'output'


def read(project):
    with open(os.path.join(inputFolder, project) + '.json') as readFile, open(seedsFile) as seeds:
        data = json.load(readFile)
        criticalFuncs = set(seeds.read().splitlines())
        return data, criticalFuncs


def draw_call_graph_plt(callGraph, vec):
    nodes = callGraph.nodes()
    colors = [vec[n] for n in nodes]
    pos = nx.spring_layout(callGraph)
    # plt.figure(figsize=(50, 30))
    ec = nx.draw_networkx_edges(callGraph, pos, alpha=0.2)
    nc = nx.draw_networkx_nodes(callGraph, pos, node_color=colors,
                                with_labels=True, node_size=100, cmap=plt.cm.jet)
    plt.colorbar(nc)
    plt.axis('off')
    plt.show()


def draw_call_graph2dot(callGraph):
    write_dot(callGraph, dotFile)


def main(project):
    start_time = time.time()
    print project + " starts."
    data, critical_function_set = read(project)
    callees = set(data.keys())
    callers = reduce((lambda x, key: (x | set(data[key]))), data.keys(), set())
    functions = callers | callees
    print "function number: " + str(len(functions))
    # critical function set that in call graph(set intersection)
    critical_functions = critical_function_set & functions
    print "seed function number: " + str(len(critical_functions))
    # build graph
    callGraph = nx.DiGraph()
    for function in data:
        for caller in data[function]:
            callGraph.add_edge(function, caller)
    # add entry node as start node and exit node
    for entry in callees - callers:
        if entry in critical_functions:
            callGraph.add_edge(start_node, entry)
    # for exit in callers - callees:
    for exit in functions:
        callGraph.add_edge(exit, start_node)
    vec = nx.pagerank(callGraph, alpha=0.85)
    vec = OrderedDict(sorted(vec.items(), key=lambda t: -t[1]))
    elapsed_time = time.time() - start_time
    print "Analyze time: " + str(elapsed_time)
    with open(os.path.join(resultFolder, project) + '.json', 'w') as pageRankFile:
        json.dump(vec, pageRankFile, indent=4)
    draw_call_graph_plt(callGraph, vec)


if __name__ == '__main__':
    projects = ['gzip', 'vim-xxd', 'curl', 'wget', 'nginx']
    for project in projects:
        main(project)
