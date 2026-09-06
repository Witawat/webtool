from __future__ import annotations

import asyncio
import ipaddress

from core.config import settings
from core.errors import AppError
from core.validation import (
    is_forbidden_ip,
    parse_cidr,
    parse_domain,
    parse_email,
    parse_host,
    parse_ip,
)

from .dns_lookup import lookup_dns
from .email_dns import analyze_email_dns
from .phone_geo import lookup_phone
from .ping import ping_host
from .providers.email import reverse_email_lookup
from .providers.geoip import lookup as geoip_lookup
from .providers.reverse_ip import reverse_ip_lookup
from .ssl_checker import check_ssl
from .subnet_calc import calculate_subnet
from .whois import lookup_whois

MAX_BULK = 10
PER_ITEM_TIMEOUT_S = 20.0


async def _run_dns(raw: str) -> dict:
    domain = parse_domain(raw)
    return await lookup_dns(domain, settings.dns_timeout_s)


async def _run_whois(raw: str) -> dict:
    domain = parse_domain(raw)
    return await lookup_whois(domain, settings.whois_timeout_s)


def _run_subnet(raw: str) -> dict:
    return calculate_subnet(parse_cidr(raw))


def _run_phone(raw: str) -> dict:
    return lookup_phone(raw, None)


async def _run_ping(raw: str) -> dict:
    return await ping_host(
        parse_host(raw), settings.ping_count, settings.ping_timeout_s
    )


async def _run_ssl(raw: str) -> dict:
    return await check_ssl(
        parse_host(raw), 443, settings.ssl_connect_timeout_s
    )


async def _run_email_dns(raw: str) -> dict:
    domain = parse_domain(raw)
    return await analyze_email_dns(domain, settings.dns_timeout_s)


async def _run_reverse_ip(raw: str) -> dict:
    ip = str(parse_ip(raw))
    if is_forbidden_ip(ipaddress.ip_address(ip)):
        raise AppError("SSRF_BLOCKED", "SSRF_BLOCKED", field="ip")
    return await reverse_ip_lookup(
        ip, settings.http_timeout_s, settings.hackertarget_key
    )


async def _run_geoip(raw: str) -> dict:
    try:
        ip_obj = ipaddress.ip_address(raw)
        if is_forbidden_ip(ip_obj):
            raise AppError("SSRF_BLOCKED", "SSRF_BLOCKED", field="query")
    except ValueError:
        from core.validation import resolve_host_ips

        domain = parse_domain(raw)
        resolved = await resolve_host_ips(domain)
        for ip_str in resolved:
            if is_forbidden_ip(ipaddress.ip_address(ip_str)):
                raise AppError("SSRF_BLOCKED", "SSRF_BLOCKED", field="query") from None

    data = await geoip_lookup(raw, settings.geoip_timeout_s)
    if data is None:
        raise AppError("NOT_FOUND", "NOT_FOUND", field="query")
    return data


async def _run_email_lookup(raw: str) -> dict:
    email = parse_email(raw)
    return await reverse_email_lookup(email, 10.0)


BULK_HANDLERS = {
    "dns": _run_dns,
    "whois": _run_whois,
    "subnet-calc": _run_subnet,
    "phone": _run_phone,
    "ping": _run_ping,
    "ssl": _run_ssl,
    "email-dns": _run_email_dns,
    "reverse-ip": _run_reverse_ip,
    "network-location": _run_geoip,
    "email-lookup": _run_email_lookup,
}


async def _call(handler, raw: str, timeout_s: float):
    result = handler(raw)
    if asyncio.iscoroutine(result):
        return await asyncio.wait_for(result, timeout=timeout_s)
    return result


async def run_bulk(slug: str, values: list, lang: str = "en") -> dict:
    handler = BULK_HANDLERS.get(slug)
    if handler is None:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="slug")
    if not 1 <= len(values) <= MAX_BULK:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="values")

    results = []
    for raw in values:
        raw = str(raw).strip()
        try:
            data = await _call(handler, raw, PER_ITEM_TIMEOUT_S)
            results.append({"input": raw, "ok": True, "data": data})
        except AppError as exc:
            results.append(
                {"input": raw, "ok": False, "error": exc.to_dict(lang)}
            )
        except TimeoutError:
            results.append(
                {
                    "input": raw,
                    "ok": False,
                    "error": {"code": "TIMEOUT", "message": "timeout"},
                }
            )
    return {"slug": slug, "count": len(results), "results": results}
