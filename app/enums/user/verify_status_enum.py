from typing_extensions import override

from app.enums.base_enum import BaseEnum

__all__ = [
    "VerifyStatusEnum",
]


class VerifyStatusEnum(str, BaseEnum):
    """
    ユーザー認証ステータス
    """

    verified = "verified"
    unverified = "unverified"

    @classmethod
    @override
    def locale_mapping(cls) -> dict[str, dict[str, str]]:
        return {
            "verified": {"ja": "認証済", "en": "Verified"},
            "unverified": {"ja": "未認証", "en": "Unverified"},
        }

    @classmethod
    @override
    def sa_enum_name(cls) -> str:
        return "verify_status"
