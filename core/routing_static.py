import ipaddress
from collections import deque


def _wan_ip(subnet, side):
    hosts = list(subnet.hosts())
    if len(hosts) < 2:
        raise ValueError(f"WAN subnet {subnet} không đủ 2 host để gán IP.")
    return hosts[0] if side == 0 else hosts[1]


def build_interface_ip_map(lan_subnets, wan_links_by_router, ethernet_ports_by_router):
    router_map = {}

    for idx, lan_sub in enumerate(lan_subnets):
        router_name = f"R{idx + 1}"
        ports = []

        lan_hosts = list(lan_sub.hosts())
        for port_index, port in enumerate(ethernet_ports_by_router[idx]):
            if port_index >= len(lan_hosts):
                break
            ports.append((port, str(lan_hosts[port_index])))

        for wan_sub, side, port in wan_links_by_router[idx]:
            ports.append((port, str(_wan_ip(wan_sub, side))))

        router_map[router_name] = ports

    return router_map


def _build_adjacency(wan_links_by_router):
    subnet_endpoints = {}
    for router_idx, links in enumerate(wan_links_by_router):
        for wan_sub, side, port in links:
            subnet_endpoints.setdefault(wan_sub, []).append((router_idx, side, port))

    adjacency = {idx: [] for idx in range(len(wan_links_by_router))}
    for wan_sub, endpoints in subnet_endpoints.items():
        if len(endpoints) != 2:
            continue
        (r1, _, _), (r2, _, _) = endpoints
        adjacency[r1].append((r2, wan_sub))
        adjacency[r2].append((r1, wan_sub))

    return adjacency, subnet_endpoints


def _first_hop(src, dst, adjacency):
    queue = deque([src])
    parent = {src: None}

    while queue:
        current = queue.popleft()
        if current == dst:
            break
        for neighbor, _ in adjacency[current]:
            if neighbor not in parent:
                parent[neighbor] = current
                queue.append(neighbor)

    if dst not in parent:
        return None

    node = dst
    while parent[node] is not None and parent[node] != src:
        node = parent[node]
    return node


def compute_static_routes(lan_subnets, wan_links_by_router):
    router_count = len(lan_subnets)
    if router_count <= 1:
        return {0: []}

    adjacency, subnet_endpoints = _build_adjacency(wan_links_by_router)

    ip_map = {}
    for wan_sub, endpoints in subnet_endpoints.items():
        for router_idx, side, _ in endpoints:
            ip_map[(router_idx, wan_sub)] = str(_wan_ip(wan_sub, side))

    static_routes = {idx: [] for idx in range(router_count)}

    for src in range(router_count):
        for dst in range(router_count):
            if src == dst:
                continue
            first_hop = _first_hop(src, dst, adjacency)
            if first_hop is None:
                continue
            shared_subnet = None
            for neighbor, wan_sub in adjacency[src]:
                if neighbor == first_hop:
                    shared_subnet = wan_sub
                    break
            if shared_subnet is None:
                continue
            next_hop_ip = ip_map.get((first_hop, shared_subnet))
            if not next_hop_ip:
                continue
            lan_sub = lan_subnets[dst]
            static_routes[src].append(
                (str(lan_sub.network_address), str(lan_sub.netmask), next_hop_ip)
            )

    return static_routes
