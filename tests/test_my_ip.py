
from services.my_ip import get_my_ip


class TestGetMyIp:
    async def test_localhost_schema(self):
        data = await get_my_ip("127.0.0.1")
        assert data["ip"] == "127.0.0.1"
        assert data["version"] == 4
        assert "hostname" in data
        assert "geo" in data

    async def test_ipv6_version(self):
        data = await get_my_ip("::1")
        assert data["version"] == 6


class TestMyIpApi:
    async def test_page(self, client):
        res = await client.get("/tools/my-ip")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_ok(self, client):
        res = await client.post("/api/my-ip")
        assert res.status_code == 200
        body = res.json()
        assert body["ok"] is True
        assert "ip" in body["data"]
        assert "version" in body["data"]
        assert "hostname" in body["data"]
        assert "geo" in body["data"]
        assert "duration_ms" in body

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(70):
            r = await client.post("/api/my-ip")
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses
        assert r.json()["error"]["code"] == "RATE_LIMITED"
