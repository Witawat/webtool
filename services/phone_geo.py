from __future__ import annotations

import phonenumbers
from phonenumbers import carrier, geocoder
from phonenumbers import timezone as phone_tz

_TYPE_NAMES = {
    -1: "UNKNOWN",
    0: "FIXED_LINE",
    1: "MOBILE",
    2: "FIXED_LINE_OR_MOBILE",
    3: "TOLL_FREE",
    4: "PREMIUM_RATE",
    5: "SHARED_COST",
    6: "VOIP",
    7: "PERSONAL_NUMBER",
    8: "PAGER",
    9: "UAN",
    10: "VOICEMAIL",
}


def lookup_phone(number: str, country: str | None) -> dict:
    try:
        parsed = phonenumbers.parse(number, country or None)
    except phonenumbers.NumberParseException:
        return {"number": number, "valid": False}

    if not phonenumbers.is_valid_number(parsed):
        return {"number": number, "valid": False}

    return {
        "number": number,
        "valid": True,
        "e164": phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.E164
        ),
        "country": phonenumbers.region_code_for_number(parsed),
        "region": geocoder.description_for_number(parsed, "en"),
        "carrier": carrier.name_for_number(parsed, "en"),
        "timezones": list(phone_tz.time_zones_for_number(parsed)),
        "number_type": _TYPE_NAMES.get(phonenumbers.number_type(parsed), "UNKNOWN"),
    }
