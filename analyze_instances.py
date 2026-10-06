import csv
import math
import statistics
from pathlib import Path

import matplotlib.pyplot as plt


# ============================================================
# 项目目录
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent


# ============================================================
# 1. 读取逐实例实验数据
# ============================================================

def load_instance_results(
    filename="instance_results.csv",
):
    """
    读取逐实例实验结果。

    返回：
        一个由字典组成的列表。
    """

    results = []

    with open(
        filename,
        "r",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            results.append(
                {
                    "num_nodes": int(
                        row["num_nodes"]
                    ),

                    "num_arcs": int(
                        row["num_arcs"]
                    ),

                    "seed": int(
                        row["seed"]
                    ),

                    "ssp_cost": float(
                        row["ssp_cost"]
                    ),

                    "gurobi_cost": float(
                        row["gurobi_cost"]
                    ),

                    "ssp_runtime": float(
                        row["ssp_runtime"]
                    ),

                    "gurobi_runtime": float(
                        row["gurobi_runtime"]
                    ),

                    "augmentation_count": int(
                        row["augmentation_count"]
                    ),

                    "same_objective": (
                        row["same_objective"]
                        == "True"
                    ),
                }
            )

    return results


# ============================================================
# 2. Pearson 相关系数
# ============================================================

def pearson_correlation(x, y):
    """
    手工计算 Pearson 相关系数。

    r > 0：
        正相关

    r < 0：
        负相关

    r ≈ 0：
        线性相关性较弱
    """

    if len(x) != len(y):
        raise ValueError(
            "x 和 y 的长度必须相同"
        )

    if len(x) < 2:
        raise ValueError(
            "至少需要两个数据点"
        )

    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)

    numerator = 0.0

    denominator_x = 0.0
    denominator_y = 0.0

    for xi, yi in zip(x, y):

        dx = xi - mean_x
        dy = yi - mean_y

        numerator += dx * dy

        denominator_x += dx ** 2
        denominator_y += dy ** 2

    denominator = math.sqrt(
        denominator_x * denominator_y
    )

    if denominator == 0:
        return float("nan")

    return numerator / denominator


# ============================================================
# 3. 按节点规模分组
# ============================================================

def group_by_size(results):
    """
    按 num_nodes 对实验结果进行分组。
    """

    grouped = {}

    for result in results:

        n = result["num_nodes"]

        if n not in grouped:
            grouped[n] = []

        grouped[n].append(result)

    return grouped


# ============================================================
# 4. 总体相关性分析
# ============================================================

def analyze_overall_correlation(results):

    augmentation_counts = [
        result["augmentation_count"]
        for result in results
    ]

    ssp_runtimes = [
        result["ssp_runtime"]
        for result in results
    ]

    correlation = pearson_correlation(
        augmentation_counts,
        ssp_runtimes,
    )

    return correlation


# ============================================================
# 5. 固定网络规模下分析相关性
# ============================================================

def analyze_correlation_by_size(results):

    grouped = group_by_size(results)

    correlations = {}

    for num_nodes, group in sorted(
        grouped.items()
    ):

        augmentation_counts = [
            result["augmentation_count"]
            for result in group
        ]

        ssp_runtimes = [
            result["ssp_runtime"]
            for result in group
        ]

        # 如果所有实例增广次数完全相同，
        # Pearson 相关系数没有定义。
        if len(
            set(augmentation_counts)
        ) <= 1:
            correlations[num_nodes] = float(
                "nan"
            )
            continue

        correlations[num_nodes] = (
            pearson_correlation(
                augmentation_counts,
                ssp_runtimes,
            )
        )

    return correlations


# ============================================================
# 6. 输出基本统计信息
# ============================================================

def print_basic_statistics(results):

    augmentation_counts = [
        result["augmentation_count"]
        for result in results
    ]

    ssp_runtimes = [
        result["ssp_runtime"]
        for result in results
    ]

    print("=" * 70)
    print("逐实例数据基本统计")
    print("=" * 70)

    print(
        f"实例数量："
        f"{len(results)}"
    )

    print(
        f"平均增广次数："
        f"{statistics.mean(augmentation_counts):.3f}"
    )

    print(
        f"最小增广次数："
        f"{min(augmentation_counts)}"
    )

    print(
        f"最大增广次数："
        f"{max(augmentation_counts)}"
    )

    print(
        f"平均 SSP 时间："
        f"{statistics.mean(ssp_runtimes):.6f} s"
    )


