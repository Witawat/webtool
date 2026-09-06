import pytest

from core.errors import AppError
from core.validation import (
    parse_cidr,
    parse_domain,
    parse_host,
    parse_ip,
    parse_port,
    validate_url_safe,
)


class TestParseIp:
    def test_valid_ipv4(self):
        assert str(parse_ip("8.8.8.8")) == "8.8.8.8"

    def test_valid_ipv6(self):
        assert str(parse_ip("::1")) == "::1"

    def test_invalid(self):
        with pytest.raises(AppError) as exc:
            parse_ip("not-an-ip")
        assert exc.value.code == "INVALID_INPUT"
        assert exc.value.field == "ip"


class TestParseDomain:
    def test_valid(self):
        assert parse_domain("Example.COM") == "example.com"

    def test_trailing_dot(self):
        assert parse_domain("example.com.") == "example.com"

    def test_invalid_no_tld(self):
        with pytest.raises(AppError):
            parse_domain("localhost")

    def test_invalid_symbols(self):
        with pytest.raises(AppError):
            parse_domain("exa mple.com")


class TestParseHost:
    def test_ip(self):
        assert parse_host("1.2.3.4") == "1.2.3.4"

    def test_domain(self):
        assert parse_host("Example.com") == "example.com"

    def test_empty(self):
        with pytest.raises(AppError):
            parse_host("   ")


class TestParsePort:
    def test_valid(self):
        assert parse_port("443") == 443

    def test_zero(self):
        with pytest.raises(AppError):
            parse_port(0)

    def test_too_high(self):
        with pytest.raises(AppError):
            parse_port(70000)

    def test_not_int(self):
        with pytest.raises(AppError):
            parse_port("abc")


class TestParseCidr:
    def test_valid(self):
        net = parse_cidr("192.168.1.0/24")
        assert net.prefixlen == 24

    def test_strict_false(self):
        net = parse_cidr("192.168.1.5/24")
        assert str(net.network_address) == "192.168.1.0"

    def test_invalid(self):
        with pytest.raises(AppError):
            parse_cidr("not-a-cidr")


class TestValidateUrlSafe:
    @pytest.mark.parametrize(
        "url",
        [
            "http://127.0.0.1",
            "http://localhost",
            "http://10.0.0.5/x",
            "http://169.254.169.254",
            "http://0.0.0.0",
            "http://[::1]",
            "http://192.168.1.1",
            "http://[fe80::1]",
        ],
    )
    async def test_blocks_internal(self, url):
        with pytest.raises(AppError) as exc:
            await validate_url_safe(url)
        assert exc.value.code == "SSRF_BLOCKED"

    async def test_bad_scheme(self):
        with pytest.raises(AppError) as exc:
            await validate_url_safe("ftp://example.com")
        assert exc.value.code == "INVALID_INPUT"

    async def test_strips_credentials(self):
        result = await validate_url_safe("http://user:pass@8.8.8.8/")
        assert "user" not in result and "pass" not in result

    async def test_public_ip_allowed(self):
        result = await validate_url_safe("http://8.8.8.8/path")
        assert result.startswith("http://8.8.8.8/")

    @pytest.mark.network
    async def test_public_domain_allowed(self):
        result = await validate_url_safe("https://example.com")
        assert result.startswith("https://example.com")
