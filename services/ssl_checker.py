from __future__ import annotations

import asyncio
import ssl
from contextlib import suppress
from datetime import UTC, datetime

from cryptography import x509
from cryptography.x509.oid import ExtensionOID, NameOID

from services.port import resolve_ip


def _host_matches(host: str, subject_cn: str, sans: list[str]) -> bool:
    host = host.lower().rstrip(".")
    candidates = [s.lower() for s in [subject_cn, *sans] if s]
    for candidate in candidates:
        if candidate.startswith("*.") and host.endswith(candidate[1:]):
            return True
        if host == candidate:
            return True
    return False


def _cert_info(cert, host: str) -> dict:
    subject_cn = ""
    for attr in cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME):
        subject_cn = attr.value
        break
    issuer_cn = ""
    for attr in cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME):
        issuer_cn = attr.value
        break

    sans: list[str] = []
    try:
        ext = cert.extensions.get_extension_for_oid(
            ExtensionOID.SUBJECT_ALTERNATIVE_NAME
        )
        sans = [
            *ext.value.get_values_for_type(x509.DNSName),
            *(str(v) for v in ext.value.get_values_for_type(x509.IPAddress)),
        ]
    except x509.ExtensionNotFound:
        pass

    days_left = (cert.not_valid_after_utc - datetime.now(UTC)).days
    warnings: list[str] = []
    if days_left < 0:
        warnings.append("expired")
    elif days_left < 30:
        warnings.append("expires_soon")
    if cert.issuer == cert.subject:
        warnings.append("self_signed")
    if not _host_matches(host, subject_cn, sans):
        warnings.append("hostname_mismatch")

    sig_oid = cert.signature_algorithm_oid
    sig_algo = getattr(sig_oid, "_name", None) or sig_oid.dotted_string

    return {
        "subject_cn": subject_cn,
        "sans": sans,
        "issuer": issuer_cn,
        "valid_from": cert.not_valid_before_utc.isoformat(),
        "valid_to": cert.not_valid_after_utc.isoformat(),
        "days_left": days_left,
        "serial": hex(cert.serial_number),
        "sig_algo": sig_algo,
        "warnings": warnings,
    }


async def check_ssl(host: str, port: int, connect_timeout_s: float) -> dict:
    ip = await resolve_ip(host)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(
                host, port, ssl=context, server_hostname=host
            ),
            timeout=connect_timeout_s,
        )
    except (OSError, ssl.SSLError, TimeoutError):
        return {
            "host": host,
            "ip": ip,
            "port": port,
            "connected": False,
            "valid": False,
            "protocol": None,
            "cipher": None,
            "cert": None,
            "warnings": [],
        }

    sslobj = writer.get_extra_info("ssl_object")
    protocol = sslobj.version()
    cipher_obj = sslobj.cipher()
    cipher = cipher_obj[0] if cipher_obj else None
    der = sslobj.getpeercert(binary_form=True)
    cert = x509.load_der_x509_certificate(der) if der else None
    writer.close()
    with suppress(OSError, ConnectionError):
        await writer.wait_closed()

    if cert is None:
        return {
            "host": host,
            "ip": ip,
            "port": port,
            "connected": True,
            "valid": False,
            "protocol": protocol,
            "cipher": cipher,
            "cert": None,
            "warnings": [],
        }

    info = _cert_info(cert, host)
    return {
        "host": host,
        "ip": ip,
        "port": port,
        "connected": True,
        "valid": info["days_left"] >= 0,
        "protocol": protocol,
        "cipher": cipher,
        "cert": info,
        "warnings": info["warnings"],
    }
