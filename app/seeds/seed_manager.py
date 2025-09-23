"""
シードデータ管理
"""

import argparse
import logging
import sys

from app.seeds.user_seed import seed_users

logger = logging.getLogger(__name__)

__all__ = [
    "run_all_seeds",
    "run_seed",
]


def run_all_seeds() -> None:
    """
    すべてのシードを実行
    """
    logger.info("すべてのシードデータの作成を開始します")
    logger.info("=" * 50)

    try:
        # ユーザーシード実行
        seed_users()
        logger.info("=" * 50)
        logger.info("すべてのシードデータの作成が完了しました")

    except Exception as e:
        logger.error(f"シードデータの作成中にエラーが発生しました: {e}")
        sys.exit(1)


def run_seed(seed_name: str) -> None:
    """
    指定されたシードを実行

    Args:
        seed_name: 実行するシード名 (user)
    """
    seed_map = {
        "user": seed_users,
    }

    if seed_name not in seed_map:
        logger.error(f"未知のシード名です: {seed_name}")
        logger.error(f"利用可能なシード: {', '.join(seed_map.keys())}")
        sys.exit(1)

    logger.info(f"{seed_name} シードの実行を開始します")
    logger.info("=" * 50)

    try:
        seed_map[seed_name]()
        logger.info("=" * 50)
        logger.info(f"{seed_name} シードの実行が完了しました")

    except Exception as e:
        logger.error(f"{seed_name} シードの実行中にエラーが発生しました: {e}")
        sys.exit(1)


def setup_logging():
    """
    ログ設定を初期化
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    """
    コマンドライン引数を処理してシードを実行
    """
    setup_logging()

    parser = argparse.ArgumentParser(description="シードデータ管理")
    parser.add_argument(
        "--seed",
        type=str,
        help="実行するシード名 (user) - 指定しない場合はすべて実行",
    )

    args = parser.parse_args()

    if args.seed:
        run_seed(args.seed)
    else:
        run_all_seeds()


if __name__ == "__main__":
    main()
