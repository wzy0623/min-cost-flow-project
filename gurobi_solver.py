import gurobipy as gp
from gurobipy import GRB


def solve_with_gurobi(
    nodes,
    arcs,
    capacity,
    cost,
    source,
    sink,
    required_flow,
):
    """
    使用 Gurobi 求解最小费用流问题。

    返回：
        flow       最优流量
        total_cost 最优目标值
    """

    # 创建模型
    model = gp.Model("min_cost_flow")

    # 暂时关闭 Gurobi 的详细日志
    model.Params.OutputFlag = 0

    # --------------------------------
    # 1. 决策变量
    # --------------------------------

    x = {}

    for u, v in arcs:
        x[(u, v)] = model.addVar(
            lb=0,
            ub=capacity[(u, v)],
            vtype=GRB.CONTINUOUS,
            name=f"x_{u}_{v}",
        )

    # --------------------------------
    # 2. 目标函数
    # --------------------------------

    model.setObjective(
        gp.quicksum(
            cost[arc] * x[arc]
            for arc in arcs
        ),
        GRB.MINIMIZE,
    )

    # --------------------------------
    # 3. 流守恒约束
    # --------------------------------

    for node in nodes:

        inflow = gp.quicksum(
            x[(u, v)]
            for u, v in arcs
            if v == node
        )

        outflow = gp.quicksum(
            x[(u, v)]
            for u, v in arcs
            if u == node
        )

        # 源点
        if node == source:
            model.addConstr(
                outflow - inflow == required_flow,
                name=f"flow_source_{node}",
            )

        # 汇点
        elif node == sink:
            model.addConstr(
                inflow - outflow == required_flow,
                name=f"flow_sink_{node}",
            )

        # 中间节点
        else:
            model.addConstr(
                inflow == outflow,
                name=f"flow_balance_{node}",
            )

    # --------------------------------
    # 4. 求解
    # --------------------------------

    model.optimize()

    # --------------------------------
    # 5. 检查求解状态
    # --------------------------------

    if model.Status != GRB.OPTIMAL:
        return None

    # --------------------------------
    # 6. 提取最优流
    # --------------------------------

    flow = {
        arc: x[arc].X
        for arc in arcs
    }

    total_cost = model.ObjVal

    return flow, total_cost