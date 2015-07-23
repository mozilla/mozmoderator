#!/bin/sh

./manage.py syncdb --noinput
./manage.py migrate --noinput
./manage.py collectstatic --noinput
./manage.py runserver 0.0.0.0:8000
