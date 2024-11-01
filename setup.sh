#!/bin/bash
pip install gunicorn
python manage.py migrate --no-input
python manage.py collectstatic --noinput
pwd
ls
gunicorn job.wsgi --bind 0.0.0.0:8000