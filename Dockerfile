FROM python:3.9-buster as moderator-dev

EXPOSE 8000
WORKDIR /app
CMD ["./bin/run-dev.sh"]

RUN useradd -d /app -M --uid 1000 --shell /usr/bin/nologin webdev

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gnupg default-libmysqlclient-dev default-mysql-client curl && \
    curl -sL https://deb.nodesource.com/setup_12.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && rm -rf /var/lib/apt/lists/*

RUN npm install -g bower gulp-cli

COPY . /app
RUN pip install --no-cache-dir --require-hashes -r requirements/dev.txt

RUN chown webdev.webdev -R .
USER webdev

FROM python:3.9-slim-buster as moderator-prod

EXPOSE 8000


WORKDIR /app
CMD ["./bin/run-prod.sh"]

RUN useradd -d /app -M --uid 1000 --shell /usr/bin/nologin webdev

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gnupg default-libmysqlclient-dev default-mysql-client curl && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
RUN pip install --no-cache-dir --require-hashes --no-deps -r requirements/prod.txt

RUN chown webdev.webdev -R .
USER webdev