# ============================================================
# 7. 打印相关系数
# ============================================================

def print_correlation_results(results):

    overall_r = analyze_overall_correlation(
        results
    )

    correlations_by_size = (
        analyze_correlation_by_size(
            results
        )
    )

    print("\n")
    print("=" * 70)
    print("增广次数与 SSP Runtime 的 Pearson 相关性")
    print("=" * 70)

    print(
        f"所有实例总体相关系数："
        f"r = {overall_r:.4f}"
    )

    print("\n固定网络规模后的相关系数：")

    for num_nodes, r in (
        correlations_by_size.items()
    ):

        if math.isnan(r):

            print(
                f"|V| = {num_nodes}: "
                f"无法计算"
            )

        else:

            print(
                f"|V| = {num_nodes}: "
                f"r = {r:.4f}"
            )


# ============================================================
# 8. 绘制总体散点图
# ============================================================

def plot_overall_scatter(results):

    augmentation_counts = [
        result["augmentation_count"]
        for result in results
    ]

    ssp_runtimes = [
        result["ssp_runtime"]
        for result in results
    ]

    plt.figure(
        figsize=(8, 5)
    )

    plt.scatter(
        augmentation_counts,
        ssp_runtimes,
    )

    plt.xlabel(
        "Augmentation Count"
    )

    plt.ylabel(
        "SSP Runtime (seconds)"
    )

    plt.title(
        "Augmentation Count vs SSP Runtime"
    )

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
    PROJECT_DIR / "augmentation_vs_runtime.png",
    dpi=300,
    )

    plt.show()


# ============================================================
# 9. 固定规模分别画散点图
# ============================================================

def plot_scatter_by_size(results):

    grouped = group_by_size(results)

    for num_nodes, group in sorted(
        grouped.items()
    ):

        augmentation_counts = [
            result["augmentation_count"]
            for result in group
        ]

        ssp_runtimes = [
            result["ssp_runtime"]
            for result in group
        ]

        plt.figure(
            figsize=(8, 5)
        )

        plt.scatter(
            augmentation_counts,
            ssp_runtimes,
        )

        plt.xlabel(
            "Augmentation Count"
        )

        plt.ylabel(
            "SSP Runtime (seconds)"
        )

        plt.title(
            f"Augmentation Count vs SSP Runtime "
            f"(|V| = {num_nodes})"
        )

        plt.grid(True)

        plt.tight_layout()

        filename = PROJECT_DIR / (
        f"augmentation_vs_runtime_"
        f"n{num_nodes}.png"
        )

        plt.savefig(
            filename,
            dpi=300,
        )

        plt.close()


# ============================================================
# 10. 主程序
# ============================================================

def main():

    # --------------------------------------------------------
    # 读取 instance_results.csv
    # --------------------------------------------------------

    instance_file = (
    PROJECT_DIR / "instance_results.csv"
)

    print(
        "正在读取数据文件：",
        instance_file
    )

    results = load_instance_results(
        instance_file
    )

        # --------------------------------------------------------
        # 基本统计
        # --------------------------------------------------------

    print_basic_statistics(
        results
    )

    # --------------------------------------------------------
    # Pearson 相关性
    # --------------------------------------------------------

    print_correlation_results(
        results
    )

    # --------------------------------------------------------
    # 总体散点图
    # --------------------------------------------------------

    plot_overall_scatter(
        results
    )

    # --------------------------------------------------------
    # 各规模单独画图
    # --------------------------------------------------------

    plot_scatter_by_size(
        results
    )

    print("\n")
    print("=" * 70)
    print("分析完成")
    print("=" * 70)

    print(
        "已生成总体散点图："
        "augmentation_vs_runtime.png"
    )

    print(
        "已生成各网络规模对应的散点图。"
    )


# ============================================================
# 11. 程序入口
# ============================================================

if __name__ == "__main__":
    main()