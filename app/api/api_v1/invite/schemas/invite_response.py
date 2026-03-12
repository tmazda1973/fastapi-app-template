"""
招待関連レスポンススキーマ
"""

from datetime import datetime

from pydantic import BaseModel

__all__ = [
    "SendInviteResponse",
    "VerifyInviteResponse",
    "AcceptInviteResponse",
]


class SendInviteResponse(BaseModel):
    """
    招待送信レスポンス
    """

    message: str
    invite_token: str
    expires_at: datetime
    expires_in_hours: int


class VerifyInviteResponse(BaseModel):
    """
    招待確認レスポンス
    """

    is_valid: bool
    user_email: str | None = None
    user_name: str | None = None
    expires_at: datetime | None = None
    expires_in_minutes: int | None = None
    error_message: str | None = None


class AcceptInviteResponse(BaseModel):
    """
    招待受諾レスポンス
    """

    message: str
    user_id: int
    user_email: str
    user_name: str
