import pytest

from core.errors import AppError
from services.traceroute import traceroute_host


class TestTracerouteHost:
    async def test_unknown_host_raises(self):
        with pytest.raises(AppError) as exc:
            await traceroute_host("no-such-host-xyz.invalid", 5, 1.0)
        assert exc.value.code == "NOT_FOUND"


class TestTracerouteApi:
    async def test_page(self, client):
        res = await client.get("/tools/traceroute")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_invalid_host_400(self, client):
        res = await client.post("/api/traceroute", json={"host": "localhost"})
        assert res.status_code == 400

    async def test_max_hops_400(self, client):
        res = await client.post(
            "/api/traceroute", json={"host": "example.com", "max_hops": 100}
        )
        assert res.status_code == 400

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(10):
            r = await client.post(
                "/api/traceroute", json={"host": "127.0.0.1", "max_hops": 3}
            )
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses


@pytest.mark.network
class TestTracerouteNetwork:
    async def test_trace_public(self):
        data = await traceroute_host("1.1.1.1", 8, 1.0)
        assert data["host"] == "1.1.1.1"
        assert data["ip"] == "1.1.1.1"
        assert isinstance(data["hops"], list)
        assert len(data["hops"]) > 0
        assert all("ttl" in h and "rtt_ms" in h for h in data["hops"])
