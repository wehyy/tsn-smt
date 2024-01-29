import networkx as nx
import random, math
import numpy as np
import configparser
import ast
import os
from logging import Logger
from matplotlib import pyplot as plt

set_dag_size = [10, 20, 30, 40, 50, 60, 70, 80, 90]         # random number of DAG nodes
set_max_out = [1, 2, 3, 4, 5]                               # max out_degree of one node
set_alpha = [0.5, 1.0, 1.5]                                 # DAG shape
set_beta = [0.0, 0.5, 1.0, 2.0]                             # DAG regularity

class Topo():

    def __init__(self):
        pass

    def loadLocalTopo(self, name):
        config_path = os.path.join(os.getcwd(), 'utils/topo_models.ini')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"config file '{config_path}' not exists!")
        
        topo_config = configparser.ConfigParser()
        topo_config.read(config_path)
        nodes = topo_config.get(name, 'nodes')
        self.nodes = ast.literal_eval(nodes)
        edges = topo_config.get(name, 'edges')
        self.edges = ast.literal_eval(edges)

        self.graph = nx.DiGraph()
        # self.graph.add_nodes_from(self.nodes)
        self.graph.add_weighted_edges_from(self.edges)

    def getGraph(self):
        return self.graph
    
    def DAGs_generate(self, mode = 'default', nodes_num = 10, max_out = 2, alpha = 1, beta = 1.0):
        ##############################################initialize############################################
        if mode != 'default':
            nodes_num = random.sample(set_dag_size, 1)[0]
            max_out = random.sample(set_max_out, 1)[0]
            alpha = random.sample(set_alpha, 1)[0]
            beta = random.sample(set_beta, 1)[0]
        
        length = math.floor(math.sqrt(nodes_num)/alpha)
        mean_value = nodes_num/length
        random_numbers = np.random.normal(loc=mean_value, scale=beta, size=length)
        print(random_numbers)
        random_numbers = random_numbers / np.sum(random_numbers) * nodes_num
        random_numbers = np.ceil(random_numbers)
        random_numbers = [int(x) for x in random_numbers]
        diff = int(np.sum(random_numbers)) - nodes_num
        if diff != 0:
            for i in range(diff):
                index = random.randrange(0, length, 1)
                random_numbers[index] -= 1
        print(random_numbers)

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
            print(pred)
            pred += len(dag_list[i])

        ######################################create start node and exit node################################
        for node,id in enumerate(into_degree):#给所有没有入边的节点添加入口节点作父亲
            if id == 0:
                edges.append(('Start',node+1))
                into_degree[node] += 1

        for node,od in enumerate(out_degree):#给所有没有出边的节点添加出口节点作儿子
            if od == 0:
                edges.append((node+1,'Exit'))
                out_degree[node] += 1

        #############################################plot###################################################
        return edges, into_degree, out_degree, position

    def plot_DAG(self, edges, postion):
        g1 = nx.DiGraph()
        g1.add_edges_from(edges)
        nx.draw_networkx(g1, arrows=True, pos=postion)
        plt.show()
        # plt.savefig("DAG.png", format="PNG")
        return plt.clf
