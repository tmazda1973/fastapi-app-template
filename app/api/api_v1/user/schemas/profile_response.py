from datetime import datetime

from pydantic import BaseModel, Field

from app.enums.user import RoleEnum, VerifyStatusEnum

__all__ = [
    "ProfileResponse",
]


class ProfileResponse(BaseModel):
    """
    レスポンススキーマ（プロフィールAPI）
    """

    id: int = Field(description="ユーザーID")
    name: str = Field(description="名前")
    email: str = Field(description="メールアドレス")
    role: RoleEnum = Field(description="権限")
    verify_status: VerifyStatusEnum = Field(description="認証ステータス")
    last_login_at: datetime | None = Field(description="最終ログイン日時", default=None)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "田中太郎",
                "email": "tanaka@example.com",
                "role": "admin",
                "verify_status": "verified",
                "last_login_at": "2025-01-31T10:30:00Z",
            }
        }
