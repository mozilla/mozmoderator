#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput
gunicorn moderator.wsgi:application -b 0.0.0.0:${PORT:-8000} --log-file -
