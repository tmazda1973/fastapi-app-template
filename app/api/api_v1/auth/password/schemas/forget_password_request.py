from pydantic import BaseModel, EmailStr, Field

__all__ = [
    "ForgotPasswordRequest",
]


class ForgotPasswordRequest(BaseModel):
    """
    リクエストスキーマ（パスワードリマインダー）
    """

    email: EmailStr = Field(description="メールアドレス")
