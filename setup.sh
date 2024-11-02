#!/bin/bash
pip install gunicorn --break-system-packages
python manage.py migrate --no-input
python manage.py collectstatic --noinput
python manage.py crontab add
pwd
ls
gunicorn job.wsgi --bind 0.0.0.0:8000