from dataclasses import dataclass, field
from typing import List


@dataclass
class RouterConnect:
    conn_id: str
    ethernet_ports: List[str] = field(default_factory=list)
    serial_ports: List[str] = field(default_factory=list)


@dataclass
class Ethernet:
    name: str
    router_id: str
    subnetmask: str


@dataclass
class Serial:
    name: str
    router_id: str
    subnetmask: str


def build_router_connect(conn_id: str, ethernet_ports: List[str], serial_ports: List[str]) -> RouterConnect:
    ethernet_ports = [port.strip() for port in ethernet_ports if port and port.strip()]
    serial_ports = [port.strip() for port in serial_ports if port and port.strip()]

    if not ethernet_ports:
        raise ValueError(f"Router {conn_id} cần ít nhất 1 cổng Ethernet.")
    if len(serial_ports) < 2:
        raise ValueError(f"Router {conn_id} cần ít nhất 2 cổng Serial.")

    return RouterConnect(conn_id=conn_id, ethernet_ports=ethernet_ports, serial_ports=serial_ports)
