import pytest

from core.errors import AppError
from core.rate_limit import RateLimiter, require_rate


class TestRateLimiter:
    def test_allows_within_limit(self):
        rl = RateLimiter()
        for _ in range(5):
            assert rl.allow("127.0.0.1", "port-checker", 5) is True

    def test_blocks_over_limit(self):
        rl = RateLimiter()
        for _ in range(5):
            rl.allow("127.0.0.1", "x", 5)
        assert rl.allow("127.0.0.1", "x", 5) is False

    def test_separate_keys_isolated(self):
        rl = RateLimiter()
        for _ in range(5):
            rl.allow("127.0.0.1", "a", 5)
        assert rl.allow("127.0.0.1", "b", 5) is True

    def test_separate_ips_isolated(self):
        rl = RateLimiter()
        for _ in range(5):
            rl.allow("1.1.1.1", "x", 5)
        assert rl.allow("2.2.2.2", "x", 5) is True


class TestRequireRate:
    def test_over_limit_raises(self):
        with pytest.raises(AppError) as exc:
            for _ in range(6):
                require_rate("127.0.0.1", "rate-test", 5)
        assert exc.value.code == "RATE_LIMITED"
        assert exc.value.status == 429
