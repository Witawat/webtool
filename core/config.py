from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "WebTool"
    version: str = "0.1.0"
    host: str = "127.0.0.1"
    port: int = 8000
    default_lang: str = "th"

    port_timeout_s: float = 3.0
    scan_port_timeout_s: float = 1.5
    scan_max_ports: int = 100
    scan_max_parallel: int = 20
    ping_count: int = 4
    ping_timeout_s: float = 2.0
    trace_max_hops: int = 30
    trace_hop_timeout_s: float = 2.0
    dns_timeout_s: float = 5.0
    ssl_connect_timeout_s: float = 10.0
    whois_timeout_s: float = 10.0
    http_timeout_s: float = 10.0
    http_max_redirects: int = 5
    http_max_body: int = 1_000_000
    geoip_timeout_s: float = 5.0
    trust_proxy: bool = False
    global_semaphore: int = 50

    maxmind_key: str = ""
    maxmind_db_path: str = ""
    hackertarget_key: str = ""
    email_api_key: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

TOOLS = [
    {"slug": "my-ip", "icon": "🖥️", "group": "check"},
    {"slug": "port-checker", "icon": "🔌", "group": "check"},
    {"slug": "port-scan", "icon": "📡", "group": "check"},
    {"slug": "ping", "icon": "📶", "group": "check"},
    {"slug": "traceroute", "icon": "🗺️", "group": "check"},
    {"slug": "dns", "icon": "🌐", "group": "dns"},
    {"slug": "email-dns", "icon": "📧", "group": "dns"},
    {"slug": "ssl", "icon": "🔒", "group": "ssl"},
    {"slug": "whois", "icon": "🏛️", "group": "whois"},
    {"slug": "asn-rdap", "icon": "🧩", "group": "whois"},
    {"slug": "fetch", "icon": "🚀", "group": "http"},
    {"slug": "header", "icon": "📋", "group": "http"},
    {"slug": "subnet-calc", "icon": "🧮", "group": "calc"},
    {"slug": "phone", "icon": "📱", "group": "phone"},
    {"slug": "reverse-ip", "icon": "🔁", "group": "reverse"},
    {"slug": "network-location", "icon": "📍", "group": "geo"},
    {"slug": "email-lookup", "icon": "🕵️", "group": "reverse"},
]
