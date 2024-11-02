#!/bin/bash
pip install gunicorn --break-system-packages
python3 manage.py migrate --no-input
python3 manage.py collectstatic --noinput
python3 manage.py crontab add
pwd
ls
gunicorn job.wsgi --bind 0.0.0.0:8000