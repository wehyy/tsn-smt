'''Solution of CoFlow Schedule Problem, especially the sequence of operations
assigned in each edge(machine), and the deduced start time of each operation accordingly.
'''

from collections import defaultdict
from matplotlib.container import BarContainer
from model.problem import CFSProblem
from model.variable import (FlowStep, EdgeStep, TransOperationStep)
from model.domain import (TransOperation, Cloneable)
from jsp_fwk.model.problem import JSProblem
from jsp_fwk.model.solution import JSSolution
from common.graph import DirectedGraph


class CFSSolution(Cloneable):

    def __init__(self, problem: CFSProblem) -> None:
        '''Initialize solution by copying all operations from `problem`.

        Args:
            problem (JSProblem): Problem to solve.
        '''
        self.__ops = [TransOperationStep(op) for op in problem.ops]

        if problem.path_ops:
            ops_map = dict(zip(problem.ops, self.__ops))
            self.__path_ops = []
            for path in problem.path_ops:
                self.__path_ops.append([ops_map[op] for op in path])
        
        self.__edges = problem.edges

        # group operation steps with job and machine and initialize job chain
        self.__flow_ops = defaultdict(list)
        self.__edge_ops = defaultdict(list)
        self.__create_flow_chain()

        # operations in topological order: available for disjunctive graph model only
        self.__sorted_ops = None # type: list[TransOperationStep]


    @property
    def ops(self) -> list: 
        '''All operation steps in job related order: 
        [job0_op0, job0_op1, ..., job1_op0, job1_op1, ...]'''
        return self.__ops
    
    @property
    def path_ops(self) -> list:
        return self.__path_ops

    @property
    def flow_ops(self): 
        '''Operation steps grouped by flow: {flow_step: [op0, op1, op2, ...]}.'''
        return self.__flow_ops

    @property
    def edge_ops(self): 
        '''Operation steps grouped by edge: {edge_step: [op0, op5, op8, ...]}.'''
        return self.__edge_ops

    @property
    def sorted_ops(self): 
        '''Topological order of the operation steps. Only available for disjunctive graph model.'''
        return self.__sorted_ops

    @property
    def makespan(self) -> float:
        '''Makespan of current solution. 
        Only available when the solution is feasible; otherwise None.
        '''
        return max(map(lambda op: op.end_time, self.__ops))
    

    def find(self, source_op:TransOperation):
        '''Find the associated step with source operation.'''
        for op in self.__ops:
            if op.source==source_op:
                return op
        return None


    def flow_head(self, op:TransOperationStep):
        '''The first step in flow chain of specified `op`, i.e. the virtual flow step.'''
        for flow_step in self.__flow_ops:
            if flow_step.source==op.source.flow:
                return flow_step
        return None
    

    def edge_head(self, op:TransOperationStep):
        '''The first step in edge chain of specified `op`, i.e. the virtual edge step.'''
        for edge_step in self.__edge_ops:
            if edge_step.source==op.source.edge:
                return edge_step
        return None


    @property
    def imminent_ops(self):
        '''Collect imminent operations in the processing queue.'''
        head_ops = []
        for flow_step in self.__flow_ops:
            op = flow_step.next_flow_op
            while op and op.pre_edge_op:
                op = op.next_flow_op
            if op: head_ops.append(op)
        return head_ops

    
    def copy(self):
        '''Hard copy of current solution. Override `Cloneable.copy()`.'''
        # copy step instances and flow chain
        ops = [op.source for op in self.__ops]
        solution = CFSSolution(problem=CFSProblem(ops=ops))

        # copy edge chain
        def map_source_to_step(solution):
            '''map source instance to step instance'''
            step_map = {}
            for edge_step, ops in solution.edge_ops.items():
                step_map[edge_step.source] = edge_step
                for op_step in ops:
                    step_map[op_step.source] = op_step
            return step_map
        step_map = map_source_to_step(solution)

        for op, new_op in zip(self.__ops, solution.ops):
            if not op.pre_edge_op: continue
            new_op.pre_edge_op = step_map[op.pre_edge_op.source]
        
        # update
        solution.evaluate()

        return solution


    def estimated_start_time(self, op:TransOperationStep) -> float:
        '''Estimate the start time if it's dispatched to the end of current edge chain.'''
        edge_op = self.edge_head(op).tailed_edge_op
        return max(op.pre_flow_op.end_time, edge_op.end_time)


    def dispatch(self, op:TransOperationStep):
        '''Dispatch the operation step to the associated edge.'''
        pre_edge_op = self.edge_head(op).tailed_edge_op
        op.pre_edge_op = pre_edge_op
        self.evaluate(op=op) # update start time accordingly


    def is_feasible(self) -> bool:
        '''If current solution is valid or not. 
        Note to call this method after evaluating the solution if based on disjunctive graph model.
        '''
        # check topological order if disjunctive graph model, 
        # otherwise check the start time further directly
        if self.__sorted_ops: return True

        # validate job chain        
        # for flow, ops in self.__flow_ops.items():
        #     ops.sort(key=lambda op: op.id) # sort in flow sequence, i.e. default id order
        #     ref = 0
        #     for op in ops:
        #         if op.end_time <= ref: 
        #             print('debug: validate job chain', op, op.end_time, ref)
        #             return False
        #         ref = op.end_time

        # validate flow chain
        for path in self.__path_ops:
            ref = 0
            for op in path:
                if op.end_time <= ref:
                    print('debug: validate job chain', op, op.end_time, ref)
                    return False
                ref = op.end_time
        
        # validate edge chain        
        for edge, ops in self.__edge_ops.items():
            ops.sort(key=lambda op: op.start_time) # sort by start time
            ref = 0
            for op in ops:
                if op.end_time <= ref: 
                    print('debug: validate edge chain')
                    return False
                ref = op.end_time
        
        return True


    def evaluate(self, op:TransOperationStep=None) -> bool:
        '''Evaluate specified and succeeding operations of current solution, especially 
        work time. Generally the machine chain was changed before calling this method.

        NOTE: this method is only available for disjunctive graph model.

        Args:
            op (OperationStep, optional): The operation step to update. Defaults to None,
                i.e. the first operation.
        
        Returns:
            bool: True if current solution is feasible.
        '''
        # update topological order due to the changed machine chain
        self.__update_graph()
        if not self.__sorted_ops: 
            print('debug: not sorted_ops')
            return False

        # the position of target process
        pos = 0 if op is None else self.__sorted_ops.index(op)
        
        # update process by the topological order
        for op in self.__sorted_ops[pos:]:
            op.update_start_time()
        
        return True


    def plot(self, axes:tuple):
        '''Plot Gantt chart.

        Args:
            axes (tuple): Axes of `matplotlib` figure: (job sub-plot axis, machine sub-plot axis).
        '''
        gnt_job, gnt_machine = axes

        # title
        gnt_job.set_title(f'Result: {self.makespan or "n.a."}', color='gray', fontsize='small', loc='right')

        # clear plotted bars
        bars = [bar for bar in gnt_job.containers if isinstance(bar, BarContainer)]
        bars.extend([bar for bar in gnt_machine.containers if isinstance(bar, BarContainer)])
        for bar in bars: 
            bar.remove()
        
        # map edge to y tick
        edge_id_map_y_tick = {}
        count = 0
        for edge in self.__edges:
            edge_id_map_y_tick[edge.id] = count
            count += 1

        # plot new bars
        for op in self.__ops:
            gnt_job.barh(op.source.flow.id, op.source.duration, left=op.start_time, height=0.5)
            gnt_machine.barh(edge_id_map_y_tick[op.source.edge.id], op.source.duration, left=op.start_time, height=0.5)
            
        # reset x-limit
        for axis in axes:
            axis.relim()
            axis.autoscale()


    def __create_flow_chain(self):
        '''Initialize flow chain based on the sequence of operations.'''
        # group operations with job and machine, respectively
        flow_ops = defaultdict(list)
        edge_ops = defaultdict(list)
        for op in self.__ops:
            flow_ops[op.source.flow].append(op)
            edge_ops[op.source.edge].append(op)
        
        # convert the key form Job/Machine to JobStep/MachineStep
        self.__flow_ops = { FlowStep(flow) : ops for flow, ops in flow_ops.items() }
        self.__edge_ops = { EdgeStep(edge) : ops for edge, ops in edge_ops.items() }
        
        # create chain for operations of each job
        def create_chain(flow_step:FlowStep, ops:list):
            pre = flow_step
            for op in ops:
                op.pre_flow_op = pre
                pre = op

        for flow, ops in self.__flow_ops.items(): create_chain(flow, ops)    
    

    def __update_graph(self):
        '''Update the associated directed graph and the topological order accordingly.'''
        # add the dummy source and sink node
        source, sink = TransOperationStep(), TransOperationStep()

        # identical directed graph
        graph = DirectedGraph()
        for op in self.__ops:
            # flow chain edge
            if not isinstance(op.pre_flow_op, TransOperationStep): # first real operation step
                graph.add_edge(source, op)
            
            if op.next_flow_op:
                graph.add_edge(op, op.next_flow_op)
            else:
                graph.add_edge(op, sink)
            
            # edge chain edge
            if op.next_edge_op and op.next_edge_op!=op.next_flow_op:
                graph.add_edge(op, op.next_edge_op)

        # topological order:
        # except the dummy source and sink nodes
        ops = graph.sort()
        self.__sorted_ops = ops[1:-1] if ops else None