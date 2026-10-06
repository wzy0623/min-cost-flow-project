import math

from random_instance import generate_random_instance

from min_cost_flow import (
    min_cost_flow_with_potential,
    check_capacity,
    check_flow_conservation,
    check_objective,
)

from gurobi_solver import solve_with_gurobi


nodes, arcs, capacity, cost, source, sink, required_flow = (
    generate_random_instance(
        num_nodes=10,
        num_arcs=20,
        required_flow=5,
        seed=42,
    )
)


# ========================================
# SSP
# ========================================

ssp_result = min_cost_flow_with_potential(
    nodes=nodes,
    arcs=arcs,
    capacity=capacity,
    cost=cost,
    source=source,
    sink=sink,
    required_flow=required_flow,
)


if ssp_result is None:
    print("SSP 未找到可行解")
    raise SystemExit


ssp_flow, ssp_cost = ssp_result


# ========================================
# Validators
# ========================================

capacity_ok = check_capacity(
    ssp_flow,
    capacity,
)

conservation_ok = check_flow_conservation(
    nodes,
    arcs,
    ssp_flow,
    source,
    sink,
    required_flow,
)

objective_ok = check_objective(
    arcs,
    ssp_flow,
    cost,
    ssp_cost,
)


# ========================================
# Gurobi
# ========================================

gurobi_result = solve_with_gurobi(
    nodes=nodes,
    arcs=arcs,
    capacity=capacity,
    cost=cost,
    source=source,
    sink=sink,
    required_flow=required_flow,
)


if gurobi_result is None:
    print("Gurobi 未找到可行解")
    raise SystemExit


gurobi_flow, gurobi_cost = gurobi_result


# ========================================
# 对比
# ========================================

same_objective = math.isclose(
    ssp_cost,
    gurobi_cost,
    rel_tol=1e-9,
    abs_tol=1e-9,
)


print("\n" + "=" * 60)
print("随机实例测试结果")
print("=" * 60)

print("节点数：", len(nodes))
print("弧数：", len(arcs))
print("要求流量：", required_flow)

print("-" * 60)

print("SSP 最优费用：", ssp_cost)
print("Gurobi 最优费用：", gurobi_cost)

print("-" * 60)

print(
    "容量约束：",
    "PASS" if capacity_ok else "FAIL"
)

print(
    "流守恒：",
    "PASS" if conservation_ok else "FAIL"
)

print(
    "目标函数：",
    "PASS" if objective_ok else "FAIL"
)

print(
    "SSP / Gurobi 目标值一致：",
    "PASS" if same_objective else "FAIL"
)