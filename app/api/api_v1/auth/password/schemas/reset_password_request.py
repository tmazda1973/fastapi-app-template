from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator

from app.core.i18n.validation_helper import ValidationMessage

__all__ = [
    "ResetPasswordRequest",
]


class ResetPasswordRequest(BaseModel):
    """
    リクエストスキーマ（パスワードリセット）
    """

    email: EmailStr = Field(description="メールアドレス")
    token: str = Field(description="リセットトークン")
    reset_code: str = Field(description="リセットコード")
    new_password: str = Field(description="新しいパスワード")
    confirm_password: str = Field(description="新しいパスワード（確認用）")

    @field_validator("reset_code")
    @classmethod
    def validate_reset_code(cls, v: str) -> str:
        """
        リセットコードのバリデーション
        """
        if len(v) < 6:
            raise ValueError(ValidationMessage.min_length("reset_code", 6))
        if len(v) > 10:
            raise ValueError(ValidationMessage.max_length("reset_code", 10))
        return v

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v: str, info: ValidationInfo) -> str:
        """
        パスワード確認のバリデーション
        """
        # 最小文字数チェック
        if len(v) < 8:
            raise ValueError(ValidationMessage.min_length_simple("password", 8))

        # パスワード一致チェック
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError(ValidationMessage.password_mismatch())
        return v

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """
        パスワード強度のバリデーション
        """
        if len(v) < 8:
            raise ValueError(ValidationMessage.min_length_simple("password", 8))

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(ValidationMessage.password_complexity())

        return v
