FROM python:3.11.7 AS base

ENV POETRY_VERSION=1.8.2 \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_HOME=/opt/poetry \
  PYSETUP_PATH=/opt/pysetup

RUN python -m venv $POETRY_HOME; \
  $POETRY_HOME/bin/pip install poetry==$POETRY_VERSION

WORKDIR $PYSETUP_PATH

COPY pyproject.toml poetry.lock ./

RUN $POETRY_HOME/bin/poetry install --no-root

FROM base AS dev

WORKDIR /app

ARG UID=10001
ARG GID=10001


COPY scripts/install_nodejs.sh /opt/
RUN apt-get update; \
  apt-get install -y \
  curl \
  gpg \
  mariadb-client \
  zip \
  zsh; \
  /opt/install_nodejs.sh; \
  npm install -g bower gulp-cli; \
  rm -rf /var/lib/apt/lists/*

ENV PORT=8000 \
  PATH=/opt/pysetup/.venv/bin:$PATH \
  VENV_PATH=/opt/pysetup/.venv

RUN groupadd -g $GID app; \
  useradd -d /app -g $GID -u $UID -M -s /usr/bin/zsh app; \
  chown -R app:app /app
USER app

COPY --chown=app:app . .

EXPOSE $PORT

CMD ["./bin/run-dev.sh"]

# Production image
FROM python:3.11.7-slim AS prod

ARG UID=10001
ARG GID=10001

RUN apt-get update; \
  apt-get install --no-install-recommends \
  mariadb-client; \
  rm -rf /var/lib/apt/lists/*

ENV PORT=8000 \
  PATH=/opt/pysetup/.venv/bin:$PATH \
  POETRY_HOME=/opt/poetry \
  VENV_PATH=/opt/pysetup/.venv

COPY --from=base $POETRY_HOME $POETRY_HOME
COPY --from=base $VENV_PATH $VENV_PATH
COPY pyproject.toml poetry.lock ./

RUN $POETRY_HOME/bin/poetry install --no-dev --no-root

RUN groupadd -g $GID app; \
  useradd -g $GID -u $UID -M -s /bin/bash app; \
  mkdir -p /app; \
  chown -R app:app /app

USER app
WORKDIR /app

COPY --chown=app:app . .

EXPOSE $PORT

CMD ["./bin/run-prod.sh"]
