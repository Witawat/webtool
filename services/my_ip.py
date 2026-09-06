from __future__ import annotations

import asyncio
import ipaddress
import socket


def _reverse_dns(ip: str) -> str | None:
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror, OSError):
        return None


async def _geo_lookup(ip: str):
    try:
        from .providers.geoip import lookup

        return await lookup(ip)
    except Exception:
        return None


async def get_my_ip(ip: str) -> dict:
    hostname = await asyncio.to_thread(_reverse_dns, ip)
    version = ipaddress.ip_address(ip).version
    geo = await _geo_lookup(ip)
    return {"ip": ip, "version": version, "hostname": hostname, "geo": geo}
