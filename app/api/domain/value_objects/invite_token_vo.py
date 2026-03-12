from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from app.utils import datetime_util

__all__ = [
    "InviteTokenVo",
]


@dataclass(frozen=True)
class InviteTokenVo:
    """
    値オブジェクト（招待トークン）

    :var value: 値
    :var expires_at: 有効期限
    """

    value: str
    expires_at: dt.datetime

    @classmethod
    def create(
        cls,
        *,
        token_value: str,
        expire_minutes: int,
    ) -> InviteTokenVo:
        """
        値オブジェクトを生成します。

        :param token_value: トークン文字列
        :param expire_minutes: 有効期限（分）
        :return: 値オブジェクト
        """

        expires_at = datetime_util.now() + dt.timedelta(minutes=expire_minutes)
        return cls(
            value=token_value,
            expires_at=expires_at,
        )

    def is_expired(self) -> bool:
        """
        トークンが期限切れであるかをチェックします。

        :return: True 期限切れ、False 有効
        """
        return datetime_util.now() > self.expires_at

    def to_timestamp(self) -> int:
        """
        タイムスタンプ形式で有効期限を取得します。

        :return: 有効期限のタイムスタンプ
        """
        return int(self.expires_at.timestamp())

    @property
    def expires_timestamp(self) -> int:
        """
        有効期限をUnixタイムスタンプで取得します。

        データベース保存やAPI応答に使用します。

        :return: 有効期限のUnixタイムスタンプ (例: 1751433240)
        """
        return int(self.expires_at.timestamp())

    @property
    def expires_in_minutes(self) -> int:
        """
        あと何分で期限切れになるかを取得します。

        :return: 残り時間（分）、既に期限切れの場合は0
        """
        if self.is_expired():
            return 0

        delta = self.expires_at - datetime_util.now()
        return max(0, int(delta.total_seconds() / 60))

    @property
    def expires_in_hours(self) -> int:
        """
        現在時刻から有効期限までの残り時間数を取得します。

        :return: 残り時間（時間）、既に期限切れの場合は0
        """
        return self.expires_in_minutes // 60
