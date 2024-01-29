import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from networkx.algorithms import approximation as approx
import random
import time
from iras_docplex import iras_docplex
# from make_print_to_file import make_print_to_file

###### A configuration synthesis tool for online routing and scheduling of time-sensitive traffic ######
###### Created by @BUPT FNL 2022.8.10 ######

###########生成拓扑并画出图#############

nodes=['0','1','2','3']
# edges=[('0','1'),('1','0'),('0','3'),('3','0'),('1','2'),('2','1'),('2','3'),('3','2'),('2','4'),('4','2'),('3','5'),('5','3'),('4','5'),('5','4')]
# edges=[('0','1'),('1','0'),('1','2'),('2','1'),('2','3'),('3','2'),('0','4'),('4','0'),('4','8'),('8','4'),('1','5'),('5','1'),('5','9'),('9','5'),('2','6'),('6','2'),('6','10'),('10','6'),('3','7'),('7','3'),('7','11'),('11','7'),('8','9'),('9','8'),('9','10'),('10','9'),('10','11'),('11','10')]
#nodes=['0','1','2','3','4','5','6','7','8','9','10','11']
#nodes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14' ]
# edges_50 = [('0', '17'), ('6','19'),('16','21'), ('0', '5'), ('0', '21'), ('0', '1'), ('1', '6'), ('1', '20'), ('2', '19'), ('2', '9'), ('2', '11'), ('3', '11'), ('4', '13'), ('4', '15'), ('4', '20'), ('5', '8'), ('6', '7'), ('8', '18'), ('9', '17'), ('9', '11'), ('9', '18'), ('10', '23'), ('11', '12'), ('14', '17'), ('16', '23'), ('18', '22')]
# edges_15 = [(0, 6), (0, 9), (0, 10), (1, 13), (1, 3), (11, 14), (2, 9), (3, 9), (3, 12), (4, 8), (4, 5), (7, 13), (7, 11), (8, 9), (9, 12)]
# edges_18 = [(0, 13), (0, 4), (0, 6), (0, 1), (0, 8), (1, 13), (1, 14), (2, 6), (2, 12), (2, 4), (3, 7), (3, 14), (5, 13), (6, 8), (7, 9), (8, 11), (10, 11), (12, 14)]
# edges_21  =[(0, 9), (0, 2), (0, 11), (0, 14), (1, 9), (1, 6), (2, 7), (2, 13), (3, 7), (3, 11), (3, 5), (3, 12), (3, 4), (3, 14), (4, 10), (5, 13), (5, 8), (5, 6), (5, 7), (7, 8), (8, 9)]
# edges_24 =  [(0, 13), (0, 6), (0, 4), (0, 10), (0, 3), (1, 10), (2, 7), (2, 3), (3, 11), (3, 10), (4, 13), (5, 12), (5, 7), (6, 13), (7, 11), (7, 9), (7, 13), (8, 13), (9, 13), (10, 14), (10, 12), (11, 13), (12, 13), (13, 14)]
#edges = [(0, 14), (0, 10), (0, 12), (1, 9), (1, 5), (1, 13), (1, 11), (1, 14), (1, 7), (1, 6), (2, 14), (2, 13), (2, 10), (2, 4), (3, 12), (3, 9), (4, 9), (4, 7), (4, 8), (4, 6), (5, 11), (6, 10), (6, 9), (7, 13), (7, 11), (9, 11), (9, 10)]
#edges=[('0','1'),('1','0'),('1','2'),('2','1'),('2','3'),('3','2'),('0','4'),('4','0'),('4','8'),('8','4'),('1','5'),('5','1'),('5','9'),('9','5'),('2','6'),('6','2'),('6','10'),('10','6'),('3','7'),('7','3'),('7','11'),('11','7'),('8','9'),('9','8'),('9','10'),('10','9'),('10','11'),('11','10')]
edges=[('0','1'),('1','0'),('1','2'),('2','1'),('2','3'),('3','2')]
# edges30 = [(0, 5), (0, 11), (0, 10), (0, 3), (0, 2), (0, 6), (0, 8), (1, 3), (1, 14), (1, 9), (1, 8), (1, 12), (2, 9), (2, 14), (2, 11), (2, 3), (2, 5), (3, 7), (3, 11), (4, 11), (4, 12), (5, 8), (5, 14), (5, 11), (5, 6), (6, 9), (9, 10), (10, 14), (11, 12), (12, 13)]
# edges45 = [(0, 6), (0, 5), (0, 14), (0, 3), (0, 12), (0, 7), (1, 6), (1, 12), (1, 5), (1, 10), (2, 11), (2, 10), (2, 3), (2, 6), (2, 4), (3, 9), (3, 10), (3, 8), (3, 13), (3, 6), (3, 5), (4, 8), (4, 9), (4, 13), (5, 10), (5, 8), (5, 13), (5, 14), (6, 13), (6, 12), (6, 9), (6, 11), (6, 10), (7, 13), (7, 12), (7, 14), (8, 12), (8, 13), (8, 11), (9, 11), (10, 11), (10, 14), (10, 12), (11, 13), (11, 14)]

