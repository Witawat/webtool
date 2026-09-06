from core.errors import AppError
from core.validation import parse_cidr
from services.subnet_calc import calculate_subnet


class TestCalculateSubnet:
    def test_ipv4_24(self):
        data = calculate_subnet(parse_cidr("192.168.1.0/24"))
        assert data["network"] == "192.168.1.0"
        assert data["broadcast"] == "192.168.1.255"
        assert data["netmask"] == "255.255.255.0"
        assert data["wildcard"] == "0.0.0.255"
        assert data["first_host"] == "192.168.1.1"
        assert data["last_host"] == "192.168.1.254"
        assert data["usable_hosts"] == 254
        assert data["total_hosts"] == 256
        assert data["prefix"] == 24
        assert data["ip_version"] == 4
        assert data["cidr"] == "192.168.1.0/24"

    def test_strict_false_normalizes(self):
        data = calculate_subnet(parse_cidr("10.0.0.5/8"))
        assert data["network"] == "10.0.0.0"
        assert data["cidr"] == "10.0.0.0/8"
        assert data["usable_hosts"] == 16777214

    def test_slash_32(self):
        data = calculate_subnet(parse_cidr("1.2.3.4/32"))
        assert data["first_host"] == "1.2.3.4"
        assert data["last_host"] == "1.2.3.4"
        assert data["usable_hosts"] == 1
        assert data["total_hosts"] == 1

    def test_slash_31(self):
        data = calculate_subnet(parse_cidr("192.168.1.0/31"))
        assert data["first_host"] == "192.168.1.0"
        assert data["last_host"] == "192.168.1.1"
        assert data["usable_hosts"] == 2

    def test_ipv6(self):
        data = calculate_subnet(parse_cidr("2001:db8::/64"))
        assert data["ip_version"] == 6
        assert data["prefix"] == 64
        assert data["first_host"] == "2001:db8::1"
        assert data["total_hosts"] == 18446744073709551616

    def test_invalid_raises(self):
        try:
            parse_cidr("not-a-cidr")
        except AppError as exc:
            assert exc.code == "INVALID_INPUT"
        else:
            raise AssertionError("should raise")


class TestSubnetCalcApi:
    async def test_page(self, client):
        res = await client.get("/tools/subnet-calc")
        assert res.status_code == 200
        assert 'id="tool-form"' in res.text

    async def test_ok(self, client):
        res = await client.post(
            "/api/subnet-calc", json={"cidr": "192.168.1.0/24"}
        )
        assert res.status_code == 200
        body = res.json()
        assert body["ok"] is True
        assert body["data"]["usable_hosts"] == 254
        assert "duration_ms" in body

    async def test_invalid_400(self, client):
        res = await client.post("/api/subnet-calc", json={"cidr": "999.1.1.0/x"})
        assert res.status_code == 400
