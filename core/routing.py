import ipaddress
from dataclasses import dataclass


@dataclass
class RoutingConfig:
    routing_type: str
    protocol: str | None = None
    network: str | None = None
    mask: str | None = None
    next_hop: str | None = None
    auto_static: bool = False

    def validate(self):
        if self.routing_type == "STATIC":
            if self.auto_static:
                return
            if not self.network or not self.mask or not self.next_hop:
                raise ValueError("Thiếu Network/Mask/Next Hop cho định tuyến tĩnh.")
            try:
                ipaddress.ip_network(f"{self.network}/{self.mask}", strict=False)
                ipaddress.ip_address(self.next_hop)
            except ValueError as exc:
                raise ValueError("Network/Mask/Next Hop không hợp lệ.") from exc
        else:
            if not self.protocol:
                raise ValueError("Thiếu giao thức định tuyến động.")
