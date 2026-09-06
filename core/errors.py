from __future__ import annotations

from typing import Any

STATUS_BY_CODE = {
    "INVALID_INPUT": 400,
    "SSRF_BLOCKED": 400,
    "NOT_FOUND": 404,
    "RATE_LIMITED": 429,
    "UPSTREAM_ERROR": 502,
    "TIMEOUT": 504,
    "TOOL_DISABLED": 503,
    "INTERNAL": 500,
}

ERROR_MESSAGES = {
    "th": {
        "INVALID_INPUT": "ข้อมูลที่ส่งมาไม่ถูกต้อง",
        "SSRF_BLOCKED": "URL หรือโฮสต์ที่ขอไม่อนุญาตให้เข้าถึง (เป็นเป้าหมายภายใน)",
        "NOT_FOUND": "ไม่พบเป้าหมายที่ระบุ",
        "RATE_LIMITED": "เรียกใช้งานถี่เกินไป กรุณารอสักครู่แล้วลองใหม่",
        "UPSTREAM_ERROR": "บริการภายนอกมีปัญหา กรุณาลองใหม่อีกครั้ง",
        "TIMEOUT": "การทำงานใช้เวลานานเกินไป กรุณาลองใหม่ (timeout)",
        "TOOL_DISABLED": "เครื่องมือนี้ยังไม่เปิดใช้งาน (ต้องตั้งค่า API key)",
        "INTERNAL": "เกิดข้อผิดพลาดภายในระบบ กรุณาลองใหม่",
    },
    "en": {
        "INVALID_INPUT": "Invalid input",
        "SSRF_BLOCKED": "The requested URL or host is not allowed (internal target)",
        "NOT_FOUND": "Target not found",
        "RATE_LIMITED": "Too many requests, please slow down and try again",
        "UPSTREAM_ERROR": "Upstream service error, please try again",
        "TIMEOUT": "Operation timed out, please try again",
        "TOOL_DISABLED": "This tool is disabled (API key required)",
        "INTERNAL": "Internal server error, please try again",
    },
}


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message_key: str | None = None,
        status: int | None = None,
        field: str | None = None,
        extra: dict | None = None,
    ) -> None:
        self.code = code
        self.message_key = message_key or code
        self.status = status or STATUS_BY_CODE.get(code, 500)
        self.field = field
        self.extra = extra or {}
        super().__init__(self.code)

    def message(self, lang: str = "th") -> str:
        table = ERROR_MESSAGES.get(lang, ERROR_MESSAGES["th"])
        msg = table.get(self.message_key, self.message_key)
        if self.extra:
            try:
                return msg.format(**self.extra)
            except (KeyError, IndexError):
                return msg
        return msg

    def to_dict(self, lang: str = "th") -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "message": self.message(lang)}
        if self.field:
            payload["field"] = self.field
        return payload
