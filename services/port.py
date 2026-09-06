from __future__ import annotations

import asyncio
import socket
import time
from contextlib import suppress

from core.errors import AppError
from core.validation import PORT_NAMES


async def _resolve_ip(host: str) -> str:
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
    ip = await _resolve_ip(host)
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
