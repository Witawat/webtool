class TestHome:
    async def test_healthz(self, client):
        res = await client.get("/healthz")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}

    async def test_home_renders_17_cards(self, client):
        res = await client.get("/")
        assert res.status_code == 200
        html = res.text
        assert html.count("tool-card") == 17

    async def test_home_thai_default(self, client):
        res = await client.get("/")
        assert "เครื่องมือเครือข่าย" in res.text

    async def test_home_english_via_query(self, client):
        res = await client.get("/?lang=en")
        assert "Network Tools" in res.text

    async def test_unknown_tool_404(self, client):
        res = await client.get("/tools/nope")
        assert res.status_code == 404
