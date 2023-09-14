FROM python:3.11-bullseye as moderator-dev

EXPOSE 8000
WORKDIR /app
CMD ["./bin/run-dev.sh"]
ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    POETRY_VERSION=1.6 \
    PIP_VERSION=23.2.1

RUN useradd -d /app -M --uid 1000 --shell /usr/bin/zsh webdev

RUN set -xe \
    && apt-get update && apt-get install apt-transport-https \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential libmariadb3 mariadb-client optipng zip zsh \
    # python
    && python -m venv /venv \
    && pip install --upgrade pip==${PIP_VERSION} \
    && pip install --upgrade poetry==${POETRY_VERSION} \
    && poetry config virtualenvs.create false \
    # clean up
    && rm -rf /var/lib/apt/lists/*

COPY scripts/install_nodejs.sh ./install_nodejs.sh
RUN ./install_nodejs.sh && rm ./install_nodejs.sh

RUN npm install -g bower gulp-cli
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY . /app

RUN chown webdev.webdev -R .
USER webdev

FROM python:3.11-slim-bullseye as moderator-prod

EXPOSE 8000


WORKDIR /app
CMD ["./bin/run-prod.sh"]

RUN useradd -d /app -M --uid 1000 --shell /usr/bin/nologin webdev

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gnupg default-libmysqlclient-dev default-mysql-client curl && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends libmariadb3 mariadb-client && \
    # clean up
    rm -rf /var/lib/apt/lists/*

COPY . /app

RUN chown webdev.webdev -R .
USER webdev
