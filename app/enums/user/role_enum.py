from typing_extensions import override

from app.enums.base_enum import BaseEnum

__all__ = [
    "RoleEnum",
]


class RoleEnum(str, BaseEnum):
    """
    権限
    """

    user = "user"
    admin = "admin"

    @classmethod
    @override
    def locale_mapping(cls) -> dict[str, dict[str, str]]:
        return {
            "user": {"ja": "ユーザー", "en": "User"},
            "admin": {"ja": "管理者", "en": "Admin"},
        }

    @classmethod
    @override
    def sa_enum_name(cls) -> str:
        return "user_role"
