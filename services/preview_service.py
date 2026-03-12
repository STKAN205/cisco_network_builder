from services.exporter import export_configs


def render_topology_diagram(edges, routing_label=None, router_interfaces=None):
    lines = ["Sơ đồ kết nối:"]
    if routing_label:
        lines.append(routing_label)
    lines.append("")
    if router_interfaces:
        for router_name, ports in router_interfaces.items():
            port_parts = [f"{port}<{ip}>" for port, ip in ports]
            lines.append(f"{router_name}: " + " ".join(port_parts))
        lines.append("")
    for left, left_port, right, right_port, subnet in edges:
        lines.append(f"{left} {left_port} <-> {right} {right_port} ({subnet})")
    return "\n".join(lines)


__all__ = ["export_configs", "render_topology_diagram"]
