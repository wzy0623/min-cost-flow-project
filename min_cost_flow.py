import heapq


def build_residual_network(arcs, capacity, cost, flow):

    residual_arcs = []
    residual_capacity = {}
    residual_cost = {}

    for u, v in arcs:

        # 正向残量弧
        forward_capacity = capacity[(u, v)] - flow[(u, v)]

        if forward_capacity > 0:
            residual_arcs.append((u, v))
            residual_capacity[(u, v)] = forward_capacity
            residual_cost[(u, v)] = cost[(u, v)]

        # 反向残量弧
        if flow[(u, v)] > 0:
            residual_arcs.append((v, u))
            residual_capacity[(v, u)] = flow[(u, v)]
            residual_cost[(v, u)] = -cost[(u, v)]

    return residual_arcs, residual_capacity, residual_cost



def dijkstra_with_potential(
    nodes,
    residual_arcs,
    residual_cost,
    start,
    potential
):

    INF = float("inf")

    dist = {node: INF for node in nodes}
    parent = {}

    dist[start] = 0

    adj = {node: [] for node in nodes}

    for u, v in residual_arcs:
        adj[u].append(v)

    heap = [(0, start)]

    while heap:

        current_dist, u = heapq.heappop(heap)

        if current_dist > dist[u]:
            continue

        for v in adj[u]:

            reduced_cost = (
                residual_cost[(u, v)]
                + potential[u]
                - potential[v]
            )

            new_dist = dist[u] + reduced_cost

            if new_dist < dist[v]:

                dist[v] = new_dist
                parent[v] = u

                heapq.heappush(
                    heap,
                    (new_dist, v)
                )

    return dist, parent

def get_path(parent, start, target):

    if target == start:
        return [start]

    if target not in parent:
        return None

    path = []
    current = target

    while current != start:

        path.append(current)

        if current not in parent:
            return None

        current = parent[current]

    path.append(start)
    path.reverse()

    return path

def nodes_to_arcs(path_nodes):

    path_arcs = []

    for i in range(len(path_nodes) - 1):

        u = path_nodes[i]
        v = path_nodes[i + 1]

        path_arcs.append((u, v))

    return path_arcs

def min_cost_flow_with_potential(
    nodes,
    arcs,
    capacity,
    cost,
    source,
    sink,
    required_flow,
    verbose=False,
    return_stats=False,
):

    INF = float("inf")

    # 当前流
    flow = {
        arc: 0
        for arc in arcs
    }

    # 初始 potential
    potential = {
        node: 0
        for node in nodes
    }

    sent_flow = 0
    total_cost = 0
    augmentation_count = 0


    while sent_flow < required_flow:

        # --------------------------------
        # 1. 构造残量网络
        # --------------------------------

        residual_arcs, residual_capacity, residual_cost = \
            build_residual_network(
                arcs,
                capacity,
                cost,
                flow
            )


        # --------------------------------
        # 2. Reduced-cost Dijkstra
        # --------------------------------

        dist, parent = dijkstra_with_potential(
            nodes,
            residual_arcs,
            residual_cost,
            source,
            potential
        )


        # 如果汇点不可达
        if dist[sink] == INF:

            print("剩余网络中不存在 s-t 路径")
            print("无法发送要求的全部流量")

            return None


        # --------------------------------
        # 3. 恢复路径
        # --------------------------------

        path_nodes = get_path(
            parent,
            source,
            sink
        )

        path_arcs = nodes_to_arcs(
            path_nodes
        )


        # --------------------------------
        # 4. 更新 potential
        # --------------------------------

        for v in nodes:

            if dist[v] < INF:

                potential[v] += dist[v]


        # --------------------------------
        # 5. 计算瓶颈 delta
        # --------------------------------

        delta = required_flow - sent_flow

        for arc in path_arcs:

            delta = min(
                delta,
                residual_capacity[arc]
            )


        # --------------------------------
        # 6. 用原残量费用计算路径真实费用
        # --------------------------------

        path_cost = 0

        for arc in path_arcs:

            path_cost += residual_cost[arc]


        # --------------------------------
        # 7. 更新流量
        # --------------------------------

        for u, v in path_arcs:

            # 正向残量弧
            if (u, v) in flow:

                flow[(u, v)] += delta

            # 反向残量弧
            else:

                flow[(v, u)] -= delta


        # --------------------------------
        # 8. 更新总流量和总费用
        # --------------------------------

        sent_flow += delta

        total_cost += delta * path_cost

        augmentation_count += 1


        # --------------------------------
        # 输出本轮信息
        # --------------------------------

        print("最短增广路：", path_nodes)
        print("本轮增广量：", delta)
        print("路径单位费用：", path_cost)
        print("累计流量：", sent_flow)
        print("累计费用：", total_cost)
        print("当前 potential：", potential)
        print("-" * 40)

    if return_stats:

        stats = {
            "augmentation_count": augmentation_count,
        }

    return flow, total_cost, stats


def check_capacity(flow, capacity):

    for arc in flow:

        if flow[arc] < 0:
            return False

        if flow[arc] > capacity[arc]:
            return False

    return True

def check_flow_conservation(
    nodes,
    arcs,
    flow,
    source,
    sink,
    required_flow
):
    net_flow = {node: 0 for node in nodes}

    # 计算每个节点：流入 - 流出
    for u, v in arcs:
        net_flow[u] -= flow[(u, v)]
        net_flow[v] += flow[(u, v)]

    for node in nodes:

        # 源点
        if node == source:
            if net_flow[node] != -required_flow:
                return False

        # 汇点
        elif node == sink:
            if net_flow[node] != required_flow:
                return False

        # 中间节点
        else:
            if net_flow[node] != 0:
                return False

    return True

import math


def check_objective(
    arcs,
    flow,
    cost,
    total_cost
):
    computed_cost = sum(
        flow[arc] * cost[arc]
        for arc in arcs
    )

    return math.isclose(
        computed_cost,
        total_cost,
        rel_tol=1e-9,
        abs_tol=1e-9
    )