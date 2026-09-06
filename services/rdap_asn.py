from __future__ import annotations

import httpx

from core.errors import AppError

RDAP_BASE = "https://rdap.org"
MAX_REDIRECTS = 10


def _vcard_name(entity: dict) -> str | None:
    vcard = entity.get("vcardArray")
    if not isinstance(vcard, (list, tuple)) or len(vcard) < 2:
        return None
    for item in vcard[1]:
        if isinstance(item, (list, tuple)) and len(item) >= 4 and item[0].lower() in (
            "fn",
            "org",
        ):
            return str(item[3])
    return None


def _find_org(entities: list | None) -> dict | None:
    for entity in entities or []:
        roles = entity.get("roles") or []
        if "registrant" in roles or "abuse" in roles:
            name = _vcard_name(entity)
            if name:
                return {"handle": entity.get("handle"), "name": name}
    for entity in entities or []:
        name = _vcard_name(entity)
        if name:
            return {"handle": entity.get("handle"), "name": name}
    return None


def _cidr_from(data: dict) -> str | None:
    cidrs = data.get("cidr0_cidrs")
    if not isinstance(cidrs, list) or not cidrs:
        return None
    first = cidrs[0]
    prefix = first.get("v4prefix") or first.get("v6prefix")
    length = first.get("length")
    if prefix and length is not None:
        return f"{prefix}/{length}"
    return None


async def _fetch_json(url: str, timeout_s: float) -> dict:
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=timeout_s,
            max_redirects=MAX_REDIRECTS,
        ) as client:
            resp = await client.get(url)
    except httpx.HTTPError as exc:
        raise AppError("UPSTREAM_ERROR", "UPSTREAM_ERROR", status=502) from exc
    if resp.status_code == 404:
        raise AppError("NOT_FOUND", "NOT_FOUND", field="query")
    if resp.status_code != 200:
        raise AppError("UPSTREAM_ERROR", "UPSTREAM_ERROR", status=502)
    return resp.json()


async def lookup_ip(ip: str, timeout_s: float) -> dict:
    data = await _fetch_json(f"{RDAP_BASE}/ip/{ip}", timeout_s)
    return {
        "ip": ip,
        "handle": data.get("handle"),
        "name": data.get("name"),
        "type": data.get("type", "IP Network"),
        "start_address": data.get("startAddress"),
        "end_address": data.get("endAddress"),
        "cidr": _cidr_from(data),
        "country": data.get("country"),
        "asn": None,
        "org": _find_org(data.get("entities")),
        "source": data.get("port43") or RDAP_BASE,
    }


async def lookup_asn(asn: int, timeout_s: float) -> dict:
    data = await _fetch_json(f"{RDAP_BASE}/autnum/{asn}", timeout_s)
    return {
        "ip": None,
        "handle": data.get("handle"),
        "name": data.get("name"),
        "type": data.get("type", "Autonomous System"),
        "start_address": str(data.get("startAutnum")) if data.get("startAutnum") else None,
        "end_address": str(data.get("endAutnum")) if data.get("endAutnum") else None,
        "cidr": None,
        "country": data.get("country"),
        "asn": {
            "number": data.get("startAutnum"),
            "name": data.get("name"),
        },
        "org": _find_org(data.get("entities")),
        "source": data.get("port43") or RDAP_BASE,
    }
