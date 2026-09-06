from datetime import datetime

import pytest

from services.whois import _as_list, _fmt_date, lookup_whois


class TestHelpers:
    def test_as_list_none(self):
        assert _as_list(None) == []

    def test_as_list_single(self):
        assert _as_list("abc") == ["abc"]

    def test_as_list_multi(self):
        assert _as_list(["a", "b"]) == ["a", "b"]

    def test_fmt_date_datetime(self):
        d = datetime(2026, 1, 2, 3, 4, 5)
        assert _fmt_date(d) == "2026-01-02T03:04:05"

    def test_fmt_date_list(self):
        d = datetime(2026, 1, 2, 3, 4, 5)
        assert _fmt_date([d]) == "2026-01-02T03:04:05"

    def test_fmt_date_none(self):
        assert _fmt_date(None) is None


class TestWhoisApi:
    async def test_page(self, client):
        res = await client.get("/tools/whois")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_invalid_domain_400(self, client):
        res = await client.post("/api/whois", json={"domain": "localhost"})
        assert res.status_code == 400

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(20):
            r = await client.post("/api/whois", json={"domain": "example.com"})
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses


@pytest.mark.network
class TestWhoisNetwork:
    async def test_lookup_real(self):
        data = await lookup_whois("example.com", 10.0)
        assert data["domain"] == "example.com"
        assert "raw_text" in data
        assert isinstance(data["status"], list)
        assert isinstance(data["nameservers"], list)
        assert "tld_privacy" in data
