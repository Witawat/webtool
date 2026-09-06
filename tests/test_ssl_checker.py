import pytest

from services.ssl_checker import _host_matches, check_ssl


class TestHostMatches:
    def test_exact_domain(self):
        assert _host_matches("example.com", "example.com", []) is True

    def test_wildcard(self):
        assert _host_matches("www.example.com", "*.example.com", []) is True

    def test_mismatch(self):
        assert _host_matches("other.com", "example.com", []) is False

    def test_san_match(self):
        assert _host_matches("api.example.com", "example.com", ["api.example.com"]) is True


class TestCheckSsl:
    async def test_connection_refused(self):
        data = await check_ssl("127.0.0.1", 1, 1.0)
        assert data["connected"] is False
        assert data["valid"] is False
        assert data["warnings"] == []

    async def test_unknown_host_raises(self):
        from core.errors import AppError

        with pytest.raises(AppError) as exc:
            await check_ssl("no-such-host-xyz.invalid", 443, 2.0)
        assert exc.value.code == "NOT_FOUND"


class TestSslApi:
    async def test_page(self, client):
        res = await client.get("/tools/ssl")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_invalid_host_400(self, client):
        res = await client.post("/api/ssl", json={"host": "localhost"})
        assert res.status_code == 400

    async def test_invalid_port_400(self, client):
        res = await client.post("/api/ssl", json={"host": "example.com", "port": 0})
        assert res.status_code == 400

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(20):
            r = await client.post("/api/ssl", json={"host": "127.0.0.1", "port": 1})
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses


@pytest.mark.network
class TestSslNetwork:
    async def test_public_cert(self):
        data = await check_ssl("example.com", 443, 5.0)
        assert data["connected"] is True
        assert data["protocol"] is not None
        assert data["cipher"] is not None
        assert data["cert"] is not None
        assert data["cert"]["subject_cn"]
        assert isinstance(data["cert"]["sans"], list)
        assert isinstance(data["cert"]["days_left"], int)
        assert "serial" in data["cert"]
