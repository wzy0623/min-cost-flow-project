# 最小费用流算法项目

本项目使用 Python 实现 **最小费用流问题（Minimum-Cost Flow Problem）**。

当前核心算法采用：

- 逐次最短路算法（Successive Shortest Path, SSP）
- 残量网络（Residual Network）
- 节点势函数（Potential）
- 约化费用（Reduced Cost）
- 基于最小堆的 Dijkstra 最短路算法

本项目不仅希望得到最小费用流问题的最优解，还希望通过从底层实现算法，理解以下概念之间的关系：

$$
\text{原始网络}
\rightarrow
\text{残量网络}
\rightarrow
\text{最短增广路}
\rightarrow
\text{流量增广}
\rightarrow
\text{Potential}
\rightarrow
\text{Reduced Cost}
$$

最终目标是逐步将项目扩展为一个完整的 **组合优化算法学习与实验项目**。

---

## 1. 问题定义

给定一个有向网络

$$
G=(V,A),
$$

其中：

- $V$：节点集合；
- $A$：有向弧集合；
- $u_{uv}$：弧 $(u,v)$ 的容量；
- $c_{uv}$：弧 $(u,v)$ 的单位费用；
- $x_{uv}$：弧 $(u,v)$ 上的实际流量。

给定源点 $s$、汇点 $t$ 和需要发送的总流量 $F$。

目标是在满足容量约束和流守恒约束的前提下，使总运输费用最小。

目标函数为：

$$
\min
\sum_{(u,v)\in A}
c_{uv}x_{uv}.
$$

---

## 2. 约束条件

### 2.1 容量约束

对于任意弧 $(u,v)\in A$，需要满足：

$$
0\le x_{uv}\le u_{uv}.
$$

也就是说，一条弧上的流量：

- 不能为负；
- 不能超过该弧容量。

---

### 2.2 流守恒约束

对于所有中间节点

$$
v\in V\setminus\{s,t\},
$$

要求：

$$
\sum_{(u,v)\in A}x_{uv}
=
\sum_{(v,w)\in A}x_{vw}.
$$

即：

$$
\text{流入}=\text{流出}.
$$

对于源点 $s$：

$$
\text{流出}-\text{流入}=F.
$$

对于汇点 $t$：

$$
\text{流入}-\text{流出}=F.
$$

---

## 3. 算法总体思路

本项目采用 **逐次最短路算法（Successive Shortest Path Algorithm）**。

算法的基本流程为：

1. 初始化所有弧的流量为 $0$；
2. 根据当前流量构造残量网络；
3. 根据节点势函数计算约化费用；
4. 在约化费用下使用 Dijkstra 算法寻找最短增广路；
5. 根据 `parent` 恢复最短路径；
6. 找到路径上的最小残量容量；
7. 沿最短路径进行流量增广；
8. 更新节点势函数；
9. 重新构造残量网络；
10. 重复上述过程，直到发送完要求的总流量 $F$。

算法整体流程可以表示为：

```text
原始网络
   ↓
初始化 flow
   ↓
构造残量网络
   ↓
计算 Reduced Cost
   ↓
Heap-Dijkstra
   ↓
恢复最短增广路
   ↓
计算瓶颈容量 Δ
   ↓
沿路径增广
   ↓
更新 Potential
   ↓
是否已经发送 F 单位流量？
   ├── 否 → 重新构造残量网络
   └── 是 → 输出最终流和总费用
```

---

## 4. 残量网络

残量网络用于描述：

> 在当前流量解的基础上，还允许怎样修改当前流。

对于原网络中的一条弧

$$
(u,v),
$$

容量为 $u_{uv}$，当前流量为 $x_{uv}$。

---

### 4.1 正向残量弧

如果：

$$
x_{uv}<u_{uv},
$$

说明弧 $(u,v)$ 还没有达到容量上限，因此还可以继续增加流量。

此时残量网络中存在正向残量弧：

$$
u\rightarrow v.
$$

其残量容量为：

$$
r_{uv}
=
u_{uv}-x_{uv}.
$$

其残量费用为：

$$
c^R_{uv}=c_{uv}.
$$

---

### 4.2 反向残量弧

如果：

$$
x_{uv}>0,
$$

