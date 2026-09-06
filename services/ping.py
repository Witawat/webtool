from __future__ import annotations

import asyncio
import time
from contextlib import suppress

from services.port import resolve_ip


async def _tcp_ping(host: str, timeout_s: float) -> tuple[bool, int]:
    for port in (80, 443):
        try:
            start = time.perf_counter()
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=timeout_s
            )
            writer.close()
            with suppress(OSError, ConnectionError):
                await writer.wait_closed()
            return True, int((time.perf_counter() - start) * 1000)
        except (TimeoutError, OSError):
            continue
    return False, 0


def _clean_rtt(value: float | None) -> float:
    if value is None or value == float("inf"):
        return 0.0
    return round(value, 1)


async def ping_host(host: str, count: int, timeout_s: float) -> dict:
    ip = await resolve_ip(host)

    icmp_result = None
    try:
        from icmplib import async_ping

        icmp_result = await asyncio.wait_for(
            async_ping(
                host,
                count=count,
                timeout=timeout_s,
                interval=0.2,
                privileged=False,
            ),
            timeout=count * timeout_s + 10.0,
        )
    except Exception:
        icmp_result = None

    if icmp_result is not None and icmp_result.is_alive:
        return {
            "host": host,
            "ip": ip,
            "sent": icmp_result.packets_sent,
            "received": icmp_result.packets_received,
            "loss_pct": icmp_result.packet_loss,
            "rtt_ms": {
                "min": _clean_rtt(icmp_result.min_rtt),
                "avg": _clean_rtt(icmp_result.avg_rtt),
                "max": _clean_rtt(icmp_result.max_rtt),
            },
            "alive": True,
            "icmp": True,
        }

    alive_tcp, rtt = await _tcp_ping(host, timeout_s)
    if alive_tcp:
        return {
            "host": host,
            "ip": ip,
            "sent": count,
            "received": count,
            "loss_pct": 0,
            "rtt_ms": {"min": rtt, "avg": rtt, "max": rtt},
            "alive": True,
            "icmp": False,
        }
    return {
        "host": host,
        "ip": ip,
        "sent": count,
        "received": 0,
        "loss_pct": 100,
        "rtt_ms": {"min": 0, "avg": 0, "max": 0},
        "alive": False,
        "icmp": True,
    }
