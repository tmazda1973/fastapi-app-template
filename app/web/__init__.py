from fastapi import APIRouter

from .inertia_pages import router as inertia_pages_router

web_router = APIRouter()

# Inertia.jsベースのルーター（認証機能含む）
web_router.include_router(inertia_pages_router, tags=["inertia-pages"])
