from typing_extensions import override

from app.enums.base_enum import BaseEnum

__all__ = [
    "InviteStatusEnum",
]


class InviteStatusEnum(str, BaseEnum):
    """
    ユーザー招待状態
    """

    accepted = "accepted"
    pending = "pending"
    expired = "expired"

    @classmethod
    @override
    def locale_mapping(cls) -> dict[str, dict[str, str]]:
        return {
            "accepted": {"ja": "認証済", "en": "Invite Accepted"},
            "pending": {"ja": "認証待ち", "en": "Invite Pending"},
            "expired": {"ja": "期限切れ", "en": "Invite Expired"},
        }

    @classmethod
    @override
    def sa_enum_name(cls) -> str:
        return "invite_status"
