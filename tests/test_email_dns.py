import pytest

from services.email_dns import analyze_email_dns


class TestEmailDnsApi:
    async def test_page(self, client):
        res = await client.get("/tools/email-dns")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_invalid_domain_400(self, client):
        res = await client.post("/api/email-dns", json={"domain": "localhost"})
        assert res.status_code == 400

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(40):
            r = await client.post("/api/email-dns", json={"domain": "example.com"})
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses


@pytest.mark.network
class TestEmailDnsNetwork:
    async def test_gmail(self):
        data = await analyze_email_dns("gmail.com", 5.0)
        assert data["domain"] == "gmail.com"
        assert data["mx"]
        assert data["spf"]["present"] is True
        assert data["spf"]["pass"] is True
        assert isinstance(data["dkim"]["records"], list)
        assert "dmarc" in data
        assert data["summary"] in ("pass", "warn", "fail")
