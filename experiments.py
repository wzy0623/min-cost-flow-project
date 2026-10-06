import csv
import math
import statistics
import time
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent

from random_instance import generate_random_instance

from min_cost_flow import (
    min_cost_flow_with_potential,
)

from gurobi_solver import (
    solve_with_gurobi,
)


# ============================================================
# 1. 单个随机实例实验
# ============================================================

def run_single_experiment(
    num_nodes,
    num_arcs,
    required_flow,
    seed,
):
    """
    在同一个随机网络实例上：

    1. 运行自己实现的 SSP；
    2. 运行 Gurobi；
    3. 比较两者最优目标值；
    4. 记录 SSP 增广次数；
    5. 记录两种方法运行时间。

    返回一个字典。
    """

    # --------------------------------------------------------
    # 生成随机实例
    # --------------------------------------------------------

    (
        nodes,
        arcs,
        capacity,
        cost,
        source,
        sink,
        required_flow,
    ) = generate_random_instance(
        num_nodes=num_nodes,
        num_arcs=num_arcs,
        required_flow=required_flow,
        seed=seed,
    )

    # ========================================================
    # SSP
    # ========================================================

    # ========================================================
# SSP
#
# 同一个实例重复运行多次，
# 使用中位数作为该实例的 runtime。
# 这样可以降低偶发系统噪声对计时的影响。
# ========================================================

    ssp_repeat = 10

    ssp_runtimes = []

    ssp_result = None


    for _ in range(ssp_repeat):

        start_time = time.perf_counter()

        current_result = min_cost_flow_with_potential(
            nodes=nodes,
            arcs=arcs,
            capacity=capacity,
            cost=cost,
            source=source,
            sink=sink,
            required_flow=required_flow,
            verbose=False,
            return_stats=True,
        )

        runtime = (
            time.perf_counter()
            - start_time
        )

        ssp_runtimes.append(
            runtime
        )

    # 每一次运行求的是完全相同的实例，
    # 因此只需要保留一次求解结果。
    if ssp_result is None:
        ssp_result = current_result


    ssp_runtime = statistics.median(
        ssp_runtimes
    )


    if ssp_result is None:
        raise RuntimeError(
            f"SSP 未找到可行解："
            f"|V|={num_nodes}, "
            f"|A|={num_arcs}, "
            f"seed={seed}"
        )


    _, ssp_cost, ssp_stats = ssp_result

    augmentation_count = ssp_stats[
            "augmentation_count"
        ]

    # ========================================================
    # Gurobi
    # ========================================================

    start_time = time.perf_counter()

    gurobi_result = solve_with_gurobi(
        nodes=nodes,
        arcs=arcs,
        capacity=capacity,
        cost=cost,
        source=source,
        sink=sink,
        required_flow=required_flow,
    )

    gurobi_runtime = time.perf_counter() - start_time

    if gurobi_result is None:
        raise RuntimeError(
            f"Gurobi 未找到可行解："
            f"|V|={num_nodes}, "
            f"|A|={num_arcs}, "
            f"seed={seed}"
        )

    _, gurobi_cost = gurobi_result

    # ========================================================
    # SSP 与 Gurobi 正确性比较
    # ========================================================

    same_objective = math.isclose(
        ssp_cost,
        gurobi_cost,
        rel_tol=1e-9,
        abs_tol=1e-9,
    )

    # ========================================================
    # 返回单个实例的原始数据
    # ========================================================

    return {
        "num_nodes": num_nodes,
        "num_arcs": num_arcs,
        "seed": seed,

        "ssp_cost": ssp_cost,
        "gurobi_cost": gurobi_cost,

        "ssp_runtime": ssp_runtime,
        "gurobi_runtime": gurobi_runtime,

        "augmentation_count": augmentation_count,

        "same_objective": same_objective,
    }


# ============================================================
# 2. 固定规模下运行多个随机实例
# ============================================================

