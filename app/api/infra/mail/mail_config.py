from dataclasses import dataclass

from app.core.config import settings

__all__ = [
    "MailConfig",
]


@dataclass
class MailConfig:
    """
    メールコンフィグ

    メール送信に必要な設定を保持するクラスです。

    :var default_sender: デフォルトの送信者メールアドレス
    :var smtp_server: SMTPサーバーのアドレス
    :var smtp_port: SMTPサーバーのポート番号
    :var use_tls: TLSを使用するかどうか
    :var username: SMTPサーバーのユーザー名（オプション）
    :var password: SMTPサーバーのパスワード（オプション）
    :var from_name: 送信者名（オプション）
    """

    default_sender: str
    smtp_server: str
    smtp_port: int
    use_tls: bool = True
    username: str | None = None
    password: str | None = None
    from_name: str | None = None

    @classmethod
    def from_settings(cls) -> "MailConfig":
        """
        設定値からインスタンスを生成します。
        """
        return cls(
            default_sender=settings.MAIL_FROM,
            smtp_server=settings.MAIL_SERVER,
            smtp_port=settings.MAIL_PORT,
            use_tls=settings.ENV != "LOCAL",  # LOCAL環境以外ではTLSを使用
            username=settings.MAIL_USERNAME,
            password=settings.MAIL_PASSWORD,
            from_name=settings.MAIL_FROM_NAME,
        )
