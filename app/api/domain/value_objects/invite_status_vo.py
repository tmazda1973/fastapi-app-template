from __future__ import annotations

from dataclasses import dataclass

from app.enums.user import InviteStatusEnum, VerifyStatusEnum
from app.models import User
from app.utils.common_util import check_expired_token

__all__ = [
    "InviteStatusVo",
]


@dataclass(frozen=True)
class InviteStatusVo:
    """
    値オブジェクト（招待ステータス）

    :var user: ユーザーモデル
    """

    user: User

    @classmethod
    def create(
        cls,
        *,
        user: User,
    ) -> InviteStatusVo:
        """
        値オブジェクトを生成します。

        :param user: ユーザーモデル
        :return: 値オブジェクト
        """

        return cls(user=user)

    @property
    def value(self) -> InviteStatusEnum:
        """
        招待ステータスを取得します。

        :return: 招待ステータス
        """

        status = InviteStatusEnum.pending  # 招待ステータス
        if self.user is None:
            return status

        if self.user.verify_status == VerifyStatusEnum.unverified:
            # ユーザー未検証
            if check_expired_token(self.user.invite_token_expires):
                # 招待トークンの有効期限が切れている
                status = InviteStatusEnum.expired

        elif self.user.verify_status == VerifyStatusEnum.verified:
            # ユーザー検証済
            status = InviteStatusEnum.accepted

        return status