def run_size_experiment(
    num_nodes,
    num_arcs,
    required_flow,
    seeds,
):
    """
    对同一个网络规模运行多个随机实例。

    例如：

        |V| = 100
        |A| = 400

    然后 seed = 0, 1, ..., 9。

    最终计算：

    - SSP 平均运行时间
    - SSP 运行时间标准差
    - Gurobi 平均运行时间
    - Gurobi 运行时间标准差
    - 平均增广次数
    - 增广次数标准差
    - 所有实例是否与 Gurobi 目标值一致

    同时保留每一个实例的原始数据。
    """

    ssp_times = []
    gurobi_times = []
    augmentation_counts = []

    instance_results = []

    all_correct = True

    # --------------------------------------------------------
    # 对每个随机种子分别实验
    # --------------------------------------------------------

    for seed in seeds:

        result = run_single_experiment(
            num_nodes=num_nodes,
            num_arcs=num_arcs,
            required_flow=required_flow,
            seed=seed,
        )

        # 保存 SSP 时间
        ssp_times.append(
            result["ssp_runtime"]
        )

        # 保存 Gurobi 时间
        gurobi_times.append(
            result["gurobi_runtime"]
        )

        # 保存 SSP 增广次数
        augmentation_counts.append(
            result["augmentation_count"]
        )

        # 保存单个实例的完整原始数据
        instance_results.append(result)

        # 检查 SSP 与 Gurobi 是否一致
        if not result["same_objective"]:
            all_correct = False

    # --------------------------------------------------------
    # 计算该规模的统计结果
    # --------------------------------------------------------

    summary = {
        "num_nodes": num_nodes,
        "num_arcs": num_arcs,

        "ssp_mean": statistics.mean(
            ssp_times
        ),

        "ssp_std": statistics.stdev(
            ssp_times
        ),

        "gurobi_mean": statistics.mean(
            gurobi_times
        ),

        "gurobi_std": statistics.stdev(
            gurobi_times
        ),

        "augmentation_mean": statistics.mean(
            augmentation_counts
        ),

        "augmentation_std": statistics.stdev(
            augmentation_counts
        ),

        "all_correct": all_correct,
    }

    return summary, instance_results


# ============================================================
# 3. 保存规模汇总结果
# ============================================================

def save_summary_results(
    summary_results,
    filename=PROJECT_DIR / "experiment_results.csv",
):
    """
    保存每个网络规模的 Mean / Std 汇总结果。
    """

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "num_nodes",
            "num_arcs",
            "ssp_mean",
            "ssp_std",
            "gurobi_mean",
            "gurobi_std",
            "augmentation_mean",
            "augmentation_std",
            "all_correct",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for result in summary_results:
            writer.writerow(result)


# ============================================================
# 4. 保存逐实例原始结果
# ============================================================

def save_instance_results(
    all_instance_results,
    filename=PROJECT_DIR / "instance_results.csv",
    ):
    """
    保存每一个随机实例的原始实验数据。

    后续可以使用这个文件研究：

        augmentation_count
                VS
        SSP runtime
    """

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "num_nodes",
            "num_arcs",
            "seed",
            "ssp_cost",
            "gurobi_cost",
            "ssp_runtime",
            "gurobi_runtime",
            "augmentation_count",
            "same_objective",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for result in all_instance_results:
            writer.writerow(result)


# ============================================================
# 5. 主程序
# ============================================================

