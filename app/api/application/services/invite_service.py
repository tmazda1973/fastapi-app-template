"""
招待関連サービス
"""

import secrets
import string
from datetime import datetime, timezone
from typing import TypedDict, Union

from fastapi import BackgroundTasks

from app.api.domain.services.user_domain_service import UserDomainService
from app.api.infra.adapters.datastore_adapter import DatastoreAdapter
from app.api.infra.mail.template_mail_sender import TemplateMailSender
from app.core.config import settings
from app.core.errors.codes import ErrorCode
from app.core.exception import BadRequestException
from app.core.i18n.error_message import ErrorMessage
from app.enums.user import RoleEnum, VerifyStatusEnum
from app.models.user import User
from app.utils.common_util import decode_jwt, hash_password

__all__ = [
    "InviteService",
    "InviteAcceptSuccessResult",
    "InviteAcceptFailureResult",
    "InviteAcceptResult",
]


class InviteAcceptSuccessResult(TypedDict):
    """
    招待受諾成功時の結果
    """

    success: bool  # True
    user_id: int
    user_email: str
    user_name: str
    message: str


class InviteAcceptFailureResult(TypedDict):
    """
    招待受諾失敗時の結果
    """

    success: bool  # False
    error_message: str


# 招待受諾結果の型（成功または失敗）
InviteAcceptResult = Union[InviteAcceptSuccessResult, InviteAcceptFailureResult]


