"""
エラーレスポンススキーマ
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

__all__ = [
    "APIErrorDetail",
    "APIErrorResponse",
    "APISuccessResponse",
]


class APIErrorDetail(BaseModel):
    """
    エラー詳細情報
    """

    field: Optional[str] = None
    code: Optional[str] = None
    message: Optional[str] = None


class APIErrorResponse(BaseModel):
    """
    APIエラーレスポンス
    """

    success: bool = Field(default=False, description="成功フラグ")
    error_code: str = Field(description="エラーコード")
    message: str = Field(description="エラーメッセージ")
    details: Optional[list[APIErrorDetail]] = Field(
        default=None,
        description="詳細エラー情報",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="エラー発生時刻",
    )
    trace_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="トレースID",
    )
    request_id: Optional[str] = Field(default=None, description="リクエストID")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class APISuccessResponse(BaseModel):
    """
    レスポンススキーマ（正常系）
    """

    success: bool = Field(default=True, description="成功フラグ")
    message: str = Field(default="Success", description="成功メッセージ")
    data: Optional[Any] = Field(default=None, description="レスポンスデータ")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="レスポンス時刻",
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
