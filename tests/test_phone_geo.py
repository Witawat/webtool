from services.phone_geo import lookup_phone


class TestLookupPhone:
    def test_valid_us_number(self):
        data = lookup_phone("+16692226000", None)
        assert data["valid"] is True
        assert data["e164"] == "+16692226000"
        assert data["country"] == "US"
        assert data["region"]
        assert isinstance(data["timezones"], list)
        assert "number_type" in data

    def test_valid_with_country_hint(self):
        data = lookup_phone("(650) 253-0000", "US")
        assert data["valid"] is True
        assert data["country"] == "US"

    def test_invalid(self):
        data = lookup_phone("123", None)
        assert data["valid"] is False

    def test_garbage(self):
        data = lookup_phone("!!@@##", None)
        assert data["valid"] is False


class TestPhoneApi:
    async def test_page(self, client):
        res = await client.get("/tools/phone")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_missing_number_400(self, client):
        res = await client.post("/api/phone", json={"number": ""})
        assert res.status_code == 400

    async def test_ok(self, client):
        res = await client.post("/api/phone", json={"number": "+16692226000"})
        assert res.status_code == 200
        body = res.json()
        assert body["ok"] is True
        assert body["data"]["valid"] is True
        assert body["data"]["country"] == "US"

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(30):
            r = await client.post("/api/phone", json={"number": "+16692226000"})
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses
