from __future__ import annotations

import asyncio

from core.errors import AppError
from services.port import resolve_ip


def _clean_rtts(values) -> list[float]:
    out = []
    for value in values or []:
        if value is None or value == float("inf"):
            continue
        out.append(round(value, 1))
    return out


async def traceroute_host(host: str, max_hops: int, timeout_s: float) -> dict:
    ip = await resolve_ip(host)
    try:
        from icmplib import traceroute

        hops = await asyncio.wait_for(
            asyncio.to_thread(
                traceroute,
                host,
                max_hops=max_hops,
                timeout=timeout_s,
                interval=0.05,
            ),
            timeout=max_hops * timeout_s + 30.0,
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    except Exception as exc:
        raise AppError("INTERNAL", "INTERNAL", status=500) from exc

    result = []
    for hop in hops:
        rtts = _clean_rtts(hop.rtts)
        result.append(
            {
                "ttl": hop.distance,
                "ip": getattr(hop, "address", None),
                "hostname": getattr(hop, "alias", None),
                "rtt_ms": rtts,
                "timed_out": not rtts or not getattr(hop, "is_alive", True),
            }
        )
    return {"host": host, "ip": ip, "hops": result}
