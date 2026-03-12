from fastapi import APIRouter, Depends

from app.api.api_v1.auth.password.router import router as password_router
from app.api.api_v1.auth.router import router as auth_router
from app.api.api_v1.locale.router import router as locale_router
from app.api.api_v1.user.router import router as user_router
from app.core.config import settings

# 条件付きインポート：招待機能が有効な場合のみ
if settings.ENABLE_USER_INVITATION:
    from app.api.api_v1.invite.router import router as invite_router

__all__ = [
    "api_v1_router",
]

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_v1_router.include_router(password_router, prefix="/auth", tags=["auth", "password"])
api_v1_router.include_router(locale_router, prefix="", tags=["locale"])
api_v1_router.include_router(user_router, prefix="/user", tags=["user"])

# 条件付きルーター登録：招待機能が有効な場合のみ
if settings.ENABLE_USER_INVITATION:
    api_v1_router.include_router(invite_router, prefix="/invite", tags=["invite"])
