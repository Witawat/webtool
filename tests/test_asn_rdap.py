import pytest

from services.rdap_asn import _cidr_from, _find_org, _vcard_name, lookup_asn, lookup_ip


class TestParsers:
    def test_vcard_name(self):
        entity = {"vcardArray": ["vcard", [["fn", {}, "text", "Example Org"]]]}
        assert _vcard_name(entity) == "Example Org"

    def test_find_org_prefers_registrant(self):
        entities = [
            {"handle": "h2", "roles": ["technical"], "vcardArray": ["vcard", [["fn", {}, "text", "Tech"]]]},
            {"handle": "h1", "roles": ["registrant"], "vcardArray": ["vcard", [["fn", {}, "text", "Owner"]]]},
        ]
        org = _find_org(entities)
        assert org == {"handle": "h1", "name": "Owner"}

    def test_cidr(self):
        data = {"cidr0_cidrs": [{"v4prefix": "8.8.8.0", "length": 24}]}
        assert _cidr_from(data) == "8.8.8.0/24"


class TestAsnRdapApi:
    async def test_page(self, client):
        res = await client.get("/tools/asn-rdap")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_invalid_query_400(self, client):
        res = await client.post("/api/asn-rdap", json={"query": "localhost"})
        assert res.status_code == 400

    async def test_invalid_asn_400(self, client):
        res = await client.post("/api/asn-rdap", json={"query": "0"})
        assert res.status_code == 400

    async def test_rate_limited(self, client):
        statuses = set()
        for _ in range(30):
            r = await client.post("/api/asn-rdap", json={"query": "8.8.8.8"})
            statuses.add(r.status_code)
            if r.status_code == 429:
                break
        assert 429 in statuses


@pytest.mark.network
class TestAsnRdapNetwork:
    async def test_lookup_ip(self):
        data = await lookup_ip("8.8.8.8", 10.0)
        assert data["ip"] == "8.8.8.8"
        assert data["handle"]
        assert data["type"]
        assert data["cidr"]
        assert data["source"]

    async def test_lookup_asn(self):
        data = await lookup_asn(15169, 10.0)
        assert data["asn"]["number"] == 15169
        assert data["asn"]["name"]
