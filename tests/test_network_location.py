from unittest.mock import AsyncMock, patch

import pytest

from services.providers.geoip import lookup as geoip_lookup


class TestNetworkLocationApi:
    async def test_page(self, client):
        res = await client.get("/tools/network-location")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_invalid_query_400(self, client):
        res = await client.post("/api/network-location", json={"query": "!!"})
        assert res.status_code == 400

    async def test_internal_ip_ssrf_400(self, client):
        res = await client.post("/api/network-location", json={"query": "127.0.0.1"})
        assert res.status_code == 400
        assert res.json()["error"]["code"] == "SSRF_BLOCKED"

    async def test_ok_with_mock_provider(self, client):
        fake = AsyncMock(
            return_value={
                "query": "8.8.8.8",
                "ip": "8.8.8.8",
                "city": "Mountain View",
                "region": "California",
                "country": "United States",
                "country_code": "US",
                "lat": 37.4056,
                "lon": -122.0775,
                "isp": "Google LLC",
                "org": "Google LLC",
                "asn": "AS15169",
                "provider": "ip-api.com",
            }
        )
        with patch("routers.network_location.geoip_lookup", fake):
            res = await client.post("/api/network-location", json={"query": "8.8.8.8"})
        assert res.status_code == 200
        body = res.json()
        assert body["ok"] is True
        assert body["data"]["city"] == "Mountain View"
        assert body["data"]["provider"] == "ip-api.com"

    async def test_provider_none_404(self, client):
        fake = AsyncMock(return_value=None)
        with patch("routers.network_location.geoip_lookup", fake):
            res = await client.post(
                "/api/network-location", json={"query": "8.8.8.8"}
            )
        assert res.status_code == 404

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(20):
            r = await client.post("/api/network-location", json={"query": "8.8.8.8"})
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses


@pytest.mark.network
class TestGeoipNetwork:
    async def test_ipapi_http_real(self):
        data = await geoip_lookup("8.8.8.8", 10.0)
        assert data is not None
        assert data["provider"] == "ip-api.com"
        assert data["ip"] == "8.8.8.8"
        assert data["lat"] is not None
        assert data["lon"] is not None
