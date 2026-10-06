import math

from examples import (
    arcs,
    capacity,
    cost,
    nodes,
    required_flow,
    sink,
    source,
)
from gurobi_solver import solve_with_gurobi
from min_cost_flow import (
    check_capacity,
    check_flow_conservation,
    check_objective,
    min_cost_flow_with_potential,
)


def main():

    # =========================================================
    # 1. 自实现 SSP 算法
    # =========================================================

    print("=" * 60)
    print("自实现 Successive Shortest Path 求解")
    print("=" * 60)

    result = min_cost_flow_with_potential(
        nodes=nodes,
        arcs=arcs,
        capacity=capacity,
        cost=cost,
        source=source,
        sink=sink,
        required_flow=required_flow,
    )

    if result is None:
        print("不存在满足要求流量的可行解")
        return

    flow, total_cost = result


    # =========================================================
    # 2. 输出 SSP 最终结果
    # =========================================================

    print("\n最终结果")
    print("-" * 60)

    for arc in arcs:
        print(
            f"弧 {arc}: "
            f"flow = {flow[arc]}, "
            f"capacity = {capacity[arc]}, "
            f"cost = {cost[arc]}"
        )

    print("-" * 60)
    print(f"SSP 最小费用：{total_cost}")


    # =========================================================
    # 3. Validator
    # =========================================================

    capacity_ok = check_capacity(
        flow,
        capacity,
    )

    conservation_ok = check_flow_conservation(
        nodes,
        arcs,
        flow,
        source,
        sink,
        required_flow,
    )

    objective_ok = check_objective(
        arcs,
        flow,
        cost,
        total_cost,
    )


    print("\n结果验证")
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


    # =========================================================
    # 4. Gurobi 交叉验证
    # =========================================================

    print("\n")
    print("=" * 60)
    print("Gurobi 交叉验证")
    print("=" * 60)

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
        print("Gurobi 未找到最优解")
        return


    gurobi_flow, gurobi_cost = gurobi_result


    # =========================================================
    # 5. 输出 Gurobi 结果
    # =========================================================

    print("\nGurobi 最优流")
    print("-" * 60)

    for arc in arcs:
        print(
            f"弧 {arc}: "
            f"flow = {gurobi_flow[arc]}"
        )

    print("-" * 60)

    print(f"Gurobi 最优费用：{gurobi_cost}")


    # =========================================================
    # 6. SSP 与 Gurobi 对比
    # =========================================================

    same_objective = math.isclose(
        total_cost,
        gurobi_cost,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )


    print("\n算法对比")
    print("-" * 60)

    print(f"SSP 最优费用：     {total_cost}")
    print(f"Gurobi 最优费用：  {gurobi_cost}")

    print(
        "目标值一致：",
        "PASS" if same_objective else "FAIL"
    )


    # =========================================================
    # 7. 总体验证结果
    # =========================================================

    all_passed = (
        capacity_ok
        and conservation_ok
        and objective_ok
        and same_objective
    )


    print("\n")
    print("=" * 60)

    if all_passed:
        print("所有检查均通过：PASS")
    else:
        print("存在检查未通过：FAIL")

    print("=" * 60)


if __name__ == "__main__":
    main()