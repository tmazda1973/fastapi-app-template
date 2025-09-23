"""
セッション管理サービス
"""

from app.models import User

__all__ = [
    "update_session_user_data",
]


def update_session_user_data(
    session: dict,
    user: User,
) -> None:
    """
    セッションのユーザーデータを更新します。

    :param session: セッションデータ
    :param user: ユーザー情報
    """

    if "user" in session:
        session["user"]["name"] = user.name
