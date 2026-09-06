from __future__ import annotations

import asyncio
import socket
import time
from contextlib import suppress

from core.errors import AppError
from core.validation import PORT_NAMES


async def resolve_ip(host: str) -> str:
    try:
        infos = await asyncio.wait_for(
            asyncio.get_running_loop().getaddrinfo(
                host, None, proto=socket.IPPROTO_TCP
            ),
            timeout=5.0,
        )
    except (TimeoutError, socket.gaierror, OSError) as exc:
        raise AppError("NOT_FOUND", "NOT_FOUND", field="host") from exc
    return infos[0][4][0]


async def check_port(host: str, port: int, timeout_s: float) -> dict:
    ip = await resolve_ip(host)
    start = time.perf_counter()
    state = "closed"
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=timeout_s
        )
        writer.close()
        with suppress(OSError, ConnectionError):
            await writer.wait_closed()
        state = "open"
    except TimeoutError:
        state = "filtered"
    except OSError:
        state = "closed"
    latency_ms = int((time.perf_counter() - start) * 1000)
    return {
        "host": host,
        "ip": ip,
        "port": port,
        "service": PORT_NAMES.get(port),
        "state": state,
        "latency_ms": latency_ms,
    }


async def scan_ports(
    ip: str, start_port: int, end_port: int, timeout_s: float, max_parallel: int
) -> dict:
    semaphore = asyncio.Semaphore(max_parallel)

    async def _one(port: int) -> dict:
        async with semaphore:
            return await check_port(ip, port, timeout_s)

    results = await asyncio.gather(
        *(_one(port) for port in range(start_port, end_port + 1))
    )
    open_ports = [
        {"port": r["port"], "service": r["service"], "latency_ms": r["latency_ms"]}
        for r in results
        if r["state"] == "open"
    ]
    closed = sum(1 for r in results if r["state"] != "open")
    return {
        "ip": ip,
        "scanned": len(results),
        "open_ports": open_ports,
        "closed": closed,
    }
