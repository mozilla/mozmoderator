#!/bin/sh

python manage.py migrate
gunicorn moderator.wsgi:application -b 0.0.0.0:${PORT:-8000} --log-file -