class InviteService:
    """
    招待サービス
    """

    def __init__(
        self,
        user_domain_service: UserDomainService,
        datastore_adapter: DatastoreAdapter,
        template_mail_sender: TemplateMailSender,
    ):
        """
        コンストラクタ

        :param user_domain_service: ユーザードメインサービス
        :param datastore_adapter: データストアアダプター
        :param template_mail_sender: テンプレートメール送信サービス
        """
        self._user_domain_service = user_domain_service
        self._datastore_adapter = datastore_adapter
        self._template_mail_sender = template_mail_sender

    def send_invite(
        self,
        email: str,
        name: str,
        role: str | None,
        background_tasks: BackgroundTasks,
    ) -> tuple[str, datetime]:
        """
        招待メールを送信します。

        :param email: 招待するメールアドレス
        :param name: ユーザー名
        :param role: 権限（省略時はuser）
        :param background_tasks: バックグラウンドタスク
        :return: (招待トークン, 有効期限)
        :raises BadRequestException: 招待送信失敗時
        """

        try:
            # 既存ユーザーチェック
            existing_user = (
                self._datastore_adapter.query(User).filter(User.email == email).first()
            )
            if (
                existing_user
                and existing_user.verify_status == VerifyStatusEnum.verified
            ):
                raise BadRequestException(
                    error_code=ErrorCode.USER_EMAIL_EXISTS,
                    message=ErrorMessage(ErrorCode.USER_EMAIL_EXISTS).value,
                )

            # 招待可能かチェック
            if existing_user and not self._user_domain_service.is_invitable_user(email):
                raise BadRequestException(
                    error_code=ErrorCode.USER_CANNOT_BE_INVITED,
                    message=ErrorMessage(ErrorCode.USER_CANNOT_BE_INVITED).value,
                )

            # ユーザー作成または更新
            if existing_user:
                user = existing_user
                user.name = name
                if role:
                    user.role = RoleEnum(role)
            else:
                # 一時パスワード生成
                temp_password = self._generate_temp_password()

                user = User(
                    email=email,
                    name=name,
                    password=hash_password(temp_password),  # 一時的なパスワード
                    role=RoleEnum(role) if role else RoleEnum.user,
                    verify_status=VerifyStatusEnum.unverified,
                )

            # 招待トークン生成
            invite_token = self._user_domain_service.create_invite_token(user)
            user.invite_token = invite_token.value
            user.invite_expires = invite_token.expires_timestamp

            # データベース保存
            self._datastore_adapter.add(user)
            self._datastore_adapter.commit()

            # 招待メール送信
            invite_url = (
                f"{settings.FRONTEND_URL}/invite/accept?token={invite_token.value}"
            )
            self._template_mail_sender.send_invite_mail(
                to_email=email,
                user_name=name,
                invite_url=invite_url,
                expires_in_hours=invite_token.expires_in_hours,
                background_tasks=background_tasks,
            )

            return invite_token.value, invite_token.expires_at

        except BadRequestException:
            raise

        except Exception as e:
            self._datastore_adapter.rollback()
            raise BadRequestException(
                error_code=ErrorCode.INVITE_SEND_FAILED,
                message=ErrorMessage(ErrorCode.INVITE_SEND_FAILED).value,
            ) from e

    def verify_invite_token(self, token: str) -> dict:
        """
        招待トークンを検証します

        :param token: 招待トークン
        :return: 検証結果
        """
        try:
            # トークンデコード
            payload = decode_jwt(token)
            if not payload or payload.get("token_type") != "INVITE_TOKEN":
                return {
                    "is_valid": False,
                    "error_message": ErrorMessage(ErrorCode.INVITE_TOKEN_INVALID).value,
                }

            # ユーザー存在確認
            email = payload.get("sub")
            user = (
                self._datastore_adapter.query(User).filter(User.email == email).first()
            )
            if not user:
                return {
                    "is_valid": False,
                    "error_message": ErrorMessage(
                        ErrorCode.INVITE_USER_NOT_FOUND
                    ).value,
                }

            # トークン有効期限確認
            current_timestamp = int(datetime.now(timezone.utc).timestamp())
            if not user.invite_expires or current_timestamp > user.invite_expires:
                return {
                    "is_valid": False,
                    "error_message": ErrorMessage(ErrorCode.INVITE_TOKEN_EXPIRED).value,
                }

            # トークン一致確認
            if user.invite_token != token:
                return {
                    "is_valid": False,
                    "error_message": ErrorMessage(
                        ErrorCode.INVITE_TOKEN_MISMATCH
                    ).value,
                }

            # 既に認証済みかチェック
            if user.verify_status == VerifyStatusEnum.verified:
                return {
                    "is_valid": False,
                    "error_message": ErrorMessage(
                        ErrorCode.INVITE_USER_ALREADY_VERIFIED
                    ).value,
                }

            # 残り時間計算
            current_timestamp = int(datetime.now(timezone.utc).timestamp())
            remaining_minutes = max(
                0, int((user.invite_expires - current_timestamp) / 60)
            )

            return {
                "is_valid": True,
                "user_email": user.email,
                "user_name": user.name,
                "expires_at": datetime.fromtimestamp(user.invite_expires, timezone.utc),
                "expires_in_minutes": remaining_minutes,
            }

        except Exception:
            return {
                "is_valid": False,
                "error_message": ErrorMessage(
                    ErrorCode.INVITE_TOKEN_VERIFICATION_FAILED
                ).value,
            }

    def accept_invite(self, token: str, password: str) -> InviteAcceptResult:
        """
        招待を受諾します

        :param token: 招待トークン
        :param password: 設定するパスワード
        :return: 受諾結果
        """
        try:
            # トークン検証
            verification_result = self.verify_invite_token(token)
            if not verification_result["is_valid"]:
                raise BadRequestException(
                    error_code=ErrorCode.BAD_REQUEST,
                    message=verification_result["error_message"],
                )

            # ユーザー取得
            email = verification_result["user_email"]
            user = (
                self._datastore_adapter.query(User).filter(User.email == email).first()
            )
            if not user:
                raise BadRequestException(
                    error_code=ErrorCode.USER_NOT_FOUND,
                    message=ErrorMessage(ErrorCode.USER_NOT_FOUND).value,
                )

            # パスワード設定とアカウント有効化
            user.password = hash_password(password)
            user.verify_status = VerifyStatusEnum.verified
            user.invite_token = None
            user.invite_expires = None
            user.last_login_at = datetime.now(timezone.utc)

            self._datastore_adapter.add(user)
            self._datastore_adapter.commit()

            return {
                "success": True,
                "user_id": user.id,
                "user_email": user.email,
                "user_name": user.name,
                "message": "招待の受諾が完了しました。",
            }

        except BadRequestException as e:
            self._datastore_adapter.rollback()
            return {
                "success": False,
                "error_message": e.message,
            }
        except Exception:
            self._datastore_adapter.rollback()
            return {
                "success": False,
                "error_message": ErrorMessage(ErrorCode.INVITE_ACCEPT_FAILED).value,
            }

    def _generate_temp_password(self, length: int = 16) -> str:
        """
        一時パスワードを生成します

        :param length: パスワード長
        :return: 一時パスワード
        """
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(characters) for _ in range(length))
