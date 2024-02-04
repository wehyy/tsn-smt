import networkx as nx
import numpy as np
import random
from utils.topo import Topo

class TaskGenerator():

    def __init__(self):
        self.taskflowList = []
    
    def loadTopo(self, topo: Topo):
        self.topo = topo

    def getSubGraph(self, topo: Topo):
        g = topo.graph
        source_list = [node for node, ind in zip(topo.nodes, topo.into_degree) if ind == 0]
        destination_list = [node for node, outd in zip(topo.nodes, topo.out_degree) if outd == 0]
        selected_src = random.sample(source_list, min(random.randint(1, 3), len(source_list)))
        selected_dst = random.sample(destination_list, 1)
        selected_nodes = list(selected_src)
        curr_nodes = list(selected_src)
        while True:
            if selected_dst in selected_nodes:
                break
            curr_edges = g.edges(curr_nodes)
            next_hop_nodes = [x for x in self._edges_to_nodes(curr_edges) if x not in curr_nodes]
            selected_nodes += next_hop_nodes
            curr_nodes = next_hop_nodes


        pass

    def _edges_to_nodes(self, edges):
        tmp_g = nx.DiGraph()
        tmp_g.add_edges_from(edges)
        nodes = list(tmp_g.nodes())
        return nodes

def edges_to_nodes(edges):
    tmp_g = nx.DiGraph()
    tmp_g.add_edges_from(edges)
    nodes = list(tmp_g.nodes())
    return nodes