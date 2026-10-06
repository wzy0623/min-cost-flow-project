import random


def generate_random_instance(
    num_nodes,
    num_arcs,
    required_flow,
    max_capacity=20,
    max_cost=10,
    seed=None,
):
    """
    随机生成一个最小费用流实例。

    参数
    ----------
    num_nodes : int
        节点数量

    num_arcs : int
        弧数量

    required_flow : int
        需要从 source 发送到 sink 的流量

    max_capacity : int
        随机弧最大容量

    max_cost : int
        随机弧最大单位费用

    seed : int or None
        随机种子，用于复现实验

    返回
    ----------
    nodes
    arcs
    capacity
    cost
    source
    sink
    required_flow
    """

    if seed is not None:
        random.seed(seed)

    # --------------------------------
    # 1. 创建节点
    # --------------------------------

    nodes = list(range(1, num_nodes + 1))

    source = 1
    sink = num_nodes

    arcs = []
    arc_set = set()

    capacity = {}
    cost = {}

    # --------------------------------
    # 2. 创建一条保证可行的主路径
    # --------------------------------
    #
    # 1 -> 2 -> 3 -> ... -> n
    #
    # 每条弧容量至少为 required_flow，
    # 因此一定可以把 required_flow 单位流
    # 从 source 发送到 sink。
    # --------------------------------

    for u in range(1, num_nodes):

        v = u + 1

        arc = (u, v)

        arcs.append(arc)
        arc_set.add(arc)

        capacity[arc] = random.randint(
            required_flow,
            max(required_flow, max_capacity),
        )

        cost[arc] = random.randint(
            1,
            max_cost,
        )

    # --------------------------------
    # 3. 随机添加额外弧
    # --------------------------------

    max_possible_arcs = (
        num_nodes * (num_nodes - 1) // 2
    )

    if num_arcs > max_possible_arcs:
        raise ValueError(
            "当前生成器不允许原网络同时出现反向成对弧，"
            "因此 num_arcs 设置过大。"
        )

    if num_arcs < num_nodes - 1:
        raise ValueError(
            "num_arcs 至少需要 num_nodes - 1，"
            "否则无法保留保证可行的主路径。"
        )

    while len(arcs) < num_arcs:

        u = random.choice(nodes)
        v = random.choice(nodes)

        if u == v:
            continue

        arc = (u, v)
        reverse_arc = (v, u)

        # 已存在则跳过
        if arc in arc_set:
            continue

        # 暂时不允许原网络存在成对反向弧
        if reverse_arc in arc_set:
            continue

        arcs.append(arc)
        arc_set.add(arc)

        capacity[arc] = random.randint(
            1,
            max_capacity,
        )

        cost[arc] = random.randint(
            1,
            max_cost,
        )

    return (
        nodes,
        arcs,
        capacity,
        cost,
        source,
        sink,
        required_flow,
    )


if __name__ == "__main__":

    instance = generate_random_instance(
        num_nodes=6,
        num_arcs=10,
        required_flow=5,
        seed=42,
    )

    (
        nodes,
        arcs,
        capacity,
        cost,
        source,
        sink,
        required_flow,
    ) = instance

    print("nodes =", nodes)
    print("arcs =", arcs)
    print("capacity =", capacity)
    print("cost =", cost)
    print("source =", source)
    print("sink =", sink)
    print("required_flow =", required_flow)