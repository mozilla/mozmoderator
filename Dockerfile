FROM python:2.7.10-slim

WORKDIR /app

EXPOSE 8000
CMD ["./bin/run-docker.sh"]

# Avoid using root as default user
RUN adduser --uid 1000 --disabled-password --gecos '' --no-create-home dev

# Update and install required packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential python-dev libmysqlclient-dev

COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# Cleanup unused packages
RUN apt-get purge -y python-dev build-essential
RUN apt-get autoremove -y
RUN rm -rf /var/lib/{apt,dpkg,cache,log} /usr/share/doc /usr/share/man /tmp/*

# Change User
RUN chown dev.dev -R .
USER dev
