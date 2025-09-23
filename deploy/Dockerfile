
FROM python:3.11-slim AS python-base

# python
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=2.1.3 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/workspace" \
    VENV_PATH="/workspace/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base AS poetry-base
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    # deps for installing poetry
    curl \
    git

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python

# `builder-base` stage is used to build deps + create our virtual environment
FROM poetry-base AS builder-base
RUN apt-get update && \
    apt-get install --no-install-recommends -y  \
    # deps for building python deps
    build-essential \
    libpq-dev \
    pkg-config \
    git

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./README.md ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --only main

# `development` image is used during development / testing
FROM python-base AS development

# copy in our built poetry + venv
COPY --from=poetry-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $VENV_PATH $VENV_PATH

RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq-dev sudo curl && \
    # Node.js 18.x をインストール
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    # ユーザー作成
    useradd -m -d /home/app -s /bin/bash app && \
    echo '%app ALL=(ALL) NOPASSWD:ALL' >>/etc/sudoers

# will become mountpoint of our code
WORKDIR /workspace

COPY . .

# フロントエンドの依存関係をインストール
WORKDIR /workspace/frontend-inertia

# Use npm ci for exact versions, fallback to install with updates
RUN npm ci --production=false 2>/dev/null || \
    (echo "Lock file outdated, updating..." && rm -f package-lock.json && npm install)

# エントリーポイントスクリプトをコピー
WORKDIR /workspace
COPY ./deploy/entrypoint.sh /workspace/entrypoint.sh
RUN chmod +x /workspace/entrypoint.sh

RUN chown -R app:app /workspace
USER app

# 環境変数でモード切り替え（デフォルトはproduction）
ENV APP_ENV=production

EXPOSE 8000 5173

# 統一エントリーポイント（開発・プロダクション両対応）
CMD ["/workspace/entrypoint.sh"]
