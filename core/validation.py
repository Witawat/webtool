from __future__ import annotations

import asyncio
import ipaddress
import re
import socket

from .errors import AppError

PORT_NAMES = {
    21: "FTP",
    22: "SSH",
    23: "TELNET",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    115: "SFTP",
    135: "RPC",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    1433: "MSSQL",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP-Alt",
    25565: "Minecraft",
}

_DOMAIN_RE = re.compile(r"^([a-z0-9-]+\.)+[a-z]{2,63}$")


def parse_ip(s: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    s = s.strip()
    try:
        return ipaddress.ip_address(s)
    except ValueError as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="ip") from exc


def parse_domain(s: str) -> str:
    s = s.strip().rstrip(".").lower()
    if not s:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="domain")
    try:
        ascii_domain = s.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="domain") from exc
    if not _DOMAIN_RE.match(ascii_domain):
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="domain")
    return ascii_domain


def parse_host(s: str) -> str:
    s = s.strip()
    if not s:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="host")
    try:
        ipaddress.ip_address(s)
        return s
    except ValueError:
        pass
    return parse_domain(s)


def parse_port(s) -> int:
    try:
        port = int(s)
    except (TypeError, ValueError) as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="port") from exc
    if not 1 <= port <= 65535:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="port")
    return port


def parse_cidr(s: str) -> ipaddress.IPv4Network | ipaddress.IPv6Network:
    s = s.strip()
    try:
        return ipaddress.ip_network(s, strict=False)
    except ValueError as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="cidr") from exc


def _is_forbidden_ip(ip_obj) -> bool:
    return (
        ip_obj.is_private
        or ip_obj.is_link_local
        or ip_obj.is_loopback
        or ip_obj.is_reserved
        or ip_obj.is_multicast
        or ip_obj.is_unspecified
    )


def _split_host_port(s: str) -> tuple[str, str | None]:
    if s.startswith("["):
        end = s.find("]")
        if end == -1:
            return s, None
        host = s[: end + 1]
        rest = s[end + 1 :]
        if rest.startswith(":"):
            return host, rest[1:]
        return host, None
    host, sep, port = s.partition(":")
    return host, (port if sep else None)


def _normalize_hostname(host: str) -> str:
    try:
        return host.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="url") from exc


async def _resolve_host_ips(host: str) -> list[str]:
    try:
        infos = await asyncio.wait_for(
            asyncio.get_running_loop().getaddrinfo(
                host, None, proto=socket.IPPROTO_TCP
            ),
            timeout=5.0,
        )
    except (TimeoutError, socket.gaierror, OSError) as exc:
        raise AppError("NOT_FOUND", "NOT_FOUND", field="url") from exc
    return [info[4][0] for info in infos]


async def validate_url_safe(url: str) -> str:
    url = url.strip()
    parts = url.split("://", 1)
    if len(parts) != 2 or parts[0].lower() not in ("http", "https"):
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="url")
    scheme = parts[0].lower()
    rest = parts[1].split("#", 1)[0]
    host_port, _, path = rest.partition("/")
    userinfo, _, host_port = host_port.rpartition("@")
    del userinfo
    host, port = _split_host_port(host_port)
    if not host:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="url")
    if port:
        parse_port(port)

    if host.startswith("[") and host.endswith("]"):
        try:
            ip_obj = ipaddress.ip_address(host[1:-1])
        except ValueError as exc:
            raise AppError("INVALID_INPUT", "INVALID_INPUT", field="url") from exc
    else:
        try:
            ip_obj = ipaddress.ip_address(host)
        except ValueError:
            ip_obj = None

    if ip_obj is not None:
        if _is_forbidden_ip(ip_obj):
            raise AppError("SSRF_BLOCKED", "SSRF_BLOCKED", field="url")
    else:
        host = _normalize_hostname(host)
        resolved = await _resolve_host_ips(host)
        if not resolved:
            raise AppError("NOT_FOUND", "NOT_FOUND", field="url")
        for ip_str in resolved:
            if _is_forbidden_ip(ipaddress.ip_address(ip_str)):
                raise AppError("SSRF_BLOCKED", "SSRF_BLOCKED", field="url")

    return f"{scheme}://{host_port}/{path}"
