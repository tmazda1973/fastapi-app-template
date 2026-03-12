from datetime import UTC, datetime


def now() -> datetime:
    """
    現在のUTC日時を取得します。

    :return: 現在のUTC日時
    """
    return datetime.now(UTC)
