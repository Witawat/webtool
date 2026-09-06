import pytest

from core.errors import AppError
from services.header_checker import SECURITY_HEADERS, check_headers


class TestHeaderService:
    async def test_ssrf_blocked(self):
        with pytest.raises(AppError) as exc:
            await check_headers("http://127.0.0.1/", 5.0)
        assert exc.value.code == "SSRF_BLOCKED"


class TestHeaderApi:
    async def test_page(self, client):
        res = await client.get("/tools/header")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_invalid_url_400(self, client):
        res = await client.post("/api/header", json={"url": "ftp://example.com"})
        assert res.status_code == 400

    async def test_ssrf_400(self, client):
        res = await client.post("/api/header", json={"url": "http://localhost/"})
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "SSRF_BLOCKED"

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(20):
            r = await client.post("/api/header", json={"url": "http://127.0.0.1/"})
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses


@pytest.mark.network
class TestHeaderNetwork:
    async def test_public_headers(self):
        data = await check_headers("https://example.com", 10.0)
        assert data["status"] == 200
        assert isinstance(data["score"], int)
        assert 0 <= data["score"] <= 6
        assert "hsts" in data["security"]
        assert "csp" in data["security"]
        assert isinstance(data["headers"], dict)
        assert len(SECURITY_HEADERS) == 6
