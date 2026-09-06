import pytest

from services.port import scan_ports


class TestScanPorts:
    async def test_localhost_range(self):
        data = await scan_ports("127.0.0.1", 1, 3, 0.3, 10)
        assert data["ip"] == "127.0.0.1"
        assert data["scanned"] == 3
        assert isinstance(data["open_ports"], list)
        assert data["closed"] == 3

    async def test_open_port_detected(self):
        data = await scan_ports("127.0.0.1", 1, 1, 0.3, 5)
        assert data["scanned"] == 1


class TestPortScanApi:
    async def test_page(self, client):
        res = await client.get("/tools/port-scan")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_domain_not_allowed_400(self, client):
        res = await client.post(
            "/api/port-scan",
            json={"ip": "example.com", "start_port": 1, "end_port": 10},
        )
        assert res.status_code == 400

    async def test_too_many_ports_400(self, client):
        res = await client.post(
            "/api/port-scan",
            json={"ip": "8.8.8.8", "start_port": 1, "end_port": 500},
        )
        assert res.status_code == 400

    async def test_ok(self, client):
        res = await client.post(
            "/api/port-scan",
            json={"ip": "127.0.0.1", "start_port": 1, "end_port": 5},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["ok"] is True
        assert body["data"]["scanned"] == 5

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(10):
            r = await client.post(
                "/api/port-scan",
                json={"ip": "127.0.0.1", "start_port": 1, "end_port": 3},
            )
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses


@pytest.mark.network
class TestPortScanNetwork:
    async def test_scan_public_open(self):
        data = await scan_ports("8.8.8.8", 443, 445, 2.0, 5)
        assert any(p["port"] == 443 for p in data["open_ports"])