#edges_18 = []
#for i in range(len(edges_18)):
#    edges_18.append ((str(edges[i][0]),str(edges[i][1])))
#for i in range(len(edges_18)):
#    edges_18.append ((edges_18[i][1],edges_18[i][0]))
#print(edges_18)

G = nx.MultiDiGraph()
G.add_nodes_from(nodes)
G.add_edges_from(edges)
# nx.draw_spectral(G, with_labels=True, )
nx.draw(G, with_labels=True, )
plt.show()

def calculate_ee_matrix(Gnodes, Gedges, inc_matrix): #计算图的边边邻接矩阵
    ee_matrix = np.zeros([len(Gedges), len(Gedges)])
    for i in range(len(Gnodes)):
        a = []
        for j in range(len(Gedges)):
            if inc_matrix[i,j] == 1:
                a.append(j)
        for x in range(len(a)):
            for y in range(len(a)):
                ee_matrix[a[x],a[y]] = 1
                ee_matrix[a[x],a[x]] = 0
    return ee_matrix

#根据图生成节点、边和相应的矩阵
Gnodes = list(G.nodes)  #图的节点列表
Gedges = list(G.edges)   #图的边列表
adj_matrix = nx.to_numpy_array(G) #图的点点邻接矩阵
inc_matrix = nx.incidence_matrix(G)  #图的点边关联矩阵
ee_matrix = calculate_ee_matrix(Gnodes, Gedges, inc_matrix)  #图的边边关联矩阵
# make_print_to_file("./")
print("*" * 10, "有向无环双边图，拓扑初始化：图中共%d个节点，%d条边"%(len(Gnodes),len(Gedges)), "*" * 10)
print("节点列表:", Gnodes)
print("边列表:", Gedges)
print("点点邻接矩阵: \n",adj_matrix)
print("点边关联矩阵： \n", inc_matrix.todense())
print("边边邻接矩阵： \n", ee_matrix)

# #求两个节点间的路径
# all_shortest_paths = nx.all_shortest_paths(G, '0', '4') #两个节点间的所有最短路径
# all_simple_paths = nx.all_simple_paths(G, '0', '4') #两个节点间的所有简单路径
# shortest_simple_paths = nx.shortest_simple_paths(G, '0','2') #两个节点间的所有简单路径,并按最短到最长排序
# print(list(shortest_simple_paths))

###########生成流量并初始化矩阵#############

def generate_of_df(Gnodes):  #生成流的源节点和目的节点（且源！=目的）
    while True:
        of = random.randint(0,len(Gnodes)-1)
        df = random.randint(0,len(Gnodes)-1)
        if of == df:
            continue
        if of != df:
            break
    return (of,df)

def generate_flow(num, Gnodes):  #生成num个流的列表，每条流为四元组（of, df, pf, rf）,分别表示源，目的，发包周期，出端口传输所需时间
    list_flow = []
    for i in range(num):
        tup_of_df = generate_of_df(Gnodes)
        pf = random.choice([1000,2000,4000,8000])
        rf = random.choice([3,6,9,12])
        tup_pf_rf = (pf, rf)
        tup_flow = tup_of_df + tup_pf_rf
        list_flow.append(tup_flow)
    return list_flow

