"""
Inertia.jsページルーター

機能別に分割されたページルーターを統合します。
"""

from fastapi import APIRouter

from .pages.auth_pages import router as auth_router
from .pages.common_pages import router as common_router
from .pages.invite_pages import router as invite_router
from .pages.password_pages import router as password_router
from .pages.user_pages import router as user_router

# メインルーターを作成
router = APIRouter()

# 各機能のルーターを統合
router.include_router(common_router, tags=["Common"])
router.include_router(auth_router, tags=["Authentication"])
router.include_router(user_router, tags=["User"])
router.include_router(invite_router, tags=["Invite"])
router.include_router(password_router, tags=["Password"])
