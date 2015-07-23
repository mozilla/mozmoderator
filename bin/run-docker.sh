#!/bin/sh

./manage.py syncdb --noinput
./manage.py migrate --noinput
./manage.py collectstatic --noinput
gunicorn moderator.wsgi:application -b 0.0.0.0:8000 -w 2 --log-file -