print( "\n","*" * 10, "流初始化", "*" * 10 )
hypercycle = 8000
total_flow_number = 5
total_flow_list = []
flows_init = (0,0,0,0)
total_flow_list.append(flows_init)

print("初始化流列表为：", total_flow_list)

u_fe_matrix = np.zeros([len(total_flow_list), len(Gedges)])  #初始化u[f][e]矩阵
t_fe_matrix = np.ones([len(total_flow_list), len(Gedges)])  #初始化t[f][e]矩阵
# N = [[0]*10 for i in range(10)]
print("u[f][e]矩阵为：\n", u_fe_matrix)
print("t[f][e]矩阵为：\n", t_fe_matrix, '\n')


fc = [flows_init]
# fn = generate_flow(1, Gnodes)
# total_flow_list.append(fn)
# print("新加流后流列表为：", total_flow_list,'\n')
#Delay = 18
in_node_delay = 5 #每跳的内节点内时延为5us

# fn_all_simple_paths = list(nx.all_simple_paths(G, str(fn[0][0]), str(fn[0][1])))
# fn_rank_paths = calculate_paths(fn_all_simple_paths)

###########路径转换边集合函数以及路径排序函数#############

def paths_to_edges(paths):  #将流的路径转化成边的组合
    flow_edge_list = []
    for j in range(len(paths) - 1):
        edge_tmp = (paths[j], paths[j + 1])
        flow_edge_list.append(edge_tmp)
    print("流的路径流经过的边为：", flow_edge_list)
    return flow_edge_list

def calculate_paths(all_simple_paths):   #给定流的路径，计算出按权重从小到大排序的路径列表
    #print("*"*5, "预路由算法","*"*5)
    all_simple_paths = all_simple_paths
    print("所有简单路径为：", all_simple_paths)
    for i in range(len(all_simple_paths)):
        flow_edge_list = paths_to_edges(all_simple_paths[i])
        hop_count = len(all_simple_paths[i]) - 1
        #print("hop_count为：", hop_count)
        flow_num_max = 0
        for k in range(len(flow_edge_list)):
            flow_num_tmp = 0
            for m in range(len(fc)-1):
                flow_num_tmp += u_fe_matrix[m, Gedges.index((flow_edge_list[k][0],flow_edge_list[k][1],0))]
            if flow_num_tmp > flow_num_max:
                flow_num_max = flow_num_tmp
        #print("flow_num_max为：", flow_num_max)
        rank_num = hop_count/(1+len(Gedges)/2)+flow_num_max/(1+total_flow_number)
        all_simple_paths[i].append(round(rank_num,4))
    rank_simple_paths = sorted(all_simple_paths, key = lambda paths: paths[-1])
    #print("加权后的路径为:", rank_simple_paths)
    for i in range(len(all_simple_paths)):
        rank_simple_paths[i].pop()
    print("最后得到的路由列表:", rank_simple_paths,'\n')
    return rank_simple_paths

###########IRAS调度函数#############

