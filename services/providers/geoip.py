from __future__ import annotations

import asyncio
import ipaddress
import os

import httpx

from core.config import settings
from core.errors import AppError

IPAPI_URL = "http://ip-api.com/json"
IPAPI_FIELDS = (
    "status,message,query,country,countryCode,region,regionName,city,"
    "lat,lon,isp,org,as"
)


async def _lookup_ipapi(query: str, timeout_s: float) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            resp = await client.get(
                f"{IPAPI_URL}/{query}", params={"fields": IPAPI_FIELDS}
            )
            data = resp.json()
    except httpx.HTTPError:
        return None
    if not isinstance(data, dict) or data.get("status") != "success":
        return None
    return {
        "query": query,
        "ip": data.get("query"),
        "city": data.get("city"),
        "region": data.get("regionName"),
        "country": data.get("country"),
        "country_code": data.get("countryCode"),
        "lat": data.get("lat"),
        "lon": data.get("lon"),
        "isp": data.get("isp"),
        "org": data.get("org"),
        "asn": data.get("as"),
        "provider": "ip-api.com",
    }


async def _lookup_maxmind(query: str, db_path: str) -> dict | None:
    try:
        ipaddress.ip_address(query)
    except ValueError:
        from services.port import resolve_ip

        try:
            query = await resolve_ip(query)
        except AppError:
            return None

    def _read() -> dict | None:
        try:
            from geoip2.database import Reader

            with Reader(db_path) as reader:
                try:
                    return reader.city(query)
                except Exception:
                    return None
        except Exception:
            return None

    result = await asyncio.to_thread(_read)
    if result is None:
        return None
    region = None
    if result.subdivisions:
        region = result.subdivisions.most_specific.name
    return {
        "query": query,
        "ip": query,
        "city": result.city.name,
        "region": region,
        "country": result.country.name,
        "country_code": result.country.iso_code,
        "lat": result.location.latitude,
        "lon": result.location.longitude,
        "isp": None,
        "org": None,
        "asn": None,
        "provider": "MaxMind GeoLite2",
    }


async def lookup(query: str, timeout_s: float) -> dict | None:
    if settings.maxmind_db_path and os.path.exists(settings.maxmind_db_path):
        return await _lookup_maxmind(query, settings.maxmind_db_path)
    return await _lookup_ipapi(query, timeout_s)
