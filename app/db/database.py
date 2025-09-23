from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
)
read_engine = create_engine(
    settings.SQLALCHEMY_READ_DATABASE_URL,
)

DbSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
ReadDbSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=read_engine,
)

__all__ = [
    "engine",
    "read_engine",
    "get_master_db",
    "get_read_db",
    "DbSession",
    "ReadDbSession",
]


def get_master_db():
    """
    ジェネレータ関数（通常セッション）
    """

    db = DbSession()
    try:
        yield db
        if db.in_transaction():
            db.commit()
    except Exception:
        # エラー時はロールバック
        if db.in_transaction():
            db.rollback()
        raise
    finally:
        db.close()


def get_read_db():
    """
    ジェネレータ関数（読み取り専用セッション）
    """

    db = ReadDbSession()
    try:
        yield db
    finally:
        db.close()
