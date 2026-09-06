from __future__ import annotations

import dns.asyncresolver
import dns.exception
import dns.resolver

DKIM_SELECTORS = [
    "default",
    "google",
    "selector1",
    "selector2",
    "k1",
    "s1",
    "s2",
    "selector",
]


def _txt_parts(record) -> str:
    return "".join(
        part.decode("utf-8", errors="replace")
        if isinstance(part, bytes)
        else str(part)
        for part in record.strings
    )


async def _resolve_txt(resolver, name: str, timeout_s: float) -> list[str]:
    try:
        answers = await resolver.resolve(name, "TXT", lifetime=timeout_s)
    except (
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.resolver.NoNameservers,
        dns.exception.Timeout,
    ):
        return []
    return [_txt_parts(r) for r in answers]


async def _resolve_mx(resolver, domain: str, timeout_s: float) -> list[dict]:
    try:
        answers = await resolver.resolve(domain, "MX", lifetime=timeout_s)
    except (
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.resolver.NoNameservers,
        dns.exception.Timeout,
    ):
        return []
    return [
        {"priority": r.preference, "host": r.exchange.to_text().rstrip(".")}
        for r in answers
    ]


async def analyze_email_dns(domain: str, timeout_s: float) -> dict:
    resolver = dns.asyncresolver.Resolver()

    mx = await _resolve_mx(resolver, domain, timeout_s)

    domain_txt = await _resolve_txt(resolver, domain, timeout_s)
    spf_records = [t for t in domain_txt if t.lower().startswith("v=spf1")]
    spf = {
        "present": bool(spf_records),
        "pass": bool(spf_records),
        "record": spf_records[0] if spf_records else None,
    }

    dkim_records = []
    for selector in DKIM_SELECTORS:
        records = await _resolve_txt(
            resolver, f"{selector}._domainkey.{domain}", timeout_s
        )
        for record in records:
            dkim_records.append({"selector": selector, "record": record})
        if dkim_records:
            break
    dkim = {"present": bool(dkim_records), "pass": bool(dkim_records), "records": dkim_records}

    dmarc_txt = await _resolve_txt(resolver, f"_dmarc.{domain}", timeout_s)
    dmarc_records = [t for t in dmarc_txt if t.lower().startswith("v=dmarc1")]
    dmarc = {
        "present": bool(dmarc_records),
        "pass": bool(dmarc_records),
        "record": dmarc_records[0] if dmarc_records else None,
    }

    if not mx:
        summary = "fail"
    elif spf["present"] and dkim["present"] and dmarc["present"]:
        summary = "pass"
    else:
        summary = "warn"

    return {
        "domain": domain,
        "mx": mx,
        "spf": spf,
        "dkim": dkim,
        "dmarc": dmarc,
        "summary": summary,
    }
