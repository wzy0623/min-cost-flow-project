import csv
import matplotlib.pyplot as plt


# ==========================================
# 1. 读取实验结果
# ==========================================

num_nodes = []

ssp_mean = []
ssp_std = []

gurobi_mean = []
gurobi_std = []


with open(
    "experiment_results.csv",
    "r",
    encoding="utf-8",
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        num_nodes.append(
            int(row["num_nodes"])
        )

        ssp_mean.append(
            float(row["ssp_mean"])
        )

        ssp_std.append(
            float(row["ssp_std"])
        )

        gurobi_mean.append(
            float(row["gurobi_mean"])
        )

        gurobi_std.append(
            float(row["gurobi_std"])
        )


# ==========================================
# 2. 创建图像
# ==========================================

plt.figure(
    figsize=(8, 5)
)


# ==========================================
# 3. SSP 曲线
# ==========================================

plt.errorbar(
    num_nodes,
    ssp_mean,
    yerr=ssp_std,
    marker="o",
    capsize=4,
    label="SSP",
)


# ==========================================
# 4. Gurobi 曲线
# ==========================================

plt.errorbar(
    num_nodes,
    gurobi_mean,
    yerr=gurobi_std,
    marker="o",
    capsize=4,
    label="Gurobi",
)


# ==========================================
# 5. 图像设置
# ==========================================

plt.xlabel(
    "Number of Nodes |V|"
)

plt.ylabel(
    "Runtime (seconds)"
)

plt.title(
    "Minimum-Cost Flow Runtime Scaling"
)

plt.legend()

plt.grid(True)

plt.tight_layout()


# ==========================================
# 6. 保存图片
# ==========================================

plt.savefig(
    "runtime_scaling.png",
    dpi=300,
)


# ==========================================
# 7. 显示图片
# ==========================================

plt.show()