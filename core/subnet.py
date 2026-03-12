import ipaddress

from utils.constants import TOPOLOGY_WAN_COUNT, normalize_topology_name


def tinh_subnet(mang_goc, so_router, topology):
    net = ipaddress.ip_network(mang_goc, strict=False)
    topology = normalize_topology_name(topology)

    if so_router < 1:
        raise ValueError("Số router phải lớn hơn hoặc bằng 1.")

    if topology not in TOPOLOGY_WAN_COUNT:
        raise ValueError(f"Topology không hợp lệ: {topology}")

    if so_router == 1:
        wan = 0
    else:
        wan = TOPOLOGY_WAN_COUNT[topology](so_router)

    lan = so_router
    tong = lan + wan

    extra_bits = 0
    while (1 << extra_bits) < tong:
        extra_bits += 1

    new_prefix = net.prefixlen + extra_bits
    if new_prefix > 30:
        raise ValueError(
            "Mạng gốc quá nhỏ cho số router/topology đã chọn. "
            "Hãy dùng mạng lớn hơn."
        )

    subs = list(net.subnets(new_prefix=new_prefix))
    lan_sub = subs[:lan]
    wan_sub = subs[lan:lan + wan]

    if len(wan_sub) != wan:
        raise ValueError("Không đủ subnet WAN để tạo topology.")

    return lan_sub, wan_sub
