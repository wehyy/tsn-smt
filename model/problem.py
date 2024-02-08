'''Co-Flow Schedule Problem.
'''

import os, json
from jsp_fwk import JSProblem

class CFSProblem(JSProblem):
    '''base class for Co-Flow Schedule Problem.
    '''

    def __init__(self, ops:list=None, 
                        num_jobs:int=0, num_machines:int=0, 
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
        super.__init__(ops, num_jobs, num_machines, benchmark, input_file, name)