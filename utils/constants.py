import unicodedata


def normalize_unicode(text: str) -> str:
    if not isinstance(text, str):
        return text
    return unicodedata.normalize("NFC", text)


TOPOLOGIES = [
    "Chuỗi",
    "Vòng",
    "Sao",
    "Lưới",
]

PROTOCOLS = [
    "RIP",
    "OSPF",
]

TOPOLOGY_SYNONYMS = {
    # ASCII
    "Chuoi": "Chuỗi",
    "Vong": "Vòng",
    "Luoi": "Lưới",
    # Mojibake (legacy)
    "Chuá»—i": "Chuỗi",
    "VÃ²ng": "Vòng",
    "LÆ°á»›i": "Lưới",
    "ChuÃ¡Â»â€”i": "Chuỗi",
    "VÃƒÂ²ng": "Vòng",
    "LÃ†Â°Ã¡Â»â€ºi": "Lưới",
}


def normalize_topology_name(name: str) -> str:
    if not isinstance(name, str):
        return name
    name = normalize_unicode(name).strip()
    return TOPOLOGY_SYNONYMS.get(name, name)


TOPOLOGY_WAN_COUNT = {
    "Chuỗi": lambda so_router: so_router - 1,
    "Vòng": lambda so_router: so_router,
    "Sao": lambda so_router: so_router - 1,
    "Lưới": lambda so_router: (so_router * (so_router - 1)) // 2,
}

SERIAL_PORTS = [
    "se2/0",
    "se3/0",
    "se2/1",
    "se3/1",
]
