from pydantic import BaseModel, Field, ValidationInfo, field_validator

from app.core.i18n.validation_helper import ValidationMessage

__all__ = [
    "ChangePasswordRequest",
]


class ChangePasswordRequest(BaseModel):
    """
    リクエストスキーマ（パスワード変更）
    """

    current_password: str = Field(description="現在のパスワード")
    new_password: str = Field(description="新しいパスワード")
    confirm_password: str = Field(description="新しいパスワード（確認用）")

    @field_validator("current_password")
    @classmethod
    def validate_current_password(cls, v: str) -> str:
        """
        バリデーション（現在のパスワード）
        """
        if not v.strip():
            raise ValueError(ValidationMessage.field_required("password"))

        return v

    @field_validator("confirm_password")
    @classmethod
    def validate_confirm_password(cls, v: str, info: ValidationInfo) -> str:
        """
        バリデーション（パスワード確認）
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
        バリデーション（新しいパスワード）
        """
        if len(v) < 8:
            raise ValueError(ValidationMessage.min_length_simple("password", 8))

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(ValidationMessage.password_complexity())

        return v
