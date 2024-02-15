import networkx as nx
import numpy as np
import random, math, json
import configparser
import ast
import os
from collections import defaultdict
from logging import Logger
from matplotlib import pyplot as plt
from model.domain import (Node, Edge, WeightedEdge)

set_dag_size = [10, 20, 30, 40, 50, 60, 70, 80, 90]         # random number of DAG nodes
set_max_out = [1, 2, 3, 4, 5]                               # max out_degree of one node
set_alpha = [0.5, 1.0, 1.5]                                 # DAG shape
set_beta = [0.0, 0.5, 1.0, 2.0]                             # DAG regularity

class Topo():

    def __init__(self, weighted:bool=True, nodenums:int=30):
        self._nodes = []
        self._edges = []
        self._graph = nx.DiGraph()
        self._into_degree = []
        self._out_degree = []
        self._position = []
        self._nodenums = nodenums

        if weighted:
            self.initRandomWeightedTopo()
        else:
            self.initRandomTopo()


    @property
    def graph(self): return self._graph

    @property
    def edges(self): return self._edges

    @property
    def nodes(self): return self._nodes

    @property
    def into_degree(self): return self._into_degree

    @property
    def out_degree(self): return self._out_degree

    @property
    def position(self): return self._position


    def initRandomTopo(self):
        self._nodes = [Node(i) for i in range(1, self._nodenums + 1)]
        _edges, self._into_degree, self._out_degree, self._position = self.__generate__DAG(nodes_num=self._nodenums, max_out=4, alpha=1.2, beta=2.0)
        self._graph.add_edges_from(_edges)
        edges = []
        for id, _edge in enumerate(_edges):
            edge = WeightedEdge(id, Node(_edge[0]), Node(_edge[1]), 0)
            edges.append(edge)
        self._edges = edges
            
        
    def initRandomWeightedTopo(self):
        self._nodes = [Node(i) for i in range(1, self._nodenums + 1)]
        _edges, self._into_degree, self._out_degree, self._position = self.__generate__DAG(nodes_num=self._nodenums, max_out=4, alpha=1.2, beta=2.0)
        _edges, self._graph = self.__edge_random_weight(_edges)
        edges = []
        for id, _edge in enumerate(_edges):
            edge = WeightedEdge(id, Node(_edge[0]), Node(_edge[1]), _edge[2])
            edges.append(edge)
        self._edges = edges


    def plotTopo(self):
        nx.draw_networkx(self._graph, arrows=True, pos=self._position)
        plt.show()
        return plt.clf
    
    
    def saveTopo(self, name:str):
        # benchmark path
        script_path = os.path.abspath(__file__)
        prj_path = os.path.dirname(os.path.dirname(script_path))
        benchmark_path = os.path.join(prj_path, 'benchmark')
        topo_path = os.path.join(benchmark_path, f'topos/dag{str(self._nodenums)}{name}')

        topo_details = defaultdict(list)
        topo_details["nodes"] = list(self.graph.nodes)
        topo_details["edges"] = list(self.graph.edges(data=True))
        topo_details["positon"] = self.position
        topo_details["into_degree"] = self.into_degree
        topo_details["out_degree"] = self.out_degree

        with open(topo_path, 'w') as f:
            json.dump(topo_details, f, indent=4)


    # def loadTopo(self, name:str):
    #     # benchmark path
    #     script_path = os.path.abspath(__file__)
    #     prj_path = os.path.dirname(os.path.dirname(script_path))
    #     benchmark_path = os.path.join(prj_path, 'benchmark')

    #     config_path = os.path.join(os.getcwd(), 'utils/topo_models.ini')
    #     if not os.path.exists(config_path):
    #         raise FileNotFoundError(f"config file '{config_path}' not exists!")
        
    #     topo_config = configparser.ConfigParser()
    #     topo_config.read(config_path)
    #     nodes = topo_config.get(name, 'nodes')
    #     self.nodes = ast.literal_eval(nodes)
    #     edges = topo_config.get(name, 'edges')
    #     self.edges = ast.literal_eval(edges)

    #     self.graph = nx.DiGraph()
    #     # self.graph.add_nodes_from(self.nodes)
    #     self.graph.add_weighted_edges_from(self.edges)

    
    def get_edge(self, raw_edge):
        for edge in self._edges:
            if edge.pred_node.id == raw_edge[0] and edge.succ_node.id == raw_edge[1]:
                return edge

    
    def __generate__DAG(self, mode:str='default', 
                            nodes_num:int=10, 
                            max_out:int=10, 
                            alpha:int=1, 
                            beta:int=1.0):
        ##############################################initialize############################################
        if mode != 'default':
            nodes_num = random.sample(set_dag_size, 1)[0]
            max_out = random.sample(set_max_out, 1)[0]
            alpha = random.sample(set_alpha, 1)[0]
            beta = random.sample(set_beta, 1)[0]
        
        length = math.floor(math.sqrt(nodes_num)/alpha)
        mean_value = nodes_num/length
        random_numbers = np.random.normal(loc=mean_value, scale=beta, size=length)
        # print(random_numbers)
        random_numbers = random_numbers / np.sum(random_numbers) * nodes_num
        random_numbers = np.ceil(random_numbers)
        random_numbers = [int(x) for x in random_numbers]
        diff = int(np.sum(random_numbers)) - nodes_num
        if diff != 0:
            for i in range(diff):
                index = random.randrange(0, length, 1)
                random_numbers[index] -= 1
        # print(random_numbers)
        ###############################################division#############################################
        # 用于定位
        position = {'start': (0, 4), 'Exit': (10, 4)}
        dag_list = []
        dag_num = 1
        pos = 1
        max_pos = 0
        for i in range(length):
            dag_list.append(list(range(dag_num, dag_num + random_numbers[i])))
            dag_num += random_numbers[i]
            pos = 1
            for j in dag_list[i]:
                position[j] = (3*(i+1), pos)
                pos += 5
            max_pos = pos if pos > max_pos else max_pos
        position['Start'] = (0, max_pos/2)
        position['Exit'] = (3*(length+1), max_pos/2)

        ############################################link#####################################################
        into_degree = [0] * nodes_num
        out_degree = [0] * nodes_num
        edges = []
        pred = 0
        for i in range(length-1):
            sample_list = list(range(len(dag_list[i+1])))
            for j in range(len(dag_list[i])):
                od = random.randrange(1, max_out+1, 1)
                od = len(dag_list[i+1]) if len(dag_list[i+1]) < od else od
                bridge = random.sample(sample_list, od)
                for k in bridge:
                    edges.append((dag_list[i][j], dag_list[i+1][k]))
                    if pred + len(dag_list[i]) + k > len(into_degree):
                        raise ValueError(f'len(into_degree): {len(into_degree)}, {pred + len(dag_list[i]) + k}')
                    into_degree[pred + len(dag_list[i]) + k] += 1
                    out_degree[pred + j] += 1
            # print(pred)
            pred += len(dag_list[i])
        
        repair_nodes = [node for node, ind, outd in zip(list(range(1, nodes_num+1)), into_degree, out_degree) if ind == 0 and outd == 0]
        if repair_nodes:
            for node in repair_nodes:
                repair_list = [node for node in dag_list[length-2] if out_degree[node-1] <= max_out]
                repair_bridge = random.sample(repair_list, 1)[0]
                edges.append((repair_bridge, node))
                into_degree[node-1] += 1
                out_degree[repair_bridge-1] += 1

        return edges, into_degree, out_degree, position

    def __add_start_exit_node(self):
        for node, id in enumerate(self.into_degree):#给所有没有入边的节点添加入口节点作父亲
            if id == 0:
                self.edges.append(('Start',node+1))
                self.into_degree[node] += 1

        for node, od in enumerate(self.out_degree):#给所有没有出边的节点添加出口节点作儿子
            if od == 0:
                self.edges.append((node+1,'Exit'))
                self.out_degree[node] += 1
    
    def __edge_random_weight(self, edges):
        lower, upper = 10, 50
        weighted_edges = []
        for edge in edges:
            weight = random.randint(lower, upper)
            weighted_edge = (edge[0], edge[1], weight)
            weighted_edges.append(weighted_edge)
        weighted_graph = nx.DiGraph()
        weighted_graph.add_weighted_edges_from(weighted_edges)
        return weighted_edges, weighted_graph