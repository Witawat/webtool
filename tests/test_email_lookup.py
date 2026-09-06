import pytest

from core.config import settings
from core.errors import AppError
from core.validation import parse_email
from services.providers.email import reverse_email_lookup


class TestParseEmail:
    def test_valid(self):
        assert parse_email("User@Example.com") == "user@example.com"

    def test_invalid(self):
        for bad in ("not-an-email", "a@b", "a@@b.com", "@example.com"):
            with pytest.raises(AppError):
                parse_email(bad)


class TestEmailLookupApi:
    async def test_page(self, client):
        res = await client.get("/tools/email-lookup")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_no_key_503(self, client):
        if settings.email_api_key:
            return
        res = await client.post(
            "/api/email-lookup", json={"email": "user@example.com"}
        )
        assert res.status_code == 503
        assert res.json()["error"]["code"] == "TOOL_DISABLED"

    async def test_invalid_email_400(self, client):
        res = await client.post("/api/email-lookup", json={"email": "bad"})
        assert res.status_code == 400

    async def test_ok_with_key(self, client, monkeypatch):
        monkeypatch.setattr(settings, "email_api_key", "test-key")
        res = await client.post(
            "/api/email-lookup", json={"email": "user@example.com"}
        )
        assert res.status_code == 200
        body = res.json()
        assert body["ok"] is True
        assert body["data"]["email"] == "user@example.com"
        assert body["data"]["available"] is True

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(6):
            r = await client.post(
                "/api/email-lookup", json={"email": "user@example.com"}
            )
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses


async def test_provider_no_key_raises(monkeypatch):
    monkeypatch.setattr(settings, "email_api_key", "")
    with pytest.raises(AppError) as exc:
        await reverse_email_lookup("user@example.com", 5.0)
    assert exc.value.code == "TOOL_DISABLED"
    assert exc.value.status == 503


async def test_provider_with_key(monkeypatch):
    monkeypatch.setattr(settings, "email_api_key", "test-key")
    data = await reverse_email_lookup("user@example.com", 5.0)
    assert data["email"] == "user@example.com"
    assert data["available"] is True
