import math
import statistics
import time
from pathlib import Path

import matplotlib.pyplot as plt

from min_cost_flow import (
    min_cost_flow_with_potential,
)


PROJECT_DIR = Path(__file__).resolve().parent


# ============================================================
# 1. 构造受控网络
# ============================================================

def generate_controlled_network(
    num_paths=30,
):
    """
    构造 num_paths 条彼此独立的 s-t 路径：

        source -> intermediate node -> sink

    每条路径容量为 1。

    因此如果要求发送 F 单位流，
    SSP 理论上需要进行 F 次增广。
    """

    source = 0

    intermediate_nodes = list(
        range(1, num_paths + 1)
    )

    sink = num_paths + 1

    nodes = [
        source,
        *intermediate_nodes,
        sink,
    ]

    arcs = []

    capacity = {}
    cost = {}

    for i in intermediate_nodes:

        # source -> i
        arc_1 = (source, i)

        arcs.append(arc_1)

        capacity[arc_1] = 1

        # 不同路径设置不同费用
        cost[arc_1] = i

        # i -> sink
        arc_2 = (i, sink)

        arcs.append(arc_2)

        capacity[arc_2] = 1

        cost[arc_2] = 1

    return (
        nodes,
        arcs,
        capacity,
        cost,
        source,
        sink,
    )


# ============================================================
# 2. 单个 required_flow 实验
# ============================================================

def run_experiment(
    required_flow,
    repeat=30,
):
    """
    对同一个受控实例重复运行 SSP。

    使用中位数 runtime，
    降低偶发系统噪声的影响。
    """

    (
        nodes,
        arcs,
        capacity,
        cost,
        source,
        sink,
    ) = generate_controlled_network(
        num_paths=30
    )

    runtimes = []

    augmentation_count = None

    for _ in range(repeat):

        start_time = time.perf_counter()

        result = min_cost_flow_with_potential(
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

        runtimes.append(runtime)

        if result is None:
            raise RuntimeError(
                "SSP 未找到可行解"
            )

        _, _, stats = result

        augmentation_count = stats[
            "augmentation_count"
        ]

    median_runtime = statistics.median(
        runtimes
    )

    return {
        "required_flow": required_flow,
        "augmentation_count": augmentation_count,
        "median_runtime": median_runtime,
    }


# ============================================================
# 3. 简单线性回归
# ============================================================

def linear_regression(x, y):
    """
    拟合：

        y = intercept + slope * x

    并计算 R^2。
    """

    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)

    numerator = sum(
        (xi - mean_x) * (yi - mean_y)
        for xi, yi in zip(x, y)
    )

    denominator = sum(
        (xi - mean_x) ** 2
        for xi in x
    )

    if denominator == 0:
        raise ValueError(
            "x 没有变化，无法进行线性回归"
        )

    slope = numerator / denominator

    intercept = (
        mean_y
        - slope * mean_x
    )

    predicted_y = [
        intercept + slope * xi
        for xi in x
    ]

    ss_res = sum(
        (yi - y_hat) ** 2
        for yi, y_hat in zip(
            y,
            predicted_y,
        )
    )

    ss_tot = sum(
        (yi - mean_y) ** 2
        for yi in y
    )

    if ss_tot == 0:
        r_squared = float("nan")
    else:
        r_squared = (
            1 - ss_res / ss_tot
        )

    return (
        slope,
        intercept,
        r_squared,
        predicted_y,
    )


# ============================================================
# 4. 主实验
# ============================================================

def main():

    required_flows = [
        1,
        2,
        5,
        10,
        15,
        20,
        25,
        30,
    ]

    results = []

    print("=" * 75)
    print("Controlled Augmentation Experiment")
    print("=" * 75)

    print(
        "固定网络：|V| = 32, |A| = 60"
    )

    print(
        "每条 s-t 路径容量 = 1"
    )

    print()

    # ========================================================
    # 运行实验
    # ========================================================

    for required_flow in required_flows:

        result = run_experiment(
            required_flow=required_flow,
            repeat=30,
        )

        results.append(result)

        print(
            f"F = {required_flow:>2}, "
            f"K = {result['augmentation_count']:>2}, "
            f"median runtime = "
            f"{result['median_runtime']:.6f} s"
        )

    # ========================================================
    # 提取数据
    # ========================================================

    augmentation_counts = [
        result["augmentation_count"]
        for result in results
    ]

    runtimes = [
        result["median_runtime"]
        for result in results
    ]

    # ========================================================
    # 线性回归
    # ========================================================

    (
        slope,
        intercept,
        r_squared,
        predicted_runtimes,
    ) = linear_regression(
        augmentation_counts,
        runtimes,
    )

    print()
    print("=" * 75)
    print("线性回归结果")
    print("=" * 75)

    print(
        f"slope = {slope:.10f}"
    )

    print(
        f"intercept = {intercept:.10f}"
    )

    print(
        f"R^2 = {r_squared:.6f}"
    )

    print()

    print(
        "拟合模型："
    )

    print(
        f"T ≈ {intercept:.8f} "
        f"+ {slope:.8f} K"
    )

    # ========================================================
    # 绘图
    # ========================================================

    plt.figure(
        figsize=(8, 5)
    )

    # 实验数据
    plt.scatter(
        augmentation_counts,
        runtimes,
        label="Observed runtime",
    )

    # 回归线
    plt.plot(
        augmentation_counts,
        predicted_runtimes,
        label=(
            f"Linear fit "
            f"($R^2$ = {r_squared:.3f})"
        ),
    )

    plt.xlabel(
        "Augmentation Count K"
    )

    plt.ylabel(
        "Median SSP Runtime (seconds)"
    )

    plt.title(
        "Controlled SSP Runtime vs Augmentation Count"
    )

    plt.legend()

    plt.grid(True)

    plt.tight_layout()

    output_path = (
        PROJECT_DIR
        / "controlled_runtime_vs_augmentation.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
    )

    plt.show()

    # ========================================================
    # 完成
    # ========================================================

    print()
    print("=" * 75)
    print("实验完成")
    print("=" * 75)

    print(
        "图像已保存到：",
        output_path,
    )


if __name__ == "__main__":
    main()