from typing import Annotated

from fastapi import Depends
from fastapi.templating import Jinja2Templates
from inertia import Inertia, InertiaConfig, inertia_dependency_factory
from sqlalchemy.orm import Session

from app.core.config import settings as app_settings
from app.db.database import get_master_db
from app.enums.config import EnvEnum


def create_inertia_config() -> InertiaConfig:
    """
    Inertia.js設定を作成
    """
    templates = Jinja2Templates(directory="app/templates")

    return InertiaConfig(
        templates=templates,
        version="1.0.0",
        root_template_filename="inertia.html",
        environment="development"
        if app_settings.ENV == EnvEnum.LOCAL.value
        else "production",
        dev_url="http://localhost:5173",
        root_directory="src",
        entrypoint_filename="main.tsx",
        manifest_json_path="app/static/dist/.vite/manifest.json",
        extra_template_context={
            "environment": "development"
            if app_settings.ENV == EnvEnum.LOCAL.value
            else "production",
            "frontend_url": app_settings.FRONTEND_URL,
        },
    )


# Inertia設定とDI設定
inertia_config = create_inertia_config()
inertia_dependency = inertia_dependency_factory(inertia_config)

# 共通型エイリアス
InertiaDep = Annotated[Inertia, Depends(inertia_dependency)]
DbDep = Annotated[Session, Depends(get_master_db)]
