# pull official base image
FROM continuumio/miniconda3

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# 環境のパスを追加
ENV PATH /opt/conda/envs/myenv/bin:$PATH
# シェルの初期化時に環境を有効化
RUN echo "source activate myenv" > ~/.bashrc

# install apt dependencies including Node.js
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    python3-dev \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# create conda environment
RUN conda create -n myenv python=3.11 \
    && conda install -n myenv -c conda-forge rdkit \
    && conda clean -afy

# copy poetry files
COPY ./pyproject.toml ./poetry.lock* /usr/src/app/

# copy .env.example to .env if .env does not exist
COPY ./.env.example /usr/src/app/
RUN if [ ! -f  /usr/src/app/.env ]; then cp  /usr/src/app/.env.example  /usr/src/app/.env; fi

# install Python dependencies
RUN /bin/bash -c "source activate myenv && \
    pip install --upgrade pip setuptools wheel && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi && \
    alembic --version"

# copy frontend-inertia files
COPY ./frontend-inertia/package.json ./frontend-inertia/package-lock.json* /usr/src/app/frontend-inertia/
WORKDIR /usr/src/app/frontend-inertia

# Use npm ci for exact versions, fallback to install with updates
RUN npm ci --production=false 2>/dev/null || \
    (echo "Lock file outdated, updating..." && rm -f package-lock.json && npm install)

# copy the rest of frontend files
COPY ./frontend-inertia /usr/src/app/frontend-inertia/

# go back to main workdir
WORKDIR /usr/src/app

# copy unified entrypoint script
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# 環境変数でモード切り替え（デフォルトはproduction）
ENV APP_ENV=production

#統一エントリーポイント（開発・プロダクション両対応）
CMD ["/usr/src/app/entrypoint.sh"]
