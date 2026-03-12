import logging

from app.core.config import settings

__all__ = [
    "get_forget_password_content",
    "get_change_password_content",
]

logger = logging.getLogger(__name__)


def get_forget_password_content(
    username: str,
    email: str,
    token: str,
) -> str:
    """
    メール内容を生成します。（パスワード再設定）
    :param username: ユーザー名
    :param email: メールアドレス
    :param token: トークン
    :return: メール内容
    """

    callback_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    expire_minutes = settings.RESET_PASSWORD_EXPIRES_MINUTES  # 有効期限

    return f"""{username} 様
    <br><br>
    当ツールをご利用頂き、ありがとうございます。
    <br><br>
    パスワード再設定のご依頼を受け付けました。
    <br><br>
    メールアドレス：{email}
    <br><br>
    <a href="{callback_url}">パスワード再設定URL</a>
    <br><br>
    上記のURLにアクセスすると、パスワード再設定画面に移動します。
    <br>
    パスワードを再設定することで、引き続きご利用いただけます。
    <br><br>
    ※URLの有効期限は {_format_expire_minutes(expire_minutes)} になります。
    <br>
    それ以降のアクセスは無効となりますので、ご注意ください。
    """


def get_change_password_content(
    username: str,
    email: str,
    new_password: str,
) -> str:
    """
    メール内容を生成します。（パスワード変更）

    :param username: ユーザー名
    :param email: メールアドレス
    :param new_password: 新しいパスワード
    :return: メール内容
    """
    return f"""{username} 様
    <br><br>
    パスワードが変更されました。
    <br><br>
    ご利用中のメールアドレス：{email}
    <br>
    新しいパスワード：{new_password}
    <br><br>
    新しいパスワードで、引き続きご利用いただけます。
    """


def _format_expire_minutes(minutes: int | None) -> str:
    """
    有効期限の分数を適切なフォーマットに変換します。

    - 1440分（24時間）以上の場合は日数と残りの分に分割して表示
    - それ以下の場合は分のみ表示

    :param minutes: 分数
    :return: フォーマットされた文字列
    """

    if not isinstance(minutes, int):
        logger.error(f'有効期限は整数である必要があります。[有効期限: "{minutes}"]')
        return ""

    if minutes >= 60:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes > 0:
            return f"{hours}時間 {remaining_minutes}分"
        else:
            return f"{hours}時間"
    else:
        return f"{minutes}分"
