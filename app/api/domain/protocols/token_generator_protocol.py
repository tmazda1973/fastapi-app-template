from typing import Protocol

__all__ = [
    "TokenGeneratorProtocol",
]


class TokenGeneratorProtocol(Protocol):
    """ "
    プロトコル（トークン生成）
    """

    def generate_jwt(self, payload: dict, expire_minutes: int) -> str:
        """
        JWTトークンを生成します。

        :param payload: ペイロードデータ
        :param expire_minutes: 有効期限（分単位）
        :return: JWTトークン文字列
        """
        ...
