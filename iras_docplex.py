import docplex
from docplex.mp.model import Model

###需要安装IBM Clpex求解器，并将其中Python文件夹下的Docplex文件夹复制到开发环境的库路径下###

#D = 18
hyper_cycle = 8000
in_node_delay = 5

class iras_docplex():
    def __init__(self,fc_tmp, fn_tmp, u_fe_matrix_tmp, t_fe_matrix_tmp, flow_edge_tmp, Gedges_tmp):
        self.fc = fc_tmp
        self.fn = fn_tmp
        self.u_fe_matrix = u_fe_matrix_tmp
        self.t_fe_matrix = t_fe_matrix_tmp
        self.flow_edge = flow_edge_tmp
        self.Gedges = Gedges_tmp

    def docplex_caculate(self):
        fn_pf = self.fn[2]
        A = [[] for i in range(len(self.flow_edge))]  #存储有重合的边的各流的时间，每一排为一条边的各个流的发包时间
        # B = [[]for i in range(len(self.flow_edge))]   #存储fn在各边的发包时间，每一排为一条边的fn流的发包时间，第一排为x，第二排为x+D，以此类推
        aa = [[]for i in range(len(self.flow_edge))]  #存储有重合的边的各流的周期数上界, fc_period_count
        fc_pf_matrix = [[]for i in range(len(self.flow_edge))]  #存储有重合的边的各流的周期
        fc_rf_matrix = [[]for i in range(len(self.flow_edge))]  #存储有重合的边的各流的出端口传输时间
        # x = int()
        edge_count = 0
        for j in range(len(self.flow_edge)):
            for i in range(len(self.fc)):
                if (self.u_fe_matrix[i,self.Gedges.index((self.flow_edge[j][0],self.flow_edge[j][1],0))]==1):
                    A[j].append(self.t_fe_matrix[i, self.Gedges.index((self.flow_edge[j][0],self.flow_edge[j][1],0))])
                    fc_pf_matrix[j].append(self.fc[i][2])
                    fc_rf_matrix[j].append(self.fc[i][3])
                    aa[j].append(hyper_cycle/self.fc[i][2])
                else:
                    continue
        # print('A为：', A)
        # print('aa为：', aa)
        # print('fc_pf_matrix为：', fc_pf_matrix)
        # print('fc_rf_matrix为：', fc_rf_matrix)
        mdl = Model(name='my_prob')
        fn_te_x = mdl.integer_var(name='fn_te_x')
        mdl.add_constraint(0<=fn_te_x,"var_constraint")
        mdl.add_constraint(fn_te_x<=int((self.fn[2] - self.fn[3])),"var_constraint")
        for j in range(len(self.flow_edge)):
            if A[j] != None:
                for i in range(len(A[j])):
                     for k in range(int(hyper_cycle/fn_pf)):
                         for m in range(int(aa[j][i])):
                            #mdl.add_constraint((fn_te_x >=int((A[j][i]-j*D+fc_rf_matrix[j][i]-k*fn_pf+m*fc_pf_matrix[j][i]))) + (fn_te_x <=int((A[j][i]-j*D-self.fn[3]-k*fn_pf+m*fc_pf_matrix[j][i])))>=1 )
                            mdl.add_constraint((fn_te_x >=int((A[j][i]-j*(self.fn[3]+in_node_delay)+fc_rf_matrix[j][i]-k*fn_pf+m*fc_pf_matrix[j][i]))) + (fn_te_x <=int((A[j][i]-j*(self.fn[3]+in_node_delay)-self.fn[3]-k*fn_pf+m*fc_pf_matrix[j][i])))>=1 )
            else:
                continue

        mdl.minimize(fn_te_x)
        my_solution = mdl.solve()
        if my_solution:
            result = fn_te_x.solution_value
            # print("结果t[fn][E start]  = ", result)
            return int(result)
        else:
            result = None
            # print("结果t[fn][E start]  = None")
            return result

























