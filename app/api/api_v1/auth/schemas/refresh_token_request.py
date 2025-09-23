from pydantic import Field

from app.schemas.base_response_model import BaseModel

__all__ = [
    "RefreshTokenRequest",
]


class RefreshTokenRequest(BaseModel):
    """
    リクエストスキーマ（リフレッシュトークンAPI）
    """

    refresh_token: str = Field(..., description="リフレッシュトークン")
