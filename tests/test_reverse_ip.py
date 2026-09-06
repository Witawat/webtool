from unittest.mock import AsyncMock, patch

import pytest

from core.errors import AppError
from services.providers.reverse_ip import (
    is_upstream_error,
    parse_domains,
    reverse_ip_lookup,
)


class TestHelpers:
    def test_parse_domains(self):
        assert parse_domains("a.com\nb.net\n") == ["a.com", "b.net"]

    def test_is_upstream_error_error(self):
        assert is_upstream_error("error invalid input") is True

    def test_is_upstream_error_limit(self):
        assert is_upstream_error("API count exceeded - Increase Max Quota") is True

    def test_is_upstream_error_ok(self):
        assert is_upstream_error("a.com\nb.net") is False

    def test_is_upstream_error_empty(self):
        assert is_upstream_error("") is True


class TestReverseIpApi:
    async def test_page(self, client):
        res = await client.get("/tools/reverse-ip")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_invalid_ip_400(self, client):
        res = await client.post("/api/reverse-ip", json={"ip": "not-an-ip"})
        assert res.status_code == 400

    async def test_internal_ip_ssrf_400(self, client):
        res = await client.post("/api/reverse-ip", json={"ip": "127.0.0.1"})
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "SSRF_BLOCKED"

    async def test_ok_with_mock_provider(self, client):
        fake = AsyncMock(
            return_value={
                "ip": "8.8.8.8",
                "domains": ["a.com", "b.net"],
                "count": 2,
                "provider": "HackerTarget",
            }
        )
        with patch("routers.reverse_ip.reverse_ip_lookup", fake):
            res = await client.post("/api/reverse-ip", json={"ip": "8.8.8.8"})
        assert res.status_code == 200
        body = res.json()
        assert body["ok"] is True
        assert body["data"]["count"] == 2
        assert body["data"]["provider"] == "HackerTarget"

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(8):
            r = await client.post("/api/reverse-ip", json={"ip": "8.8.8.8"})
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses


@pytest.mark.network
class TestReverseIpNetwork:
    async def test_lookup(self):
        try:
            data = await reverse_ip_lookup("8.8.8.8", 10.0, "")
        except AppError as exc:
            assert exc.code == "UPSTREAM_ERROR"
        else:
            assert "domains" in data
            assert data["ip"] == "8.8.8.8"
