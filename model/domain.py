'''Basic domain class: Flow, Node, Port and TransOperation.
'''

class Base:    
    def __init__(self, id: int) -> None:
        '''An instance with an ID.'''
        self.id = id
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.id})'
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
    
    def __hash__(self) -> int:
        return hash(self.id)


class Flow(Base):

    def __init__(self, id: int) -> None:
        '''Flow Instance'''
        super().__init__(id)


class Node(Base):

    def __init__(self, id: int) -> None:
        '''Node Instance'''
        super().__init__(id)


class Edge(Base):

    def __init__(self, id: int) -> None:
        '''Edge Instance'''
        super().__init__(id)
    

class WeightedEdge(Edge):

    def __init__(self, id: int, pred_node: Node, succ_node: Node, weight: float) -> None:
        super().__init__(id)
        self.__pred_node = pred_node
        self.__succ_node = succ_node
        self.__weight = weight

    @property
    def pred_node(self): return self.__pred_node

    @property
    def succ_node(self): return self.__succ_node

    @property
    def weight(self): return self.__weight


class TransOperation(Base):

    def __init__(self, id: int, flow: Flow, edge: Edge, duration: float) -> Node:
        '''TransOperation Instance

        Args:
            id (int): Operation ID.
            flow (Flow): The flow that this trans operation belonging to.
            edge (Edge): The edge that this trans operation assigned to.
            duration (float): The processing time.
        '''
        super().__init__(id)

        self.__flow = flow
        self.__edge = edge
        self.__duration = duration

    @property
    def flow(self): return self.__flow

    @property
    def edge(self): return self.__edge

    @property
    def duration(self): return self.__duration


class Cloneable:
    def copy(self):
        '''Shallow copy of current instance.        
        https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s12.html
        '''
        # create an empty class inheriting from this class and do nothing when initializing
        class Empty(self.__class__):            
            def __init__(self): pass
        
        # change back to the same class
        newcopy = Empty()
        newcopy.__class__ = self.__class__

        # set same properties
        newcopy.__dict__.update(self.__dict__)

        return newcopy