说明之前已经沿 $(u,v)$ 发送了一部分流量，因此允许撤销之前的部分决策。

此时残量网络中存在反向残量弧：

$$
v\rightarrow u.
$$

其残量容量为：

$$
r_{vu}=x_{uv}.
$$

其残量费用为：

$$
c^R_{vu}=-c_{uv}.
$$

反向残量弧的作用可以理解为：

$$
\boxed{\text{允许算法撤销之前已经发送的流量}}
$$

这使算法能够不断修正当前解。

---

## 5. 最短增广路

在当前残量网络中，需要寻找一条从源点 $s$ 到汇点 $t$ 的最短费用路径。

假设当前最短增广路径为：

$$
P.
$$

那么路径的单位费用为：

$$
c(P)
=
\sum_{(u,v)\in P}
c^R_{uv}.
$$

算法沿当前最短路径尽可能多地发送流量。

---

## 6. 瓶颈容量

对于最短增广路径 $P$，其最大可增广流量由路径中最小的残量容量决定。

定义：

$$
\Delta
=
\min_{(u,v)\in P}
r_{uv}.
$$

其中 $\Delta$ 称为当前增广路径的 **瓶颈容量**。

如果剩余需要发送的流量小于 $\Delta$，则实际增广量取：

$$
\Delta
=
\min
\left\{
\text{路径瓶颈容量},
\text{剩余需要发送的流量}
\right\}.
$$

---

## 7. 流量更新

如果增广路径经过正向残量弧：

$$
u\rightarrow v,
$$

则更新：

$$
x_{uv}
\leftarrow
x_{uv}+\Delta.
$$

如果增广路径经过反向残量弧：

$$
v\rightarrow u,
$$

则表示撤销原弧 $(u,v)$ 上的一部分流量：

$$
x_{uv}
\leftarrow
x_{uv}-\Delta.
$$

---

## 8. 为什么不能直接使用普通 Dijkstra？

由于残量网络中的反向弧费用满足：

$$
c^R_{vu}=-c_{uv},
$$

因此残量网络可能存在负费用弧。

而普通 Dijkstra 算法要求：

$$
c_{uv}\ge0.
$$

所以不能直接在原始残量费用上使用 Dijkstra。

为解决这个问题，引入 **节点势函数（Potential）** 和 **约化费用（Reduced Cost）**。

---

## 9. 节点势函数

为每个节点 $v$ 维护一个节点势：

$$
p(v).
$$

在原始弧费用基础上定义约化费用：

$$
c_p(u,v)
=
c(u,v)+p(u)-p(v).
$$

在残量网络中则使用：

$$
c_p^R(u,v)
=
c^R(u,v)+p(u)-p(v).
$$

算法维护节点势，使当前可用残量弧满足：

$$
c_p^R(u,v)\ge0.
$$

这样就可以继续使用 Dijkstra 算法。

---

## 10. 为什么约化费用不会改变最短路径？

假设一条从 $s$ 到 $t$ 的路径为：

$$
P:
s=v_0
\rightarrow
v_1
\rightarrow
\cdots
\rightarrow
v_k=t.
$$

路径的约化费用为：

$$
c_p(P)
=
\sum_{i=0}^{k-1}
\left(
c(v_i,v_{i+1})
+
p(v_i)
-
p(v_{i+1})
\right).
$$

展开后，中间节点的势函数会相互抵消，因此：

$$
c_p(P)
=
c(P)+p(s)-p(t).
$$

对于所有从 $s$ 到 $t$ 的路径：

$$
p(s)-p(t)
$$

都是同一个常数。

因此：

$$
\arg\min_P c(P)
=
\arg\min_P c_p(P).
$$

也就是说：

$$
\boxed{\text{约化费用不会改变最短路径的选择}}
$$

---

## 11. Potential 更新

Dijkstra 在约化费用下得到从源点到各节点的最短距离：

$$
d_p(v).
$$

然后更新节点势：

$$
p(v)
\leftarrow
p(v)+d_p(v).
$$

更新后的约化费用满足：

