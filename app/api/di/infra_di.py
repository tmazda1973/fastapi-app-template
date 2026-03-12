"""
インフラストラクチャサービスの依存性注入設定
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.infra.adapters.datastore_adapter import DatastoreAdapter
from app.db.database import get_master_db

__all__ = [
    "provide_datastore_adapter",
]


def provide_datastore_adapter(
    db: Session = Depends(get_master_db),
) -> DatastoreAdapter:
    """
    データストアアダプター
    """
    return DatastoreAdapter(db_session=db)
