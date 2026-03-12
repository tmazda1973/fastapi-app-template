import secrets
import string
from datetime import datetime, timezone
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.errors.codes import ErrorCode
from app.core.exception import BadRequestException
from app.core.i18n.error_message import ErrorMessage
from app.models.password_reset import PasswordResetToken
from app.models.user import User

__all__ = [
    "PasswordService",
]


class PasswordService:
    """
    パスワード関連サービス
    """

    def __init__(self):
        """
        コンストラクタ
        """
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        """
        パスワードを検証します。

        :param plain_password: プレーンテキストパスワード
        :param hashed_password: ハッシュ化パスワード
        :return: 検証結果
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        """
        パスワードをハッシュ化します。

        :param password: プレーンテキストパスワード
        :return: ハッシュ化パスワード
        """
        return self.pwd_context.hash(password)

    def generate_reset_code(self, length: int = 6) -> str:
        """
        リセットコードを生成します。

        :param length: コードの長さ
        :return: リセットコード
        """

        characters = string.digits + string.ascii_uppercase
        return "".join(secrets.choice(characters) for _ in range(length))

    def generate_reset_token(self, length: int = 32) -> str:
        """
        リセットトークンを生成します。

        :param length: トークンの長さ
        :return: リセットトークン
        """
        return secrets.token_urlsafe(length)

    def change_password(
        self,
        db: Session,
        user: User,
        current_password: str,
        new_password: str,
    ) -> User:
        """
        パスワードを変更します。

        :param db: DBセッション
        :param user: ユーザー
        :param current_password: 現在のパスワード
        :param new_password: 新しいパスワード
        :return: 更新されたユーザー
        """

        # 現在のパスワード確認
        if not self.verify_password(current_password, user.password):
            raise BadRequestException(
                error_code=ErrorCode.BAD_REQUEST,
                message="現在のパスワードが正しくありません",
            )

        # 新しいパスワードと現在のパスワードが同じでないか確認
        if self.verify_password(new_password, user.password):
            raise BadRequestException(
                error_code=ErrorCode.BAD_REQUEST,
                message="新しいパスワードは現在のパスワードと異なる必要があります",
            )

        # パスワード更新
        user.password = self.hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    def create_password_reset_token(
        self,
        db: Session,
        user: User,
        expires_in_minutes: int = 30,
    ) -> PasswordResetToken:
        """
        パスワードリセットトークンを作成します。

        :param db: DBセッション
        :param user: ユーザー
        :param expires_in_minutes: 有効期限（分）
        :return: パスワードリセットトークン
        """
        # 既存の有効なトークンを無効化
        existing_tokens = (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.user_id == user.id,
                not PasswordResetToken.is_used,
                PasswordResetToken.expires_at > datetime.now(timezone.utc),
            )
            .all()
        )

        for token in existing_tokens:
            token.mark_as_used()

        # 新しいトークンを生成する
        reset_token = self.generate_reset_token()
        reset_code = self.generate_reset_code()

        password_reset_token = PasswordResetToken.create_token(
            user_id=user.id,
            token=reset_token,
            reset_code=reset_code,
            expires_in_minutes=expires_in_minutes,
        )

        db.add(password_reset_token)
        db.commit()
        db.refresh(password_reset_token)

        return password_reset_token

    def get_user_by_email(
        self,
        db: Session,
        email: str,
    ) -> Optional[User]:
        """
        メールアドレスでユーザーを取得します。

        :param db: DBセッション
        :param email: メールアドレス
        :return: ユーザー（存在しない場合はNone）
        """
        return (
            db.query(User)
            .filter(User.email == email, User.deleted_at.is_(None))
            .first()
        )

    def validate_reset_token(
        self,
        db: Session,
        email: str,
        reset_code: str,
        locale: str = "ja",
    ) -> PasswordResetToken:
        """
        リセットトークンを検証します。

        :param db: DBセッション
        :param email: メールアドレス
        :param reset_code: リセットコード
        :return: パスワードリセットトークン
        """
        user = self.get_user_by_email(db, email)
        if not user:
            raise BadRequestException(
                error_code=ErrorCode.BAD_REQUEST,
                message=ErrorMessage(ErrorCode.BAD_REQUEST, locale).value,
            )

        reset_token = (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.reset_code == reset_code,
                not PasswordResetToken.is_used,
            )
            .first()
        )

        if not reset_token:
            raise BadRequestException(
                error_code=ErrorCode.BAD_REQUEST,
                message="無効なリセットコードです",
            )

        if reset_token.is_expired():
            raise BadRequestException(
                error_code=ErrorCode.BAD_REQUEST,
                message="リセットコードの有効期限が切れています",
            )

        return reset_token

    def reset_password(
        self,
        db: Session,
        email: str,
        reset_code: str,
        new_password: str,
    ) -> User:
        """
        パスワードをリセットします。

        :param db: DBセッション
        :param email: メールアドレス
        :param reset_code: リセットコード
        :param new_password: 新しいパスワード
        :return: 更新されたユーザー
        """

        # トークンを検証する
        reset_token = self.validate_reset_token(db, email, reset_code)
        user = reset_token.user

        # 新しいパスワードが現在のパスワードと同じでないか確認
        if self.verify_password(new_password, user.password):
            raise BadRequestException(
                error_code=ErrorCode.BAD_REQUEST,
                message="新しいパスワードは現在のパスワードと異なる必要があります",
            )

        # パスワード更新
        user.password = self.hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)

        # トークンを使用済みにマーク
        reset_token.mark_as_used()

        db.add(user)
        db.add(reset_token)
        db.commit()
        db.refresh(user)

        return user
