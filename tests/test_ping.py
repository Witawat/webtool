import pytest

from services.ping import ping_host


class TestPingHost:
    async def test_schema_localhost(self):
        data = await ping_host("127.0.0.1", 1, 1.0)
        assert data["host"] == "127.0.0.1"
        assert data["ip"] == "127.0.0.1"
        assert "sent" in data
        assert "received" in data
        assert "loss_pct" in data
        assert "rtt_ms" in data
        assert isinstance(data["alive"], bool)
        assert isinstance(data["icmp"], bool)

    async def test_unknown_host_raises(self):
        from core.errors import AppError

        with pytest.raises(AppError) as exc:
            await ping_host("no-such-host-xyz.invalid", 1, 1.0)
        assert exc.value.code == "NOT_FOUND"


class TestPingApi:
    async def test_page(self, client):
        res = await client.get("/tools/ping")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_invalid_host_400(self, client):
        res = await client.post("/api/ping", json={"host": "localhost"})
        assert res.status_code == 400

    async def test_count_too_high_400(self, client):
        res = await client.post(
            "/api/ping", json={"host": "example.com", "count": 50}
        )
        assert res.status_code == 400

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(20):
            r = await client.post(
                "/api/ping", json={"host": "127.0.0.1", "count": 1}
            )
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses


@pytest.mark.network
class TestPingNetwork:
    async def test_alive_public(self):
        data = await ping_host("1.1.1.1", 2, 2.0)
        assert data["alive"] is True
        assert data["ip"] == "1.1.1.1"
