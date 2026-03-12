from app.utils.common_util import encode_jwt

__all__ = [
    "JwtTokenGenerator",
]


class JwtTokenGenerator:
    """
    JWTトークン生成サービス
    """

    @classmethod
    def generate_jwt(
        cls,
        payload: dict,
        expire_minutes: int,
    ) -> str:
        """
        JWTトークンを生成します。

        :param payload: ペイロードデータ
        :param expire_minutes: 有効期限（分単位）
        :return: JWTトークン文字列
        """
        return encode_jwt(payload, expire_minutes)