$$
c_{p'}(u,v)
=
c_p(u,v)
+
d_p(u)
-
d_p(v).
$$

由于最短距离满足：

$$
d_p(v)
\le
d_p(u)+c_p(u,v),
$$

因此：

$$
c_{p'}(u,v)\ge0.
$$

这样下一轮仍然可以使用 Dijkstra。

---

## 12. 最短路径上的约化费用

如果弧 $(u,v)$ 位于当前最短路径上，那么：

$$
d_p(v)
=
d_p(u)+c_p(u,v).
$$

因此 Potential 更新后：

$$
c_{p'}(u,v)
=
0.
$$

即：

$$
\boxed{\text{当前最短路径上的弧会变成零约化费用弧}}
$$

这也保证了增广后新产生的反向弧不会破坏 Dijkstra 对非负边权的要求。

---

## 13. 项目结构

当前项目结构为：

```text
min-cost-flow-project/
│
├── main.py
├── min_cost_flow.py
├── examples.py
├── README.md
└── .gitignore
```

---

### 13.1 `main.py`

程序入口。

主要负责：

- 读取测试网络；
- 调用最小费用流算法；
- 输出最终流量；
- 输出最小费用；
- 调用 Validator 检查算法结果。

---

### 13.2 `min_cost_flow.py`

存放核心算法。

当前主要包括：

- 残量网络构造；
- Dijkstra 最短路；
- 最小堆 Priority Queue；
- Potential；
- Reduced Cost；
- 路径恢复；
- 增广操作；
- Successive Shortest Path；
- 容量约束验证；
- 流守恒验证；
- 目标函数验证。

---

### 13.3 `examples.py`

存放测试网络实例。

主要包括：

- `nodes`
- `arcs`
- `capacity`
- `cost`
- `source`
- `sink`
- `required_flow`

---

### 13.4 `README.md`

记录：

- 问题定义；
- 算法原理；
- 项目结构；
- 测试实例；
- 项目运行方式；
- 后续开发计划。

---

### 13.5 `.gitignore`

用于忽略不需要上传到 GitHub 的文件，例如：

```text
__pycache__/
*.pyc
.DS_Store
.vscode/
```

---

# 14. 当前测试实例

当前测试网络的节点集合为：

$$
V=\{1,2,3,4\}.
$$

弧集合为：

$$
A=
\{
(1,2),
(1,3),
(2,4),
(3,4)
\}.
$$

容量为：

$$
u_{12}=5,
$$

$$
u_{13}=4,
$$

$$
u_{24}=3,
$$

$$
u_{34}=5.
$$

单位费用为：

$$
c_{12}=1,
$$

$$
c_{13}=4,
$$

$$
c_{24}=1,
$$

$$
c_{34}=2.
$$

源点为：

$$
s=1.
$$

汇点为：

$$
t=4.
$$

需要发送的总流量为：

$$
F=5.
$$

---

## 15. 当前测试结果

算法最终得到：

$$
x_{12}=3,
$$

$$
x_{13}=2,
$$

$$
x_{24}=3,
$$

$$
x_{34}=2.
$$

因此总费用为：

$$
\begin{aligned}
C
&=
c_{12}x_{12}
+
c_{13}x_{13}
+
c_{24}x_{24}
+
c_{34}x_{34}\\
&=
1\times3
+
4\times2
+
1\times3
+
2\times2\\
&=
18.
\end{aligned}
$$

因此：

$$
\boxed{C^*=18}
$$

---

# 16. 结果验证

为了避免“程序能够运行，但结果实际错误”的情况，本项目目前设置了三个 Validator。

---

## 16.1 容量约束验证

检查：

$$
0\le x_{uv}\le u_{uv}.
$$

对应函数：

```python
check_capacity(...)
```

正确时输出：

```text
容量约束： PASS
```

---

## 16.2 流守恒验证

定义节点净流量：

$$
\operatorname{net}(v)
=
\operatorname{inflow}(v)
-
\operatorname{outflow}(v).
$$

要求：

源点：

$$
\operatorname{net}(s)=-F.
$$

汇点：

$$
\operatorname{net}(t)=F.
$$

中间节点：

$$
\operatorname{net}(v)=0.
$$

对应函数：

```python
check_flow_conservation(...)
```

正确时输出：

```text
流守恒： PASS
```

---

## 16.3 目标函数验证

重新计算：

$$
\text{computed\_cost}
=
\sum_{(u,v)\in A}
c_{uv}x_{uv}.
$$

并与算法返回的 `total_cost` 比较。

对应函数：

```python
check_objective(...)
```

正确时输出：

```text
目标函数： PASS
```

---

# 17. 当前运行结果

正常情况下，程序输出类似：

```text
最终结果
--------------------------------------------------
弧 (1, 2): flow = 3, capacity = 5, cost = 1
弧 (1, 3): flow = 2, capacity = 4, cost = 4
弧 (2, 4): flow = 3, capacity = 3, cost = 1
弧 (3, 4): flow = 2, capacity = 5, cost = 2
--------------------------------------------------
最小费用：18

结果验证
--------------------------------------------------
容量约束： PASS
流守恒： PASS
目标函数： PASS
```

---

# 18. 如何运行项目

首先进入项目目录：

```bash
cd min-cost-flow-project
```

然后运行：

```bash
python3 main.py
```

如果当前环境中的 Python 命令为 `python`，也可以使用：

```bash
python main.py
```

---

# 19. 当前已经实现的内容

## Python 与图数据结构

- [x] Python 列表
- [x] Python 字典
- [x] 元组表示有向弧
- [x] 邻接表
- [x] 函数
- [x] 模块化文件结构

## 图算法

- [x] BFS
- [x] `visited`
- [x] `parent`
- [x] 路径恢复
- [x] Dijkstra
- [x] Relaxation
- [x] Priority Queue
- [x] `heapq`
- [x] Bellman-Ford 基础

## 网络流算法

- [x] 容量
- [x] 流量
- [x] 残量容量
- [x] 残量网络
- [x] 正向残量弧
- [x] 反向残量弧
- [x] 增广路径
- [x] 瓶颈容量
- [x] 流量增广

## 最小费用流

- [x] Successive Shortest Path
- [x] Potential
- [x] Reduced Cost
- [x] Heap-Dijkstra
- [x] 路径费用计算
- [x] 总费用更新

## 结果验证

- [x] Capacity Validator
- [x] Flow Conservation Validator
- [x] Objective Validator

---

# 20. 后续开发计划

## 阶段一：Gurobi 交叉验证

下一步计划使用 Gurobi 建立同一个最小费用流模型。

比较：

$$
\boxed{
\text{自实现 SSP}
\quad
\text{VS}
\quad
\text{Gurobi}
}
$$

主要比较：

- 最优目标值；
- 最优流量；
- 可行性；
- 求解时间。

---

## 阶段二：随机网络生成

自动生成不同规模的网络：

$$
|V|
=
20,\ 50,\ 100,\ 200,\ldots
$$

随机生成：

- 节点；
- 弧；
- 容量；
- 单位费用；
- 流量需求。

---

## 阶段三：算法性能实验

记录不同网络规模下：

- 运行时间；
- 最优目标值；
- 增广次数；
- 网络规模；
- 算法扩展能力。

目标是研究：

$$
|V|,\ |A|
$$

增加后算法运行时间的变化。

---

## 阶段四：代码结构优化

后续考虑进一步加入：

```text
validators.py
experiments.py
random_instance.py
tests/
```

并进一步实现：

- `Edge` 数据结构；
- Reverse Edge Index；
- 自动单元测试；
- 异常输入检查；
- 更完整的错误处理。

---

## 阶段五：其他组合优化算法

完成最小费用流项目后，可以继续扩展：

- 最短路；
- 最大流；
- 最小费用最大流；
- 二分图匹配；
- 指派问题；
- 调度问题；
- 车辆路径问题；
- 整数规划；
- Gurobi；
- SCIP；
- OR-Tools。

---

# 21. 项目学习目标

本项目的目标不是单纯调用现成求解器，而是形成完整的算法学习链：

$$
\boxed{
\text{数学模型}
\rightarrow
\text{算法思想}
\rightarrow
\text{数据结构}
\rightarrow
\text{代码实现}
\rightarrow
\text{结果验证}
\rightarrow
\text{求解器对比}
\rightarrow
\text{性能实验}
}
$$

通过该项目逐步训练：

- Python 编程能力；
- 数据结构与算法能力；
- 图算法能力；
- 组合优化能力；
- 数学建模能力；
- 算法调试能力；
- Optimization Engineering 能力。
