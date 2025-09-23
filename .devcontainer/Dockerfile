FROM python:3.11-slim as python-base

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

FROM python-base as poetry-base
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    # deps for installing poetry
    curl && \
    # clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

# `builder-base` stage is used to build deps + create our virtual environment
FROM poetry-base as builder-base
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    # deps for building python deps
    build-essential \
    libpq-dev && \
    # clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml README.md ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --with dev

# `development` image is used during development / testing
FROM python-base as development

# copy in our built poetry + venv
COPY --from=poetry-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $VENV_PATH $VENV_PATH

# Install system dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    libpq-dev \
    build-essential \
    git \
    bash \
    curl \
    tar \
    sudo \
    default-jre \
    nodejs \
    npm \
    ca-certificates && \
    # Create non-root user with sudo privileges
    useradd -m -d /home/app -s /bin/bash app && \
    echo '%app ALL=(ALL) NOPASSWD:ALL' >>/etc/sudoers && \
    # Install starship prompt
    curl -sS https://starship.rs/install.sh | sh -s -- --yes && \
    echo 'eval "$(starship init bash)"' >>/home/app/.bashrc && \
    # Clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add git configuration to user
RUN echo '[safe]\n    directory = /workspace' > /home/app/.gitconfig

# Switch to non-root user
USER app

# will become mountpoint of our code
WORKDIR /workspace

# We don't need to copy files here as they will be mounted in dev container
# COPY . .

# Create .venv directory with proper permissions if it doesn't exist
RUN mkdir -p $VENV_PATH && chmod 755 $VENV_PATH

# Pre-create frontend-inertia directory and set permissions
# (for when files are mounted)
RUN mkdir -p /workspace/frontend-inertia && \
    chown -R app:app /workspace

EXPOSE 8000 5173

# Set helpful aliases for the developer
RUN echo 'alias ll="ls -la"' >> /home/app/.bashrc && \
    echo 'alias python="python3"' >> /home/app/.bashrc && \
    echo 'alias vite="cd /workspace/frontend-inertia && npm run dev"' >> /home/app/.bashrc && \
    echo 'alias build="cd /workspace/frontend-inertia && npm run build"' >> /home/app/.bashrc
