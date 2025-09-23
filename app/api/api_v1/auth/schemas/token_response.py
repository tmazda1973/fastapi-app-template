from datetime import datetime

from pydantic import Field

from app.enums.user import RoleEnum
from app.schemas.base_response_model import BaseModel

__all__ = [
    "TokenResponse",
]


class TokenResponse(BaseModel):
    """
    レスポンススキーマ（ユーザー認証API）
    """

    email: str = Field(..., description="メールアドレス")
    role: RoleEnum = Field(..., description="権限")
    role_name: str = Field(..., description="権限名")
    username: str = Field(..., description="ユーザー名")
    access_token: str = Field(..., description="アクセストークン")
    refresh_token: str | None = Field(None, description="リフレッシュトークン")
    last_login_at: datetime | None = Field(None, description="最終ログイン日時")
