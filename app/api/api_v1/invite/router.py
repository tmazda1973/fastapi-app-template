"""
招待API
"""

from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends

from app.api.application.services.invite_service import InviteService
from app.api.di.auth_dependency import authenticate_admin_router
from app.api.di.invite_di import provide_invite_service
from app.core.config import settings
from app.core.errors.codes import ErrorCode
from app.core.exception import BadRequestException
from app.core.i18n.error_message import ErrorMessage
from app.core.response import public_api_responses
from app.models.user import User

from .schemas import (
    AcceptInviteRequest,
    AcceptInviteResponse,
    SendInviteRequest,
    SendInviteResponse,
    VerifyInviteResponse,
)

# 招待機能が無効な場合は空のルーターを返す
if not settings.ENABLE_USER_INVITATION:
    router = APIRouter()
else:
    router = APIRouter(responses=public_api_responses)

    @router.post(
        "/send",
        response_model=SendInviteResponse,
        summary="ユーザー招待API",
        description="新しいユーザーを招待します。管理者権限が必要です。",
        operation_id="invite_send",
    )
    async def send_invite(
        request_data: SendInviteRequest,
        background_tasks: BackgroundTasks,
        _current_user: User = Depends(authenticate_admin_router),
        invite_service: InviteService = Depends(provide_invite_service),
    ) -> SendInviteResponse:
        """
        ユーザー招待

        :param request_data: 招待リクエスト
        :param background_tasks: バックグラウンドタスク
        :param _current_user: 現在のユーザー（管理者）
        :param invite_service: 招待サービス
        :return: 招待レスポンス
        """
        try:
            token, expires_at = invite_service.send_invite(
                email=request_data.email,
                name=request_data.name,
                role=request_data.role,
                background_tasks=background_tasks,
            )

            expires_in_hours = int(
                (expires_at - datetime.now(timezone.utc)).total_seconds() / 3600
            )

            return SendInviteResponse(
                message=ErrorMessage(ErrorCode.INVITE_SEND_SUCCESS).value,
                invite_token=token,
                expires_at=expires_at,
                expires_in_hours=max(0, expires_in_hours),
            )
        except BadRequestException:
            raise
        except Exception as e:
            raise BadRequestException(
                error_code=ErrorCode.INVITE_SEND_FAILED,
                message=ErrorMessage(ErrorCode.INVITE_SEND_FAILED).value,
            ) from e

    @router.get(
        "/verify",
        response_model=VerifyInviteResponse,
        summary="招待トークン確認API",
        description="招待トークンの有効性を確認します。",
        operation_id="invite_verify",
    )
    async def verify_invite(
        token: str,
        invite_service: InviteService = Depends(provide_invite_service),
    ) -> VerifyInviteResponse:
        """
        招待トークン確認API

        :param token: 招待トークン
        :param invite_service: 招待サービス
        :return: レスポンスデータ
        """

        result = invite_service.verify_invite_token(token)
        return VerifyInviteResponse(**result)

    @router.post(
        "/accept",
        response_model=AcceptInviteResponse,
        summary="招待受諾API",
        description="招待を受諾してアカウントを有効化します。",
        operation_id="invite_accept",
    )
    async def accept_invite(
        request_data: AcceptInviteRequest,
        invite_service: InviteService = Depends(provide_invite_service),
    ) -> AcceptInviteResponse:
        """
        招待受諾API

        :param request_data: リクエストデータ
        :param invite_service: 招待サービス
        :return: レスポンスデータ
        """

        try:
            user = invite_service.accept_invite(
                token=request_data.token,
                password=request_data.password,
            )

            return AcceptInviteResponse(
                message=ErrorMessage(ErrorCode.INVITE_ACCEPT_SUCCESS).value,
                user_id=user.id,
                user_email=user.email,
                user_name=user.name,
            )

        except BadRequestException:
            raise
        except Exception as e:
            raise BadRequestException(
                error_code=ErrorCode.INVITE_ACCEPT_FAILED,
                message=ErrorMessage(ErrorCode.INVITE_ACCEPT_FAILED).value,
            ) from e
