'''Variable of CoFlow Schedule problem, connecting Operation instance and associated 
variables to solve, i.e. the sequence of operations assigned in same edge.
'''

from .domain import (Base, TransOperation)
from jsp_fwk.model.variable import (Step, JobStep, MachineStep, OperationStep)

class Step(Base):
    
    def __init__(self, source:Base=None) -> None:
        '''A wrapper of domain instance.

        Args:
            source (Base): The domain instance, e.g. Flow, Edge or TransOperation.
        '''
        super().__init__(source.id if source else -1)

        # the source object
        self.__source = source    

    @property
    def source(self): return self.__source

    @property
    def end_time(self) -> float:
        '''The time when a step is completed. For the first job step or machine step, 
        it's 0 by default, i.e. start immediately.
        '''
        return 0.0

class FlowStep(Step):

    def __init__(self, source: Base = None) -> None:
        '''An operation step in flow(job) chain. 
        
        NOTE: the flow itself is wrapped as a FlowStep and is the first step in job chain.
        '''
        super().__init__(source=source)
        # pre-defined flow chain
        self.__pre_flow_op = None    # type: FlowStep
        self.__next_flow_op = None   # type: TransOperationStep
    
    @property
    def pre_flow_op(self): return self.__pre_flow_op

    @property
    def next_flow_op(self): return self.__next_flow_op

    @pre_flow_op.setter
    def pre_flow_op(self, op):
        self.__pre_flow_op = op
        if hasattr(op, 'next_flow_op'): op.__next_flow_op = self

    
class EdgeStep(Step):
    
    def __init__(self, source:Base=None) -> None:
        '''An operation step in edge(machine) chain.
        
        NOTE: the edge itself is wrapped as a EdgeStep and is the first step 
        in edge chain.
        '''
        super().__init__(source=source)
        # edge chain to solve
        self.__pre_edge_op = None    # type: EdgeStep
        self.__next_edge_op = None   # type: TransOperationStep
    
    @property
    def pre_edge_op(self): return self.__pre_edge_op

    @property
    def next_edge_op(self): return self.__next_edge_op

    @pre_edge_op.setter
    def pre_edge_op(self, op):
        self.__pre_edge_op = op
        if hasattr(op, 'next_edge_op'): op.__next_edge_op = self
    
    @property
    def tailed_edge_op(self):
        '''The last step in current edge chain.'''
        step = self
        while True:
            if step.__next_edge_op is None: return step
            step = step.__next_edge_op
    
    @property
    def utilization(self):
        '''Utilization of current edge: service_time / (service_time + free_time).'''
        service_time, total_time = 0, 0
        op = self.__next_edge_op
        while op:
            service_time += op.source.duration
            total_time = op.end_time
            op = op.__next_edge_op
        
        return service_time/total_time if total_time else 1.0


class TransOperationStep(FlowStep, EdgeStep):

    def __init__(self, op:TransOperation=None) -> None:
        '''An operation step wrapping the source operation instance. A step might belong to
        two kinds of sequence chain: a job chain and a machine chain.

        * A job chain is the sequence of operations to complete a job, which is constant in 
        Job-Shop problem
        * while a machine chain is the sequence of operations assigned to a same machine, 
        which is to be solved.

        Args:
            op (Operation): The source operation.
        '''
        FlowStep.__init__(self, op)
        EdgeStep.__init__(self, op)

        # final variable in mathmestical model, while shadow variable in disjunctive graph 
        # model, i.e. the start time is determined by operation sequence
        self.__start_time = 0.0
    

    @property
    def start_time(self) -> float: return self.__start_time

    @property
    def end_time(self) -> float: return self.__start_time + self.source.duration


    def update_start_time(self, start_time:float=None):
        '''Set start time directly, or update start time based on operations sequence in disjunctive 
        graph model. Note the difference to `estimated_start_time`, which is to estimate start time
        before dispatching to the machine, while this method is run after dispatched to a machine. 
        
        Args:
            start_time (float): The tartget time. Default to None, update start time based on sequence.
        '''
        if start_time is not None:
            self.__start_time = start_time

        # if dispatched, dertermine start time by the previous operations in both job chain and 
        # machine chain. Otherwise, use the default start time
        elif self.pre_edge_op:        
            self.__start_time = max(self.pre_flow_op.end_time, self.pre_edge_op.end_time)