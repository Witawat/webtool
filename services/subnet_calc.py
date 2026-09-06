from __future__ import annotations


def _first_last_host(net) -> tuple[str, str]:
    if net.prefixlen == net.max_prefixlen:
        return str(net.network_address), str(net.network_address)
    if net.version == 4 and net.prefixlen == 31:
        return str(net.network_address), str(net.broadcast_address)
    return str(net.network_address + 1), str(net.broadcast_address - 1)


def _usable_hosts(net) -> int:
    if net.version == 4 and net.prefixlen <= 30:
        return net.num_addresses - 2
    return net.num_addresses


def calculate_subnet(net) -> dict:
    first_host, last_host = _first_last_host(net)
    return {
        "cidr": str(net),
        "network": str(net.network_address),
        "broadcast": str(net.broadcast_address),
        "netmask": str(net.netmask),
        "wildcard": str(net.hostmask),
        "first_host": first_host,
        "last_host": last_host,
        "usable_hosts": _usable_hosts(net),
        "total_hosts": net.num_addresses,
        "prefix": net.prefixlen,
        "ip_version": net.version,
    }
