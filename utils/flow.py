import networkx as nx
import numpy as np
from utils.topo import Topo

class TaskGenerator():

    def __init__(self):
        self.taskflowList = []
    
    def loadTopo(self, topo: Topo):
        self.topo = topo
