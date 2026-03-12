import ipaddress


def _wildcard(mask):
    return ipaddress.IPv4Address((1 << 32) - 1 - int(mask))


def sinh_config(
    router_id,
    lan_sub,
    wan_links,
    dhcp,
    ethernet_ports=None,
    routing_type="DYNAMIC",
    routing_protocol="RIP",
    static_routes=None,
):
    config = []
    networks = [lan_sub]
    lan_hosts = list(lan_sub.hosts())

    if not lan_hosts:
        raise ValueError(f"LAN subnet không có host hợp lệ cho R{router_id}.")

    config.append("enable")
    config.append("configure terminal")
    config.append(f"hostname R{router_id}")

    if not ethernet_ports:
        ethernet_ports = ["fa1/0"]

    if len(lan_hosts) < len(ethernet_ports):
        raise ValueError(
            f"LAN subnet không đủ IP cho các cổng Ethernet trên R{router_id}."
        )

    for index, port in enumerate(ethernet_ports):
        config.append(f"interface {port}")
        config.append(f"ip address {lan_hosts[index]} {lan_sub.netmask}")
        config.append("no shutdown")
        config.append("exit")

    if dhcp:
        lan_ip = lan_hosts[0]
        config.append(f"ip dhcp excluded-address {lan_ip}")
        config.append(f"ip dhcp pool LAN_R{router_id}")
        config.append(f"network {lan_sub.network_address} {lan_sub.netmask}")
        config.append(f"default-router {lan_ip}")
        config.append("dns-server 8.8.8.8")
        config.append("exit")

    for wan, side, port in wan_links:
        hosts = list(wan.hosts())
        if len(hosts) < 2:
            raise ValueError(f"WAN subnet {wan} không đủ 2 host để gán IP.")

        ip = hosts[0] if side == 0 else hosts[1]
        networks.append(wan)

        config.append(f"interface {port}")
        config.append(f"ip address {ip} {wan.netmask}")
        config.append("no shutdown")
        config.append("exit")

    if routing_type == "STATIC":
        if not static_routes:
            raise ValueError(f"Thiếu cấu hình định tuyến tĩnh tự động cho R{router_id}.")
        for network, mask, next_hop in static_routes:
            config.append(f"ip route {network} {mask} {next_hop}")
    else:
        if routing_protocol == "RIP":
            config.append("router rip")
            config.append("version 2")
            config.append("no auto-summary")
            for network in networks:
                config.append(f"network {network.network_address}")
        else:
            config.append("router ospf 1")
            for network in networks:
                wildcard = _wildcard(network.netmask)
                config.append(f"network {network.network_address} {wildcard} area 0")

    config.append("exit")

    return "\n".join(config)