def IRAS_algorithm(fc, fn, u_fe_matrix, t_fe_matrix, iii):  #增量流路由调度算法
    r = 0
    global schedulable_flow_num
    global running_time
    global init_unscheduled_num

    fn_all_simple_paths = list(nx.all_simple_paths(G, str(fn[0]), str(fn[1]), 7))
    tmp_shortest_path = sorted(fn_all_simple_paths, key=lambda i: len(i), reverse=False)
    rank_paths = calculate_paths(tmp_shortest_path[0:5])
    starttime = time.time()
    while r < len(rank_paths):
        flow_path =  rank_paths[r]
        flow_edge = paths_to_edges(flow_path)
        flag = 0
        tmp1 = [np.linspace(0, 0, len(Gedges))]
        for i in range(len(flow_edge)):
            tmp1[0][Gedges.index((flow_edge[i][0], flow_edge[i][1], 0))] = 1
        u_fe_matrix = np.r_[u_fe_matrix, tmp1]
        for j in range(len(fc)):
            for k in range(len(flow_edge)):
                if (u_fe_matrix[j, Gedges.index((flow_edge[k][0],flow_edge[k][1],0))] + u_fe_matrix[-1, Gedges.index((flow_edge[k][0],flow_edge[k][1],0))] < 2):
                    flag += 0
                else:
                    flag += 1
        if flag == 0:  #若沿路径没有任何边和已配置流占用的边重合，直接路由
            print("*"*5,"调度结果：直接路由加入流成功","*"*5)
            print("流经过的路径为：",flow_path)

            tmp2 =[np.linspace(1, 1, len(Gedges))]
            for k in range(len(flow_edge)):
                #tmp2[0][Gedges.index((flow_edge[k][0], flow_edge[k][1], 0))] = (0 + Delay*k) %fn[2]
                tmp2[0][Gedges.index((flow_edge[k][0], flow_edge[k][1], 0))] = (0 + (fn[3]+in_node_delay) *k)%fn[2]
            t_fe_matrix =np.r_[t_fe_matrix, tmp2]
            fc.append(fn)
            schedulable_flow_num += 1
            endtime = time.time()
            print('IRAS算法运行时间%s秒' % (round((endtime - starttime),5)))
            running_time.append(round((endtime - starttime),5))
            return u_fe_matrix,t_fe_matrix
        else:
            #print("进行时隙调度加入CPLEX")
            docplex_run  = iras_docplex(fc, fn, u_fe_matrix, t_fe_matrix, flow_edge, Gedges)
            result_t_fe = docplex_run.docplex_caculate()
            if isinstance(result_t_fe, int):
                tmp3 = [np.linspace(1, 1, len(Gedges))]
                for k in range(len(flow_edge)):
                    #tmp3[0][Gedges.index((flow_edge[k][0], flow_edge[k][1], 0))] = (result_t_fe + Delay * k)%fn[2] #取模运算，使后面几跳的发包时间不超过发包周期
                    tmp3[0][Gedges.index((flow_edge[k][0], flow_edge[k][1], 0))] = (result_t_fe + (fn[3]+in_node_delay) * k)%fn[2] #取模运算，使后面几跳的发包时间不超过发包周期
                t_fe_matrix = np.r_[t_fe_matrix, tmp3]
                fc.append(fn)
                endtime = time.time()
                schedulable_flow_num += 1
                print("*" * 5, "调度结果：时隙分配加入流成功", "*" * 5)
                print("流经过的路径为：", flow_path)
                print('IRAS算法运行时间%s秒' % (round((endtime - starttime), 5)))
                running_time.append(round((endtime - starttime), 5))
                return u_fe_matrix, t_fe_matrix
            else:
                r += 1
                u_fe_matrix = np.delete(u_fe_matrix, -1, axis=0)
                init_unscheduled_num += 1
                continue
    print("*"*5,"调度结果：第%d条流不可被调度"%(iii+1),"*"*5)
    endtime = time.time()
    running_time.append(round((endtime - starttime), 5))
    endtime = time.time()
    print('IRAS算法运行时间%s秒' % (round((endtime - starttime),5)))
    return u_fe_matrix,t_fe_matrix


fnnn = generate_flow(5, Gnodes)
total_flow_list.append(fnnn)
print("新加流后流列表为：", total_flow_list,'\n')
schedulable_flow_num = 0
init_unscheduled_num = 0
running_time = []

###########增量调度迭代主函数#############

for i in range(len(fnnn)):
    print("*" * 10, "第%d条流的IRAS算法"%(i+1), "*" * 10)
    u_fe_matrix, t_fe_matrix = IRAS_algorithm(fc, fnnn[i], u_fe_matrix, t_fe_matrix, i)
    print("u[f][e]矩阵为：\n", u_fe_matrix, '\n')
    print("t[f][e]矩阵为：\n",t_fe_matrix, '\n')

print("*"*10,"实验结果","*"*10)
print("流总数为：", len(fnnn),  "可调度的流总数为：", schedulable_flow_num, "初次进入cplex不可调度的流总数为", init_unscheduled_num)
print("所有流的算法运行时间为",running_time)
print("所有流的算法运行总时间为",sum(running_time))

#绘制每条流的运行时间的柱状图
plt.bar(range(len(running_time)), running_time, align="center")
plt.legend(['flow number with runing time curve'])
plt.xlabel("the # th flow ")
plt.ylabel("running time (in second)")
plt.show()
