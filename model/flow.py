import networkx as nx
import random
from collections import deque
from model.topo import Topo
from model.domain import (Flow, Node, Edge, TransOperation)


def get_ops(flowlist):
    operations = []
    flow_ops = []
    count = 0
    for flow in flowlist:
        edge_op_temp = {}
        for edge in flow.edges:
            op = TransOperation(count, flow, edge, edge.weight)
            edge_op_temp[edge.id] = op
            count += 1
            operations.append(op)
        for path in flow.paths:
            path_op = [edge_op_temp[edge.id] for edge in path]
            flow_ops.append(path_op)
    return operations, flow_ops


class CoFlow(Flow):

    def __init__(self, id: int, topo: Topo, flow: nx.DiGraph) -> None:
        '''CoFlow Instance'''
        super().__init__(id)
        self.__topo = topo
        self.__flowG = flow
        self.__edges = [topo.get_edge(edge) for edge in flow.edges]
        self.__paths = self.__get_paths()
        self.etv, self.ltv, self.ete, self.lte, self.cp = self.__get_critical_path()
    
    @property
    def edges(self): return self.__edges

    @property
    def graph(self): return self.__flowG
    
    @property
    def paths(self): return self.__paths

    def __get_paths(self):
        graph = self.__flowG
        paths = []
        in_nodes = []
        out_nodes = []
        for node in graph.nodes:
            if graph.in_degree(node) == 0:
                in_nodes.append(node)
            if graph.out_degree(node) == 0:
                out_nodes.append(node)
        for in_node in in_nodes:
            paths += nx.all_simple_edge_paths(graph, in_node, out_nodes[0])
        paths_e = []
        for path in paths:
            paths_e.append([self.__topo.get_edge(edge) for edge in path])
        return paths_e
        
    def __get_critical_path(self):
        graph = self.__flowG
        topoSeq = list(nx.topological_sort(graph))

        # 计算事件的最早开始时间
        vertex_earliest_start = {}

        for node in topoSeq:
            # 如果是起点，最早开始时间为0
            if graph.in_degree(node) == 0:
                vertex_earliest_start[node] = 0
            else:
                # 最早开始时间为前驱节点的最晚完成时间
                vertex_earliest_start[node] = max([vertex_earliest_start[pred] + graph[pred][node]['weight'] for pred in graph.predecessors(node)])
            
        # 计算事件的最晚开始时间
        vertex_latest_start = {}
        for node in topoSeq[::-1]:
            # 如果是终点，事件最晚开始时间等于最早开始时间
            if graph.out_degree(node) == 0:
                vertex_latest_start[node] = vertex_earliest_start[node]
            else:
                # 最晚开始时间为后继节点的最早开始时间减去当前节点的持续时间
                vertex_latest_start[node] = min([vertex_earliest_start[succ] - graph[node][succ]['weight'] for succ in graph.successors(node)])
        
        # 计算活动的最早开始时间和最晚开始时间
        edge_earliest_start = {}
        edge_latest_start = {}
        for edge in self.__edges:
            edge_earliest_start[(edge.pred_node.id, edge.succ_node.id)] = vertex_earliest_start[edge.pred_node.id]
            edge_latest_start[(edge.pred_node.id, edge.succ_node.id)] = vertex_latest_start[edge.succ_node.id] - edge.weight

        # 找到关键路径
        # critical_path = [(u, v) for (u, v) in graph.edges() if edge_earliest_start[(u, v)] == edge_latest_start[(u, v)]]
        critical_path = list(nx.dag_longest_path(graph))

        return vertex_earliest_start, vertex_latest_start, edge_earliest_start, edge_latest_start, critical_path
        
    
class TaskFlowGenerator():

    def __init__(self, topo:Topo):
        self.topo = topo
        self.taskflowList = []
    
    def reloadTopo(self, topo:Topo):
        self.topo = topo

    def flowGenerate(self, nums):
        flowlist = self.getSubGraph(self.topo, nums)
        return flowlist

    def getSubGraph(self, topo: Topo, nums: int):
        sub_graph_list = []
        count = 0
        while count < nums:
            g = topo.graph
            source_list = [node.id for node, ind in zip(topo.nodes, topo.into_degree) if ind == 0]
            destination_list = [node.id for node, outd in zip(topo.nodes, topo.out_degree) if outd == 0]
            selected_src = random.sample(source_list, min(random.randint(1, 3), len(source_list)))
            # 限制源节点为 selected_src 时对应的可选择的目的节点
            alt_dst = set()
            paths = []

            # BFS get all paths with the source within selected_src
            for source in selected_src:
                visited = set()
                queue = deque([source])
                while queue:
                    current_node = queue.popleft()
                    neighbor_edges = g.edges(current_node)
                    neighbor_nodes = [x for x in edges_to_nodes(neighbor_edges) if x != current_node]
                    if current_node not in visited:
                        visited.add(current_node)
                        queue.extend(neighbor_nodes)
                dst = set(destination_list) & visited
                if not alt_dst:
                    alt_dst = dst
                else:
                    alt_dst = alt_dst & dst
                paths.append(list(visited))
            if not alt_dst:
                continue
            # 在所有可选的目的节点中随机选择一个作为唯一目的节点
            dst = random.sample(list(alt_dst), 1)
            
            # 在确定了所有源节点和唯一目的节点之后，再裁减不需要的边
            selected_nodes = set()
            for path in paths:
                visited = set()
                queue = deque(dst)
                while queue:
                    current_node = queue.popleft()
                    neighbor_edges = g.in_edges(current_node)
                    neighbor_nodes = [x for x in edges_to_nodes(neighbor_edges) if x != current_node]
                    neighbor_nodes = set(neighbor_nodes) & set(path)
                    if current_node not in visited:
                        visited.add(current_node)
                        queue.extend(neighbor_nodes)
                if not selected_nodes:
                    selected_nodes = visited
                else:
                    selected_nodes = selected_nodes | visited
            
            sub_g = nx.subgraph(g, selected_nodes)
            sub_graph_list.append(sub_g)
            count += 1
        return sub_graph_list


def edges_to_nodes(edges):
    tmp_g = nx.DiGraph()
    tmp_g.add_edges_from(edges)
    nodes = list(tmp_g.nodes())
    return nodes

def nodes_to_edges(nodes):
    edges = []
    for idx in range(len(nodes)-1):
        edges.append(nodes[idx], nodes[idx+1])
    return edges