def main():

    # --------------------------------------------------------
    # 实验参数
    # --------------------------------------------------------

    test_sizes = [
        20,
        50,
        100,
        200,
    ]

    # 每个网络中需要发送的流量
    required_flow = 10

    # 每个规模测试 10 个随机实例
    seeds = list(range(50))

    # 保存规模汇总结果
    summary_results = []

    # 保存所有单个实例的原始结果
    all_instance_results = []

    # ========================================================
    # Gurobi Warm-up
    # ========================================================

    print("=" * 80)
    print("正在进行 Gurobi warm-up...")
    print("=" * 80)

    run_single_experiment(
        num_nodes=10,
        num_arcs=20,
        required_flow=5,
        seed=999,
    )

    print("Warm-up 完成\n")

    # ========================================================
    # 正式实验
    # ========================================================

    for num_nodes in test_sizes:

        # 当前实验使用稀疏网络：
        #
        # |A| = 4 |V|

        num_arcs = 4 * num_nodes

        print("=" * 80)

        print(
            f"测试规模："
            f"|V| = {num_nodes}, "
            f"|A| = {num_arcs}"
        )

        # ----------------------------------------------------
        # 对当前规模运行 10 个随机实例
        # ----------------------------------------------------

        (
            summary,
            instance_results,
        ) = run_size_experiment(
            num_nodes=num_nodes,
            num_arcs=num_arcs,
            required_flow=required_flow,
            seeds=seeds,
        )

        # 保存当前规模汇总结果
        summary_results.append(summary)

        # 保存当前规模所有原始实例
        all_instance_results.extend(
            instance_results
        )

        # ----------------------------------------------------
        # 输出当前规模结果
        # ----------------------------------------------------

        print(
            f"SSP 平均时间："
            f"{summary['ssp_mean']:.6f} s"
        )

        print(
            f"SSP 标准差："
            f"{summary['ssp_std']:.6f}"
        )

        print(
            f"Gurobi 平均时间："
            f"{summary['gurobi_mean']:.6f} s"
        )

        print(
            f"Gurobi 标准差："
            f"{summary['gurobi_std']:.6f}"
        )

        print(
            f"平均增广次数："
            f"{summary['augmentation_mean']:.2f}"
        )

        print(
            f"增广次数标准差："
            f"{summary['augmentation_std']:.2f}"
        )

        print(
            "10 个实例目标值全部一致：",
            "PASS"
            if summary["all_correct"]
            else "FAIL"
        )

        print()

    # ========================================================
    # 打印最终汇总表
    # ========================================================

    print("\n")
    print("=" * 135)
    print("多实例性能实验汇总")
    print("=" * 135)

    print(
        f"{'|V|':>8}"
        f"{'|A|':>10}"
        f"{'SSP mean':>16}"
        f"{'SSP std':>16}"
        f"{'GRB mean':>16}"
        f"{'GRB std':>16}"
        f"{'Aug mean':>14}"
        f"{'Aug std':>14}"
        f"{'正确性':>12}"
    )

    print("-" * 135)

    for result in summary_results:

        consistency = (
            "PASS"
            if result["all_correct"]
            else "FAIL"
        )

        print(
            f"{result['num_nodes']:>8}"
            f"{result['num_arcs']:>10}"
            f"{result['ssp_mean']:>16.6f}"
            f"{result['ssp_std']:>16.6f}"
            f"{result['gurobi_mean']:>16.6f}"
            f"{result['gurobi_std']:>16.6f}"
            f"{result['augmentation_mean']:>14.2f}"
            f"{result['augmentation_std']:>14.2f}"
            f"{consistency:>12}"
        )

    # ========================================================
    # 保存 CSV
    # ========================================================

    save_summary_results(
        summary_results,
        filename="experiment_results.csv",
    )

    save_instance_results(
        all_instance_results,
        filename="instance_results.csv",
    )

    # ========================================================
    # 最终提示
    # ========================================================

    print("\n")
    print("=" * 80)
    print("实验完成")
    print("=" * 80)

    print(
        "规模汇总结果已保存到："
        "experiment_results.csv"
    )

    print(
        "逐实例原始结果已保存到："
        "instance_results.csv"
    )

    print(
        f"总共完成随机实例数量："
        f"{len(all_instance_results)}"
    )


# ============================================================
# 6. 程序入口
# ============================================================

if __name__ == "__main__":
    main()