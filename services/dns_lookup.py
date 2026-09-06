from __future__ import annotations

import asyncio
import ipaddress

import dns.asyncresolver
import dns.exception
import dns.rdatatype
import dns.resolver

from core.errors import AppError

VALID_TYPES = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA", "SRV", "CAA"]
DEFAULT_TYPES = list(VALID_TYPES)


def _format_value(rdtype: str, record) -> str:
    if rdtype == "MX":
        return f"{record.preference} {record.exchange.to_text().rstrip('.')}"
    if rdtype == "TXT":
        return "".join(
            s.decode("utf-8", errors="replace") if isinstance(s, bytes) else str(s)
            for s in record.strings
        )
    if rdtype == "SRV":
        return (
            f"{record.priority} {record.weight} {record.port} "
            f"{record.target.to_text().rstrip('.')}"
        )
    if rdtype == "CAA":
        return f"{record.flags} {record.tag} {record.value}"
    return record.to_text().rstrip(".")


async def _resolve_type(
    resolver, name: str, rdtype_str: str, timeout_s: float
) -> list[dict]:
    rdtype = dns.rdatatype.from_text(rdtype_str)
    try:
        answers = await resolver.resolve(name, rdtype, lifetime=timeout_s)
    except dns.resolver.NXDOMAIN as exc:
        raise AppError("NOT_FOUND", "NOT_FOUND", field="domain") from exc
    except (dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return []
    except dns.exception.Timeout as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc

    ttl = int(answers.rrset.ttl) if answers.rrset is not None else 0
    return [
        {
            "type": rdtype_str,
            "name": name,
            "ttl": ttl,
            "value": _format_value(rdtype_str, record),
        }
        for record in answers
    ]


async def _reverse_lookup(ip: str, timeout_s: float) -> str | None:
    try:
        name = await dns.asyncresolver.resolve_address(ip, lifetime=timeout_s)
        return str(name).rstrip(".")
    except (dns.exception.DNSException, OSError):
        return None


async def lookup_dns(host: str, types: list[str], timeout_s: float) -> dict:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        reverse = await _reverse_lookup(host, timeout_s)
        records = (
            [{"type": "PTR", "name": host, "ttl": 0, "value": reverse}]
            if reverse
            else []
        )
        return {"domain": host, "records": records, "reverse": reverse}

    resolver = dns.asyncresolver.Resolver()
    results = await asyncio.gather(
        *(_resolve_type(resolver, host, t, timeout_s) for t in types),
        return_exceptions=True,
    )
    records: list[dict] = []
    for result in results:
        if isinstance(result, BaseException):
            raise result
        records.extend(result)
    return {"domain": host, "records": records, "reverse": None}
