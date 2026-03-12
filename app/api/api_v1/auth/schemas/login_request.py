from pydantic import Field

from app.schemas.base_response_model import BaseModel

__all__ = [
    "LoginRequest",
]


class LoginRequest(BaseModel):
    """
    リクエストスキーマ（ログインAPI）
    """

    email: str = Field(..., description="メールアドレス")
    password: str = Field(..., description="パスワード")
