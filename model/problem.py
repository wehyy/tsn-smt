'''Co-Flow Schedule Problem.
'''

import os, json, random
import networkx as nx
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from model.domain import (Flow, Edge, TransOperation, Cloneable)
from model.topo import Topo
from model.flow import CoFlow, get_ops
from common.exception import JSPException
from jsp_fwk.model.domain import (Job, Machine, Operation)

class CFSProblem(Cloneable):
    '''base class for Co-Flow Schedule Problem.
    '''

    def __init__(self, path_ops:list=None, ops:list=None, 
                        num_flows:int=0, num_edges:int=0, 
                        benchmark:str=None, 
                        input_file:str=None,
                        name:str=None) -> None:
        '''Initialize problem by operation list, or random problem with specified count of jobs 
        and machines, or just load data from benchmark/user-defined file. 

        Args:
            ops (list, optional): Operation list to schedule. 
            num_jobs (int, optional): Initialize random problem by specified count of jobs. 
            num_machines (int, optional): Initialize random problem by specified count of machines. 
            benchmark (str, optional): Benchmark name to load associated data.
            input_file (str, optional): User defined data file path. 
            name (str, optional): Problem name. Benchmark name if None. 
        '''
        self.name = name
        
        # solution
        self.__solution = None          # to solve  
        self.__optimum = None           # benchmark value
        self.__solution_callback = None   # callback when a better solution is found

        # dynamic Gantt chart
        self.__gantt_animation = None
        self.__need_update_chart = False # update chart when found a better solution

        # initialize operations
        self.__ops = []   # type: list[TransOperation]
        if ops: self.__ops = ops

        # random operations
        elif num_flows and num_edges:
            self.__ops = self.__generate_by_random(num_flows, num_edges)
        
        # from benchmark
        elif benchmark:
            self.__ops, self.__path_ops = self.__load_from_benchmark(name=benchmark)
            if not name: self.name = benchmark
        
        # from user input file
        elif input_file:
            self.__ops = self.__load_from_file(input_file)            

        # collect jobs and machines
        self.__flows, self.__edges = self.__collect_flows_and_edges()

        # handle coflow schedule
        self.__path_ops = []
        if path_ops: self.__path_ops = path_ops
    
    @property
    def flows(self): return self.__flows

    @property
    def edges(self): return self.__edges

    @property
    def ops(self): return self.__ops

    @property
    def path_ops(self): return self.__path_ops

    @property
    def optimum(self): return self.__optimum

    @property
    def solution(self): return self.__solution

    def register_solution_callback(self, callback):
        '''Register solution callback called when a better solution is found.'''
        self.__solution_callback = callback


    def update_solution(self, solution):
        '''Set a better solution.

        Args:
            solution (JSSolution): A better solution. 
        '''
        # update solution and run user defined function
        self.__solution = solution
        if self.__solution_callback: self.__solution_callback(solution)

        # signal to update gantt chart
        self.__need_update_chart = True


    def dynamic_gantt(self, interval:int=2000):
        '''Initialize empty Gantt chart with `matplotlib` and update it dynamically.

        Args:
            
            interval (int, optional): Refresh interval (in ms). Defaults to 2000 ms.
        '''
        # two subplots
        fig, (gnt_job, gnt_machine) = plt.subplots(2,1, sharex=True)

        # title and sub-title
        fig.suptitle('Gantt Chart', fontweight='bold')
        if self.__optimum is not None:
            gnt_job.set_title(f'Optimum: {self.__optimum}', color='gray', fontsize='small')

        # axes style        
        # gnt_job.set(ylabel='Flow', \
        #     yticks=range(len(self.__flows)), \
        #     yticklabels=[f'F-{flow.id}' for flow in self.__flows])
        # gnt_job.grid(which='major', axis='x', linestyle='--')
        
        # gnt_machine.set(xlabel='Time', ylabel='Edge',\
        #     yticks=range(len(self.__edges)), \
        #     yticklabels=[f'E-{edge.id}' for edge in self.__edges])
        # gnt_machine.grid(which='major', axis='x', linestyle='--')
        
        gnt_job.set(ylabel='Flow', yticks=[])
        gnt_job.grid(which='major', axis='x', linestyle='--')
        
        gnt_machine.set(xlabel='Time', ylabel='Edge', yticks=[])
        gnt_machine.grid(which='major', axis='x', linestyle='--')

        # animation
        self.__gantt_animation = FuncAnimation(fig, \
            func=lambda i: self.__update_gantt_chart(axes=(gnt_job, gnt_machine)), \
            cache_frame_data=False, \
            interval=interval, \
            repeat=False)
    

    def __update_gantt_chart(self, axes:tuple):
        if not self.__need_update_chart: 
            return
        else:
            self.__need_update_chart = False

        # update gantt chart
        self.__solution.plot(axes)


    def __collect_flows_and_edges(self):
        flows, edges = zip(*((op.flow, op.edge) for op in self.__ops))
        flows = sorted(set(flows), key=lambda flow: flow.id)
        edges = sorted(set(edges), key=lambda edge: edge.id)
        return flows, edges


    def __load_from_benchmark(self, name:str) -> list:
        '''Load jobs and optimum value from benchmark data.'''
        # benchmark path
        script_path = os.path.abspath(__file__)
        prj_path = os.path.dirname(os.path.dirname(script_path))
        benchmark_path = os.path.join(prj_path, 'benchmark')

        # check benchmark name
        with open(os.path.join(benchmark_path, 'instances.json'), 'r') as f:
            instances = json.load(f)
        for instance in instances:
            if instance['name']==name:
                toponame = instance['topo']
                filename = instance['path']
                self.__optimum = instance['optimum']
                # if instance['optimum']:
                #     self.__optimum = instance['optimum']
                # elif instance['bounds']:
                #     self.__optimum = (instance['bounds']['lower'], instance['bounds']['upper'])
                break
        else:
            raise JSPException(f'Cannot find benchmark name: {name}.')
        
        # load jobs
        return self.__load_from_file(toponame, os.path.join(benchmark_path, filename))
   

    def __load_from_file(self, toponame:str, filename:str) -> list:
        '''Load jobs from formatted data file.'''
        # load topo
        topo = Topo(load_topo_name=toponame)

        if not os.path.exists(filename):
            raise JSPException(f'Cannot find data file: {filename}.')
        
        # load instance_detail #
        with open(filename, 'r') as f:
            instance_detail = json.load(f)
        
        coflows = [CoFlow(f["flowid"], topo, nx.DiGraph(f["edges"])) for f in instance_detail["flows"]]
        ops, path_ops = get_ops(coflows)
        return ops, path_ops


    def __generate_by_random(self, num_jobs:int, num_machines:int) -> list:
        '''Generate random jobs with specified count of machine and job.'''
        # job list and machine list
        machines = [Machine(i) for i in range(num_machines)]
        jobs = [Job(i) for i in range(num_jobs)]

        # random operations
        ops = []
        i = 0
        lower, upper = 10, 50
        for job in jobs:
            random.shuffle(machines)
            for machine in machines:
                duration = random.randint(lower, upper)
                op = Operation(id=i, job=job, machine=machine, duration=duration)
                ops.append(op)
                i += 1
        
        return ops    