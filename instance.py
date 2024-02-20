import logging, json, os
import networkx as nx
from collections import defaultdict
from model.problem import CFSProblem
from model.solution import CFSSolution
from solver.pulp import PuLPSolver
from model.topo import Topo
from model.flow import TaskFlowGenerator, CoFlow
from model.flow import get_ops
from model.domain import (Flow, Edge, TransOperation)

# benchmark path
script_path = os.path.abspath(__file__)
prj_path = os.path.dirname(script_path)
benchmark_path = os.path.join(prj_path, 'benchmark')


if __name__=='__main__':

    # topo_ids = list(range(1, 4))
    topo_ids = ['dag301', 'dag302', 'dag303']
    traffic_scale = [10, 20, 40, 60, 80, 100, 120, 140, 160, 320, 640, 1280]
    # traffic_scale = [10 * 2 ** i for i in range(8)] # [10, 20, 40, 80, 160, 320, 640, 1280]
    instance_info = list()
    for topo_id in topo_ids:
        topo = Topo(load_topo_name=topo_id)
        for flow_nums in traffic_scale:
            instance_file = f'{topo_id}_{str(flow_nums)}'
            instance_path = os.path.join(benchmark_path, "instances", instance_file)
            with open(instance_path, 'r') as f:
                instance_detail = json.load(f)
            
            coflows = [CoFlow(f["flowid"], topo, nx.DiGraph(f["edges"])) for f in instance_detail["flows"]]
            ops, path_ops = get_ops(coflows)
            # ops = [TransOperation(op["opid"], Flow(op["flow"]), Edge(op["edge"]), op["duration"]) for 
            #        op in instance_detail["ops"]]
            # path_ops = [[TransOperation(op["opid"], Flow(op["flow"]), Edge(op["edge"]), op["duration"]) for 
            #              op in path] for path in instance_detail["path_ops"]]

            # ----------------------------------------
            # solve cfs problem
            # ----------------------------------------
            problem = CFSProblem(path_ops=path_ops, ops=ops)
            
            instance_info.append({
                "name": f'{instance_file}',
                "topo": f'{topo_id}',
                "flows": len(problem.flows),
                "edges": len(problem.edges),
                "optimum": problem.optimum,
                "path": f'instances/{instance_file}'
            })
    info_path = os.path.join(benchmark_path, "instances.json")
    with open(info_path, 'w') as f:
        json.dump(instance_info, f, indent=4)
