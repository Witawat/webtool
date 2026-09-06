import pytest

from core.errors import AppError
from services.fetch_http import fetch_url


class TestFetchService:
    async def test_ssrf_blocked(self):
        with pytest.raises(AppError) as exc:
            await fetch_url(
                "GET", "http://127.0.0.1/", {}, None, False, 5.0, 1000, 5
            )
        assert exc.value.code == "SSRF_BLOCKED"


class TestFetchApi:
    async def test_page(self, client):
        res = await client.get("/tools/fetch")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_invalid_method_400(self, client):
        res = await client.post(
            "/api/fetch", json={"method": "TRACE", "url": "https://example.com"}
        )
        assert res.status_code == 400

    async def test_invalid_url_400(self, client):
        res = await client.post(
            "/api/fetch", json={"method": "GET", "url": "ftp://example.com"}
        )
        assert res.status_code == 400

    async def test_ssrf_400(self, client):
        res = await client.post(
            "/api/fetch", json={"method": "GET", "url": "http://127.0.0.1/"}
        )
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "SSRF_BLOCKED"

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(20):
            r = await client.post(
                "/api/fetch",
                json={"method": "GET", "url": "http://127.0.0.1/"},
            )
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses


@pytest.mark.network
class TestFetchNetwork:
    async def test_fetch_public(self):
        data = await fetch_url(
            "GET", "https://example.com", {}, None, False, 10.0, 1_000_000, 5
        )
        assert data["status"] == 200
        assert data["final_url"] == "https://example.com"
        assert "headers" in data
        assert "body" in data
        assert isinstance(data["size_bytes"], int)
