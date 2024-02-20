import logging, json, os
from collections import defaultdict
from model.problem import CFSProblem
from model.solution import CFSSolution
from solver.pulp import PuLPSolver
from model.topo import Topo
from model.flow import TaskFlowGenerator, CoFlow
from model.flow import get_ops


def print_intermediate_solution(solution:CFSSolution):
    logging.info(f'Makespan: {solution.makespan}')


# benchmark path
script_path = os.path.abspath(__file__)
prj_path = os.path.dirname(script_path)
benchmark_path = os.path.join(prj_path, 'benchmark')


if __name__=='__main__':

    topo_ids = list(range(1, 4))
    traffic_scale = list(range(20, 161, 20))
    # traffic_scale = [10 * 2 ** i for i in range(8)] # [10, 20, 40, 80, 160, 320, 640, 1280]
    instance_info = list()
    for topo_id in topo_ids:
        topo = Topo(load_topo_name=str(topo_id))
        # topo = Topo(weighted=True)
        # topo.saveTopo(str(topo_id))
        generator = TaskFlowGenerator(topo)
        for flow_nums in traffic_scale:
            flows = generator.flowGenerate(nums=flow_nums)
            coflows = []
            for i, flow in enumerate(flows):
                coflows.append(CoFlow(i, topo, flow))
            ops, path_ops = get_ops(coflows)
            # ----------------------------------------
            # save simulation instance details
            # ----------------------------------------
            # instance_file = "dag30_" + str(topo_id) + str(flow_nums)
            instance_file = f'dag{str(len(topo.nodes))}{str(topo_id)}_{str(flow_nums)}'
            instance_path = os.path.join(benchmark_path, "instances", instance_file)

            instance_detail = defaultdict(list)
            instance_detail["flows"] = [{"flowid": coflow.id,
                                         "edges": list(coflow.graph.edges(data=True)),} for coflow in coflows]
            instance_detail["ops"] = [{"opid": op.id, 
                                    "flow": op.flow.id, 
                                    "edge": op.edge.id, 
                                    "duration": op.duration} for op in ops]
            instance_detail["path_ops"] = [[{"opid": op.id, 
                                            "flow": op.flow.id,
                                            "edge": op.edge.id, 
                                            "duration": op.duration} for op in path] for path in path_ops]
            
            with open(instance_path, 'w') as f:
                json.dump(instance_detail, f, indent=4)

            # ----------------------------------------
            # solve cfs problem
            # ----------------------------------------
            problem = CFSProblem(path_ops=path_ops, ops=ops)
            solverlog_path = os.path.join(benchmark_path, f'solverlogs/{instance_file}')
            s = PuLPSolver(solver_name='CPLEX', max_time=3600, log_path=solverlog_path)
            s.solve(problem=problem, interval=2000, callback=print_intermediate_solution)
            s.wait()

            # ----------------------------------------
            # save simulation result
            # ----------------------------------------
            result_path = os.path.join(benchmark_path, f'results/{instance_file}')
            with open(result_path, 'w') as f:
                if s.status:
                    print(f'Problem: {len(problem.flows)} flows, {len(problem.edges)} edges', file=f)
                    print(f'Optimum: {problem.optimum}', file=f)
                    print(f'Solution: {problem.solution.makespan}', file=f)
                    print(f'Terminate successfully in {s.user_time} sec.', file=f)
                else:
                    print(f'Solving process failed in {s.user_time} sec.', file=f)
            
            instance_info.append({
                "name": f'{instance_file}',
                "topo": f'dag{str(len(topo.nodes))}{str(topo_id)}',
                "flows": len(problem.flows),
                "edges": len(problem.edges),
                "optimun": problem.optimum,
                "path": f'instances/{instance_file}'
            })
    info_path = os.path.join(benchmark_path, "instances.jsons")
    with open(info_path, 'w') as f:
        json.dump(instance_info, f, indent=4)
