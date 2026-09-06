from core.i18n import all_strings, t


class TestI18n:
    def test_th_default(self):
        assert t("th", "nav.home") == "หน้าแรก"

    def test_en(self):
        assert t("en", "nav.home") == "Home"

    def test_unknown_key_returns_key(self):
        assert t("th", "no.such.key") == "no.such.key"

    def test_format_args(self):
        assert t("th", "common.duration", ms=21) == "ใช้เวลา 21 ms"
        assert t("en", "common.duration", ms=21) == "took 21 ms"

    def test_all_strings_has_error_keys(self):
        data = all_strings("th")
        assert data["err.INVALID_INPUT"]
        assert data["err.RATE_LIMITED"]

    def test_all_strings_full_coverage(self):
        th = all_strings("th")
        en = all_strings("en")
        assert set(th.keys()) == set(en.keys())

    def test_every_tool_has_name_and_desc(self):
        from core.config import TOOLS

        for tool in TOOLS:
            slug = tool["slug"]
            for lang in ("th", "en"):
                name = t(lang, f"tool.{slug}.name")
                desc = t(lang, f"tool.{slug}.desc")
                assert name != f"tool.{slug}.name", f"missing name {slug} {lang}"
                assert desc != f"tool.{slug}.desc", f"missing desc {slug} {lang}"
