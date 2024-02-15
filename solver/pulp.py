import pulp
from model.problem import CFSProblem
from model.solution import CFSSolution
from jsp_fwk.model.solver import JSSolver
from jsp_fwk.model.problem import JSProblem
from jsp_fwk.model.solution import JSSolution
from jsp_fwk.common.exception import JSPException

class PuLPSolver(JSSolver):

    SOLVER_DICT = {
        'CBC': pulp.PULP_CBC_CMD,      # default by pulp
        'SCIP': pulp.SCIP_CMD,         # install and set env path manually
        'GUROBI': pulp.GUROBI_CMD,
        'CPLEX': pulp.CPLEX_CMD
    }

    def __init__(self, name:str='pulp', solver_name:str='CBC', max_time:int=None, msg:bool=False, log_path:str=None) -> None:
        '''Solve JSP with PuLP, which is an LP modeler written in python. PuLP can generate MPS 
        or LP files and call GLPK, COIN CLP/CBC, CPLEX, and GUROBI to solve linear problems.

        Args:
            name (str, optional): JSP solver name.
            solver_name (str, optional): solver for MIP, default to CBC; support also SCIP or Gurobi.
            max_time (int, optional): Max solving time in seconds. Defaults to None, i.e. no limit.
            msg (bool, optional): show solver log or not. Default to False.
        '''        
        super().__init__(name)
        self.__solver_name = solver_name
        self.__msg = msg
        self.__max_time = max_time
        self.__log_path = log_path


    def do_solve(self, problem:CFSProblem):
        '''Solve JSP with PuLP and the default CBC solver.

        https://github.com/KevinLu43/JSP-by-using-Mathematical-Programming-in-Python/
        '''
        # Initialize an empty solution from problem
        solution = CFSSolution(problem)
       
        # create model
        model, variables = self.__create_model(solution)

        # solver
        solver_cmd = self.SOLVER_DICT.get(self.__solver_name.upper(), pulp.PULP_CBC_CMD)
        solver = solver_cmd(msg=self.__msg, timeLimit=self.__max_time, options=[f'set logfile {self.__log_path}'])
        model.solve(solver)
        if model.status!=pulp.LpStatusOptimal:
            raise JSPException('No feasible solution found.')

        # assign pulp solution back to JSPSolution
        for op, var in variables.items():
            op.update_start_time(var.varValue)        
        problem.update_solution(solution) # update solution


    def __create_model(self, solution:CFSSolution):
        '''Create PuLP model: variables, constraints and objective.'''
        # create the model
        model = pulp.LpProblem("min_makespan", pulp.LpMinimize)

        # create variables
        # (1) start time of each operation
        max_time = sum(op.source.duration for op in solution.ops) # upper bound of variables
        variables = pulp.LpVariable.dicts(name='start_time', \
                                        indices=solution.ops, \
                                        lowBound=0, \
                                        upBound=max_time, \
                                        cat='Integer')

        # (2) binary variable, i.e. 0 or 1, indicating the sequence of every two operations 
        # assigned in same machine
        combinations = []
        for _, ops in solution.edge_ops.items():
            combinations.extend(pulp.combination(ops, 2))
        bin_vars =  pulp.LpVariable.dicts(name='binary_var', \
                                     indices=combinations, \
                                     lowBound=0, \
                                     cat='Binary')

        # objective: makespan / flowtime
        s_max = pulp.LpVariable(name='max_start_time', \
                                lowBound=0, \
                                upBound=max_time, \
                                cat='Integer')
        model += s_max        
        
        # apply constraints:
        # (1) the max start time
        for path in solution.path_ops:
            last_op = path[-1]
            model += (s_max-variables[last_op]) >= last_op.source.duration

        # for _, ops in solution.flow_ops.items():
        #     last_op = ops[-1]
        #     model += (s_max-variables[last_op]) >= last_op.source.duration

        # (2) operation sequence inside a job
        for path in solution.path_ops:
            pre = None
            for op in path:
                if pre:
                    model += (variables[op]-variables[pre]) >= pre.source.duration
                pre = op
        
        # pre = None
        # for op in solution.ops:
        #     if pre and pre.source.flow==op.source.flow:
        #         model += (variables[op]-variables[pre]) >= pre.source.duration
        #     pre = op

        # (3) no overlap for operations assigned to same machine
        for op_a, op_b in combinations:
            model += (variables[op_a]-variables[op_b]) >= (op_b.source.duration - max_time*(1-bin_vars[op_a, op_b]))
            model += (variables[op_b]-variables[op_a]) >= (op_a.source.duration - max_time*bin_vars[op_a, op_b])

        return model, variables
