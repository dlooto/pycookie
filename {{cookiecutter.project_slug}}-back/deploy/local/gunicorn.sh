#!/bin/bash
set -e
TIMEOUT=300   #to solve upload app package timeout issue

cd /home/deploy/{{cookiecutter.project_slug}}/prod/{{cookiecutter.project_slug}}-back/apps

# activate the virtualenv
# workon {{cookiecutter.project_slug}}
source /home/deploy/.virtualenvs/{{cookiecutter.project_slug}}/bin/activate

# changed:  --bind 0.0.0.0:8002 to --bind 127.0.0.1:8002, forbid 8002 port access
exec gunicorn wsgi -w 2 \
    --bind 127.0.0.1:8002 \
    --env DJANGO_SETTINGS_MODULE=settings.local \
    --user deploy --group deploy \
    --timeout $TIMEOUT \
    --log-level info
