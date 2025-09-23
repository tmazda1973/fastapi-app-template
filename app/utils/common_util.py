from datetime import datetime, timedelta, timezone
from typing import Union

from jose import jwt
from passlib.context import CryptContext
from zoneinfo import ZoneInfo

from app.constants.regex_constant import (
    FULL_WIDTH_ALPHANUM_SYMBOL_CHARS,
    HALF_WIDTH_ALPHANUM_SYMBOL_CHARS,
)
from app.core.config import settings
from app.utils import datetime_util

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def check_expired_token(expired: int) -> bool:
    """
    トークンの有効期限をチェックします。

    :param expired: 有効期限（秒）
    :return: 有効期限が切れているかどうか
    """

    return datetime_util.now().timestamp() > expired if type(expired) is int else True


def generate_expires_delta(minutes: int) -> datetime:
    """
    有効期限を生成します。

    :param minutes: 有効期限（分）
    :return: 有効期限
    """

    return datetime_util.now() + timedelta(minutes=minutes)


def encode_jwt(payload: dict, expired: int = None) -> str:
    """
    JWTをエンコードします。

    :param payload: エンコードするペイロード
    :param expired: 有効期限（分）
    :return: エンコードされたJWT
    """

    to_encode = payload.copy()
    expire = generate_expires_delta(expired or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_jwt(token: str) -> dict | None:
    """
    JWTをデコードします。

    :param token: デコードするJWT
    :return: デコード結果
    """

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except Exception:
        return None


def verify_jwt(token: str, token_type: str) -> Union[dict, None]:
    """
    JWTを検証します。

    :param token: 検証するJWT
    :param token_type: JWTのタイプ
    :return: 検証結果
    """

    payload = decode_jwt(token)
    if (
        not payload
        or not payload.get("sub")
        or payload.get("token_type") != token_type
        or check_expired_token(payload.get("exp", 0))
    ):
        return None

    return payload


def get_password_hash(password: str):
    """
    パスワードをハッシュ化します。

    :param password: パスワード
    :return: ハッシュ化されたパスワード
    """
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """
    パスワードを検証します。

    :param plain_password: 平文パスワード
    :param hashed_password: ハッシュ化されたパスワード
    :return: 検証結果
    """
    return pwd_context.verify(plain_password, hashed_password)


# エイリアス：一貫性のため
hash_password = get_password_hash


def datetime_to_gmt_str(dt: datetime) -> str:
    """
    日時をGMT形式の文字列に変換します。

    :param dt: 変換する日時
    :return: 変換後の文字列
    """

    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def datetime_to_jst_str(dt: datetime) -> str:
    """
    日時をJST形式の文字列に変換します。

    :param dt: 変換する日時
    :return: 変換後の文字列
    """

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    jst_dt = dt.astimezone(timezone(timedelta(hours=9)))
    return jst_dt.strftime("%Y-%m-%d %H:%M:%S")


def escape_like_string(value: str) -> str:
    """
    文字列をLIKE検索用にエスケープします。

    :param value: エスケープする文字列
    :return: エスケープ後の文字列
    """

    return value.replace("%", "\\%").replace("_", "\\_")


def halfwidth_converter(text: str | None) -> str | None:
    """
    全角英数記号を半角英数記号に変換します。

    :param text: 変換する文字列
    :return: 変換後の文字列
    """

    FULL_WIDTH = {
        "BASE": 0xFEE0,
        "LOWER": 0xFF01,
        "UPPER": 0xFF5E,
        "SPACE": 0x3000,
    }
    HALF_WIDTH = {"SPACE": 0x0020}
    ALLOWED_CHARS = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]"
    )
    if not text:
        return None

    result = []
    for char in text:
        code = ord(char)
        if (
            FULL_WIDTH["LOWER"] <= code <= FULL_WIDTH["UPPER"]
            and chr(code - FULL_WIDTH["BASE"]) in ALLOWED_CHARS
        ):
            result.append(chr(code - FULL_WIDTH["BASE"]))
        elif code == FULL_WIDTH["SPACE"]:
            result.append(chr(HALF_WIDTH["SPACE"]))
        else:
            result.append(char)
    return "".join(result)


def normalize_to_half_width(text) -> str:
    """
    全角英数記号を半角英数記号に変換します。

    :param text: 変換する文字列
    :return: 変換後の文字列
    """

    result = ""
    for char in text:
        idx = FULL_WIDTH_ALPHANUM_SYMBOL_CHARS.find(char)
        if idx >= 0:
            result += HALF_WIDTH_ALPHANUM_SYMBOL_CHARS[idx]
        else:
            result += char

    return result
