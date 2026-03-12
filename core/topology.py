from utils.constants import normalize_topology_name


def _next_port(available_ports, used_ports):
    for port in available_ports:
        if port not in used_ports:
            used_ports.add(port)
            return port

    raise ValueError("Số liên kết WAN vượt quá số cổng serial đang được hỗ trợ.")


def tao_topology(so_router, wan_subnets, topology, serial_ports_by_router):
    routers = [[] for _ in range(so_router)]
    edges = []
    used_ports = [set() for _ in range(so_router)]
    wan_index = 0

    topology = normalize_topology_name(topology)

    if so_router == 1:
        return [[]], []

    if topology == "Chuỗi":
        for i in range(so_router - 1):
            left_port = _next_port(serial_ports_by_router[i], used_ports[i])
            right_port = _next_port(serial_ports_by_router[i + 1], used_ports[i + 1])

            routers[i].append((wan_subnets[wan_index], 0, left_port))
            routers[i + 1].append((wan_subnets[wan_index], 1, right_port))
            wan_index += 1

            edges.append(
                (
                    f"R{i + 1}",
                    left_port,
                    f"R{i + 2}",
                    right_port,
                    wan_subnets[wan_index - 1],
                )
            )

    elif topology == "Vòng":
        for i in range(so_router):
            j = (i + 1) % so_router
            left_port = _next_port(serial_ports_by_router[i], used_ports[i])
            right_port = _next_port(serial_ports_by_router[j], used_ports[j])

            routers[i].append((wan_subnets[wan_index], 0, left_port))
            routers[j].append((wan_subnets[wan_index], 1, right_port))
            wan_index += 1

            edges.append(
                (
                    f"R{i + 1}",
                    left_port,
                    f"R{j + 1}",
                    right_port,
                    wan_subnets[wan_index - 1],
                )
            )

    elif topology == "Sao":
        center = 0

        for i in range(1, so_router):
            center_port = _next_port(serial_ports_by_router[center], used_ports[center])
            leaf_port = _next_port(serial_ports_by_router[i], used_ports[i])

            routers[center].append((wan_subnets[wan_index], 0, center_port))
            routers[i].append((wan_subnets[wan_index], 1, leaf_port))
            wan_index += 1

            edges.append(
                (
                    f"R{center + 1}",
                    center_port,
                    f"R{i + 1}",
                    leaf_port,
                    wan_subnets[wan_index - 1],
                )
            )

    elif topology == "Lưới":
        for i in range(so_router):
            for j in range(i + 1, so_router):
                left_port = _next_port(serial_ports_by_router[i], used_ports[i])
                right_port = _next_port(serial_ports_by_router[j], used_ports[j])

                routers[i].append((wan_subnets[wan_index], 0, left_port))
                routers[j].append((wan_subnets[wan_index], 1, right_port))
                wan_index += 1

                edges.append(
                    (
                        f"R{i + 1}",
                        left_port,
                        f"R{j + 1}",
                        right_port,
                        wan_subnets[wan_index - 1],
                    )
                )

    else:
        raise ValueError(f"Topology không hợp lệ: {topology}")

    return routers, edges
