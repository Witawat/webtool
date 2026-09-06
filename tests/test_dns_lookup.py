from types import SimpleNamespace

import pytest

from services.dns_lookup import _format_value, lookup_dns


class TestFormatValue:
    def test_a(self):
        r = SimpleNamespace(to_text=lambda: "93.184.216.34")
        assert _format_value("A", r) == "93.184.216.34"

    def test_cname_trailing_dot(self):
        r = SimpleNamespace(to_text=lambda: "example.com.")
        assert _format_value("CNAME", r) == "example.com"

    def test_mx(self):
        r = SimpleNamespace(
            preference=10, exchange=SimpleNamespace(to_text=lambda: "mail.example.com.")
        )
        assert _format_value("MX", r) == "10 mail.example.com"

    def test_txt(self):
        r = SimpleNamespace(strings=[b"v=spf1 -all"])
        assert _format_value("TXT", r) == "v=spf1 -all"

    def test_srv(self):
        r = SimpleNamespace(
            priority=1,
            weight=2,
            port=5060,
            target=SimpleNamespace(to_text=lambda: "sip.example.com."),
        )
        assert _format_value("SRV", r) == "1 2 5060 sip.example.com"


class TestDnsApi:
    async def test_page(self, client):
        res = await client.get("/tools/dns")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_invalid_domain_400(self, client):
        res = await client.post("/api/dns", json={"domain": "localhost"})
        assert res.status_code == 400

    async def test_invalid_types_400(self, client):
        res = await client.post(
            "/api/dns", json={"domain": "example.com", "types": ["XXX"]}
        )
        assert res.status_code == 400

    async def test_empty_types_400(self, client):
        res = await client.post(
            "/api/dns", json={"domain": "example.com", "types": []}
        )
        assert res.status_code == 400

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(40):
            r = await client.post(
                "/api/dns", json={"domain": "example.com", "types": ["A"]}
            )
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses
        assert r.json()["error"]["code"] == "RATE_LIMITED"


@pytest.mark.network
class TestDnsNetwork:
    async def test_lookup_domain(self):
        data = await lookup_dns("example.com", ["A", "MX"], 5.0)
        assert data["domain"] == "example.com"
        types = {r["type"] for r in data["records"]}
        assert "A" in types

    async def test_reverse_lookup_ip(self):
        data = await lookup_dns("8.8.8.8", [], 5.0)
        assert data["reverse"] is not None
        assert data["records"][0]["type"] == "PTR"

    async def test_api_ok(self, client):
        res = await client.post(
            "/api/dns", json={"domain": "example.com", "types": ["A", "AAAA"]}
        )
        assert res.status_code == 200
        body = res.json()
        assert body["ok"] is True
        assert body["data"]["domain"] == "example.com"
        assert any(r["type"] == "A" for r in body["data"]["records"])
