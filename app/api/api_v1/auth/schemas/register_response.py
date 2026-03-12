from pydantic import Field

from app.enums.user import RoleEnum
from app.schemas.base_response_model import BaseModel

__all__ = [
    "RegisterResponse",
]


class RegisterResponse(BaseModel):
    """
    レスポンススキーマ（ユーザー登録API）
    """

    message: str = Field(..., description="メッセージ")
    user_id: int = Field(..., description="ユーザーID")
    user_email: str = Field(..., description="メールアドレス")
    user_name: str = Field(..., description="ユーザー名")
    role: RoleEnum = Field(..., description="権限")
    verify_status: str = Field(..., description="認証ステータス")
