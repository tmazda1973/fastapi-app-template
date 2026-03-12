from datetime import datetime, timezone

from accessify import private
from fastapi import Request, status
from sqlalchemy import select, update

from app.api.domain.protocols import TokenGeneratorProtocol
from app.api.domain.value_objects import InviteStatusVo, InviteTokenVo
from app.api.infra.adapters import DatastoreAdapter
from app.core.config import settings
from app.core.exception import BadRequestException, UnauthorizedException
from app.core.i18n.error_message import ErrorCode, ErrorMessage
from app.enums.user import InviteStatusEnum, RoleEnum, VerifyStatusEnum
from app.models import User
from app.utils.common_util import hash_password, verify_password

__all__ = [
    "UserDomainService",
]


class UserDomainService:
    """
    ドメインサービス（ユーザー関連）
    """

    INVITE_TOKEN_EXPIRE_MINUTES = 1440  # ドメインルール

    def __init__(
        self,
        token_generator: TokenGeneratorProtocol,
        datastore_adapter: DatastoreAdapter,
    ):
        """
        コンストラクタ

        :param token_generator: トークン生成モジュール
        :param datastore_adapter: データストアアダプター
        """
        self._token_generator = token_generator
        self._datastore_adapter = datastore_adapter

    def create_invite_token(self, user: User) -> InviteTokenVo:
        """
        ユーザー招待トークンを生成します。

        :param user: ユーザーモデル
        :return: 招待トークン
        """

        payload = self._build_invite_token_payload(user)
        token_value = self._token_generator.generate_jwt(
            payload,
            self.INVITE_TOKEN_EXPIRE_MINUTES,
        )

        return InviteTokenVo.create(
            token_value=token_value,
            expire_minutes=self.INVITE_TOKEN_EXPIRE_MINUTES,
        )

    def is_invitable_user(self, email: str) -> bool:
        """
        招待者ユーザーが招待可能であるかを判定します。

        :param email: 被招待者メールアドレス
        :return: True 招待可, False 招待不可
        """

        # 招待可能なユーザーの条件:
        # - 認証が完了していない
        user = (
            self._datastore_adapter.query(User)
            .filter(User.email == email)
            .filter(User.verify_status == VerifyStatusEnum.unverified)
            .first()
        )
        if not user:
            return False

        # 招待中であれば招待不可とする
        invite_status = InviteStatusVo.create(user=user).value
        inviting_statuses = [
            InviteStatusEnum.pending,
        ]
        if invite_status in inviting_statuses:
            return False

        return True

    def create_access_token(
        self,
        user: User,
        token_type: str,
        expire_minutes: int | None = None,
    ) -> str:
        """
        アクセストークンを生成します。

        :param user: ユーザー
        :param token_type: トークンタイプ
        :param expire_minutes: 有効期限（分）
        :return: 生成されたトークン
        """

        token_payload = {
            "sub": user.email,
            "role": user.role.value,
            "username": user.name,
            "token_type": token_type,
        }
        return self._token_generator.generate_jwt(token_payload, expire_minutes)

    def create_refresh_token(
        self,
        user: User,
        token_type: str,
        expire_minutes: int | None = None,
    ) -> str:
        """
        リフレッシュトークンを生成します。

        :param user: ユーザー
        :param token_type: トークンタイプ
        :param expire_minutes: 有効期限（分）
        :return: 生成されたトークン
        """

        token_payload = {
            "sub": user.email,
            "role": user.role.value,
            "username": user.name,
            "token_type": token_type,
        }
        return self._token_generator.generate_jwt(token_payload, expire_minutes)

    def verify_user(self, email: str, password: str) -> User | None:
        """
        ユーザーの認証を行います。

        - 認証に成功した場合、最終ログイン時刻を更新します。

        :param email: メールアドレス
        :param password: パスワード
        :return: ユーザー情報（認証失敗時はNone）
        """

        user = self._verify_user(email, password)
        if not user:
            return None

        # 最終ログイン時刻を更新する
        user.last_login_at = datetime.now(timezone.utc)
        self._datastore_adapter.add(user)
        self._datastore_adapter.commit()

        return user

    def get_user_by_email(self, email: str) -> User | None:
        """
        対象のメールアドレスのユーザーを取得します。

        :param email: メールアドレス
        :return: ユーザー（存在しない場合はNone）
        """

        return (
            self._datastore_adapter.query(User)
            .filter(User.email == email, User.deleted_at.is_(None))
            .first()
        )

    def get_current_user_from_session(self, request: Request) -> User:
        """
        ログインユーザー情報を取得します（Web認証用）

        :param request: リクエストデータ
        :return: ログインユーザー情報
        """

        user_data = request.session.get("user")
        if not user_data:
            raise UnauthorizedException(
                message="認証が必要です",
                error_code=status.HTTP_401_UNAUTHORIZED,
            )

        stmt = select(User).where(User.id == user_data["id"], User.deleted_at.is_(None))
        user = self._datastore_adapter.session.execute(stmt).scalar_one_or_none()
        if not user:
            raise UnauthorizedException(
                message="ユーザーが見つかりません",
                error_code=status.HTTP_401_UNAUTHORIZED,
            )

        return user

    def login(self, user: User, refresh_token: str) -> None:
        """
        ログイン処理を行います。

        :param user: ユーザー
        :param refresh_token: リフレッシュトークン
        """

        try:
            query = (
                update(User)
                .where(User.email == user.email)
                .values(refresh_token=refresh_token)
            )
            self._datastore_adapter.session.execute(query)
            self._datastore_adapter.commit()
        except Exception:
            self._datastore_adapter.rollback()
            raise

    def logout(self, user: User) -> None:
        """
        ログアウト処理を行います。

        :param user: ユーザー
        """

        try:
            query = (
                update(User).where(User.email == user.email).values(refresh_token=None)
            )
            self._datastore_adapter.session.execute(query)
            self._datastore_adapter.commit()
        except Exception:
            self._datastore_adapter.rollback()
            raise

    def update_profile_name(self, user: User, name: str) -> None:
        """
        プロフィール名を更新

        :param user: 更新対象のユーザー
        :param name: 新しい名前
        :raises BadRequestException: バリデーションエラー時
        """
        # 名前のバリデーション
        cleaned_name = name.strip()
        if not cleaned_name:
            raise BadRequestException(
                error_code=status.HTTP_400_BAD_REQUEST,
                message=ErrorMessage(ErrorCode.VALIDATION_ERROR).value,
            )

        # ユーザーの名前を更新
        user.name = cleaned_name

        try:
            self._datastore_adapter.add(user)
            self._datastore_adapter.commit()
        except Exception as e:
            self._datastore_adapter.rollback()
            raise BadRequestException(
                error_code=status.HTTP_400_BAD_REQUEST,
                message=ErrorMessage(ErrorCode.BAD_REQUEST).value,
            ) from e

    @private
    def _build_invite_token_payload(self, user: User) -> dict:
        """
        ユーザー招待トークンのペイロードを構築します。
        """
        return {
            "sub": user.email,
            "role": user.role.value,
            "username": user.name,
            "token_type": "INVITE_TOKEN",
        }

    def create_user(self, email: str, name: str, password: str) -> User:
        """
        ユーザーを作成します（招待機能OFF時用）

        :param email: メールアドレス
        :param name: 名前
        :param password: パスワード
        :return: 作成されたユーザー
        :raises BadRequestException: 作成失敗時
        """
        try:
            # 既存ユーザーチェック
            existing_user = (
                self._datastore_adapter.query(User).filter(User.email == email).first()
            )
            if existing_user:
                raise BadRequestException(
                    error_code=ErrorCode.USER_EMAIL_EXISTS,
                    message=ErrorMessage(ErrorCode.USER_EMAIL_EXISTS).value,
                )

            # ユーザー作成
            # 招待機能がOFFの場合は即座にverifiedにする
            verify_status = (
                VerifyStatusEnum.verified
                if not settings.ENABLE_USER_INVITATION
                else VerifyStatusEnum.unverified
            )

            user = User(
                email=email,
                name=name,
                password=hash_password(password),
                role=RoleEnum.user,
                verify_status=verify_status,
                last_login_at=datetime.now(timezone.utc),
            )

            self._datastore_adapter.add(user)
            self._datastore_adapter.commit()

            return user

        except BadRequestException:
            raise
        except Exception as e:
            self._datastore_adapter.rollback()
            raise BadRequestException(
                error_code=ErrorCode.USER_REGISTER_FAILED,
                message=ErrorMessage(ErrorCode.USER_REGISTER_FAILED).value,
            ) from e

    @private
    def _verify_user(self, email: str, password: str) -> User | None:
        """
        ユーザーの認証を行います。

        :param email: メールアドレス
        :param password: パスワード
        :return: ユーザー情報（認証失敗時はNone）
        """

        user = self.get_user_by_email(email)
        if not user:
            return None

        if not verify_password(password, user.password):
            return None

        return user
