from services.bulk import run_bulk


class TestRunBulk:
    async def test_subnet_sync(self):
        data = await run_bulk("subnet-calc", ["192.168.1.0/24"], "en")
        assert data["count"] == 1
        assert data["results"][0]["ok"] is True
        assert data["results"][0]["data"]["usable_hosts"] == 254

    async def test_phone_sync(self):
        data = await run_bulk("phone", ["+16692226000", "garbage"], "en")
        assert data["count"] == 2
        assert data["results"][0]["ok"] is True
        assert data["results"][0]["data"]["valid"] is True
        assert data["results"][1]["ok"] is True
        assert data["results"][1]["data"]["valid"] is False

    async def test_unknown_slug(self):
        from core.errors import AppError

        try:
            await run_bulk("nope", ["x"], "en")
        except AppError as exc:
            assert exc.field == "slug"
        else:
            raise AssertionError("should raise")

    async def test_too_many_values(self):
        from core.errors import AppError

        try:
            await run_bulk("dns", list(range(20)), "en")
        except AppError as exc:
            assert exc.field == "values"
        else:
            raise AssertionError("should raise")


class TestBulkApi:
    async def test_page(self, client):
        res = await client.get("/tools/bulk")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_ok_subnet(self, client):
        res = await client.post(
            "/api/bulk",
            json={"slug": "subnet-calc", "values": ["192.168.1.0/24"]},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["ok"] is True
        assert body["data"]["results"][0]["ok"] is True

    async def test_invalid_slug_400(self, client):
        res = await client.post("/api/bulk", json={"slug": "nope", "values": ["x"]})
        assert res.status_code == 400

    async def test_missing_values_400(self, client):
        res = await client.post("/api/bulk", json={"slug": "dns"})
        assert res.status_code == 400

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(12):
            r = await client.post(
                "/api/bulk",
                json={"slug": "subnet-calc", "values": ["192.168.1.0/24"]},
            )
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses
