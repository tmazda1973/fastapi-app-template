"""
シードデータ（ユーザー）
"""

import logging

from sqlalchemy.orm import Session

from app.db.database import DbSession
from app.enums.user import RoleEnum, VerifyStatusEnum
from app.models.user import User
from app.utils.common_util import get_password_hash

logger = logging.getLogger(__name__)

__all__ = [
    "create_test_users",
    "seed_users",
]


def create_test_users(db: Session) -> None:
    """
    テスト用のユーザーデータを作成します。

    :param db: DBセッション
    :return: None
    """

    # 既存のユーザーが存在する場合はスキップ
    existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
    if existing_admin:
        logger.warning("管理者ユーザーは既に存在します: admin@example.com")
    else:
        # 管理者ユーザー
        admin_user = User(
            name="管理者ユーザー",
            email="admin@example.com",
            password=get_password_hash("DevAdmin2024!"),
            role=RoleEnum.admin,
            verify_status=VerifyStatusEnum.verified,
        )
        db.add(admin_user)
        logger.info(
            "管理者ユーザーを作成しました: admin@example.com (パスワード: DevAdmin2024!)"
        )

    existing_user = db.query(User).filter(User.email == "user@example.com").first()
    if existing_user:
        logger.warning("一般ユーザーは既に存在します: user@example.com")
    else:
        # 一般ユーザー
        normal_user = User(
            name="一般ユーザー",
            email="user@example.com",
            password=get_password_hash("TestUser2024!"),
            role=RoleEnum.user,
            verify_status=VerifyStatusEnum.verified,
        )
        db.add(normal_user)
        logger.info(
            "一般ユーザーを作成しました: user@example.com (パスワード: TestUser2024!)"
        )

    # 追加のテストユーザー
    test_users = [
        {
            "name": "田中太郎",
            "email": "tanaka@example.com",
            "password": "tanaka123",
            "role": RoleEnum.user,
            "verify_status": VerifyStatusEnum.verified,
        },
        {
            "name": "佐藤花子",
            "email": "sato@example.com",
            "password": "sato123",
            "role": RoleEnum.user,
            "verify_status": VerifyStatusEnum.verified,
        },
        {
            "name": "鈴木次郎",
            "email": "suzuki@example.com",
            "password": "suzuki123",
            "role": RoleEnum.user,
            "verify_status": VerifyStatusEnum.unverified,  # 未認証ユーザー
        },
        {
            "name": "システム管理者",
            "email": "system@example.com",
            "password": "system123",
            "role": RoleEnum.admin,
            "verify_status": VerifyStatusEnum.verified,
        },
    ]

    for user_data in test_users:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if existing:
            logger.warning(f"ユーザーは既に存在します: {user_data['email']}")
        else:
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                verify_status=user_data["verify_status"],
            )
            db.add(user)
            logger.info(
                f"テストユーザーを作成しました: {user_data['email']} (パスワード: {user_data['password']})"
            )

    # データベースにコミット
    db.commit()
    logger.info("ユーザーシードデータの作成が完了しました")


def seed_users() -> None:
    """
    ユーザーシードを実行するメイン関数
    """
    logger.info("ユーザーシードデータの作成を開始します")

    # データベースセッションを取得
    db = DbSession()
    try:
        create_test_users(db)
    except Exception as e:
        logger.error(f"シードデータの作成中にエラーが発生しました: {e}")
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
    seed_users()
