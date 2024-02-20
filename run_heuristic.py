import logging, json, os
from model.problem import CFSProblem
from model.solution import CFSSolution
from solver.pulp import PuLPSolver
from solver.dispatching_rule import PriorityDispatchSolver


def print_intermediate_solution(solution:CFSSolution):
    logging.info(f'Makespan: {solution.makespan}')


# benchmark path
script_path = os.path.abspath(__file__)
prj_path = os.path.dirname(script_path)
benchmark_path = os.path.join(prj_path, 'benchmark')


if __name__=='__main__':

    topo_ids = ['dag301', 'dag302', 'dag303']
    traffic_scale = [10, 20, 40, 60, 80, 100, 120, 140, 160, 320, 640, 1280]
    # traffic_scale = [10 * 2 ** i for i in range(8)] # [10, 20, 40, 80, 160, 320, 640, 1280]
    for topo_id in topo_ids:
        for flow_nums in traffic_scale:
            instance_file = f'{topo_id}_{str(flow_nums)}_h'
            # ----------------------------------------
            # solve cfs problem by PriorityDispatchSolver
            # ----------------------------------------
            rules = ['spt', 'lpt', 'sps', 'lps', 'stpt', 'ltpt', 
                     'ect', 'lct', 'swt', 'lwt', 'ltwr', 'mtwr', 
                     'est', 'lst', 'hh', 'ihh']
            for rule in rules:
                problem = CFSProblem(benchmark=f'{topo_id}_{str(flow_nums)}')
                s = PriorityDispatchSolver(rule=rule)

                s.solve(problem=problem, interval=2000, callback=print_intermediate_solution)
                s.wait()
                # ----------------------------------------
                # save simulation result
                # ----------------------------------------
                result_path = os.path.join(benchmark_path, f'results_h/{instance_file}_{rule}')
                with open(result_path, 'w') as f:
                    if s.status:
                        print(f'Problem: {len(problem.flows)} flows, {len(problem.edges)} edges', file=f)
                        print(f'Optimum: {problem.optimum}', file=f)
                        print(f'Solution: {problem.solution.makespan}', file=f)
                        print(f'Terminate successfully in {s.user_time} sec.', file=f)
                    else:
                        print(f'Solving process failed in {s.user_time} sec.', file=f)
    
