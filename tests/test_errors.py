import pytest

from core.errors import STATUS_BY_CODE, AppError


class TestAppError:
    @pytest.mark.parametrize(
        "code,status",
        list(STATUS_BY_CODE.items()),
    )
    def test_status_map(self, code, status):
        err = AppError(code)
        assert err.status == status

    def test_custom_status_wins(self):
        err = AppError("INVALID_INPUT", status=422)
        assert err.status == 422

    def test_message_th(self):
        err = AppError("RATE_LIMITED")
        assert err.message("th") == "เรียกใช้งานถี่เกินไป กรุณารอสักครู่แล้วลองใหม่"

    def test_message_en(self):
        err = AppError("RATE_LIMITED")
        assert err.message("en") == "Too many requests, please slow down and try again"

    def test_to_dict_includes_field(self):
        err = AppError("INVALID_INPUT", field="port")
        d = err.to_dict("th")
        assert d["code"] == "INVALID_INPUT"
        assert d["field"] == "port"
        assert "message" in d

    def test_unknown_code_defaults_internal(self):
        err = AppError("WHATEVER")
        assert err.status == 500
