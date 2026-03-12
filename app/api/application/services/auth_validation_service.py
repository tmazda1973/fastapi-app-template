"""
認証バリデーションサービス
"""

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.api_v1.auth.schemas import LoginRequest
from app.core.errors.codes import ErrorCode
from app.core.exception import BadRequestException, UnauthorizedException
from app.core.i18n.error_message import ErrorMessage
from app.db.database import get_read_db
from app.enums.user import VerifyStatusEnum
from app.models import User

__all__ = [
    "is_exist_user_by_email",
]


def is_exist_user_by_email(
    request: LoginRequest,
    db: Session = Depends(get_read_db),
) -> bool:
    """
    ユーザー存在確認

    - ユーザーが存在し、認証済みであるかを確認する

    :param request: リクエストデータ
    :param db: DBセッション
    :return: True ユーザーが存在する, False ユーザーが存在しない
    :raises UnauthorizedException: ユーザーが存在しない、または未認証の場合
    :raises BadRequestException: その他のエラーの場合
    """

    try:
        query = select(User).where(
            User.email == request.email,
        )
        result = db.execute(query).scalars().first()
        if result:
            if result.verify_status == VerifyStatusEnum.unverified:
                raise UnauthorizedException(
                    error_code=ErrorCode.USER_UNVERIFIED,
                    message=ErrorMessage(ErrorCode.USER_UNVERIFIED).value,
                )
            return True
        raise UnauthorizedException(
            error_code=ErrorCode.USER_EMAIL_NOT_FOUND,
            message=ErrorMessage(ErrorCode.USER_EMAIL_NOT_FOUND).value,
        )
    except Exception as e:
        if isinstance(e, UnauthorizedException):
            raise e

        raise BadRequestException(
            error_code=ErrorCode.BAD_REQUEST,
            message=ErrorMessage(ErrorCode.BAD_REQUEST).value,
        )
