FROM python:2.7-slim

EXPOSE 8000
WORKDIR /app
CMD ["./bin/run-prod.sh"]

RUN adduser --uid 431 --disabled-password --disabled-login --gecos 'webdev' --no-create-home webdev

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libmysqlclient-dev mysql-client && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
RUN pip install --no-cache-dir --require-hashes --no-deps -r requirements/prod.txt

RUN chown webdev.webdev -R .
USER webdev
