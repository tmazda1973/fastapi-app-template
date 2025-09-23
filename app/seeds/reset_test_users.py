"""
テストユーザーを削除して再作成するスクリプト
"""

import logging

from app.db.database import DbSession
from app.models.user import User
from app.seeds.user_seed import create_test_users

logger = logging.getLogger(__name__)


def reset_test_users() -> None:
    """
    テストユーザーを削除して再作成
    """
    logger.info("テストユーザーのリセットを開始します")

    db = DbSession()
    try:
        # 既存のテストユーザーを削除
        test_emails = [
            "admin@example.com",
            "user@example.com",
            "tanaka@example.com",
            "sato@example.com",
            "suzuki@example.com",
            "system@example.com",
        ]

        for email in test_emails:
            user = db.query(User).filter(User.email == email).first()
            if user:
                db.delete(user)
                logger.info(f"既存ユーザーを削除しました: {email}")

        db.commit()
        logger.info("既存テストユーザーの削除が完了しました")

        # 新しいテストユーザーを作成
        create_test_users(db)
        logger.info("新しいテストユーザーの作成が完了しました")

    except Exception as e:
        logger.error(f"リセット中にエラーが発生しました: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def setup_logging():
    """
    ログ設定を初期化
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


if __name__ == "__main__":
    setup_logging()
    reset_test_users()
