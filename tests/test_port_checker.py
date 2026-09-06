import pytest

from core.errors import AppError
from services.port import check_port


class TestCheckPort:
    async def test_closed_localhost(self):
        data = await check_port("127.0.0.1", 1, 0.5)
        assert data["state"] in ("closed", "filtered")
        assert data["port"] == 1
        assert data["ip"] == "127.0.0.1"
        assert "latency_ms" in data
        assert data["service"] is None

    async def test_known_service_name(self):
        data = await check_port("127.0.0.1", 443, 0.5)
        assert data["service"] == "HTTPS"

    async def test_unknown_host_raises(self):
        with pytest.raises(AppError) as exc:
            await check_port("no-such-host-xyz.invalid", 80, 1.0)
        assert exc.value.code == "NOT_FOUND"

    @pytest.mark.network
    async def test_open_public(self):
        data = await check_port("1.1.1.1", 443, 5.0)
        assert data["state"] == "open"
        assert data["ip"] == "1.1.1.1"


class TestPortCheckerApi:
    async def test_page(self, client):
        res = await client.get("/tools/port-checker")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_invalid_input_400(self, client):
        res = await client.post(
            "/api/port-checker", json={"host": "localhost", "port": 80}
        )
        assert res.status_code == 400

        res2 = await client.post(
            "/api/port-checker", json={"host": "example.com", "port": 0}
        )
        assert res2.status_code == 400

    async def test_ok(self, client):
        res = await client.post(
            "/api/port-checker", json={"host": "8.8.8.8", "port": 443}
        )
        assert res.status_code == 200
        body = res.json()
        assert body["ok"] is True
        d = body["data"]
        assert d["host"] == "8.8.8.8"
        assert d["ip"] == "8.8.8.8"
        assert d["port"] == 443
        assert d["state"] in ("open", "filtered", "closed")
        assert "duration_ms" in body

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(20):
            r = await client.post(
                "/api/port-checker", json={"host": "8.8.8.8", "port": 443}
            )
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses
        assert r.json()["error"]["code"] == "RATE_LIMITED"
