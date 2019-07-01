#! /bin/bash
git pull origin master
source venv/bin/activate
pip install -r requirements.txt
uwsgi --stop uwsgi/uwsgi.pid
uwsgi --ini mp_uwsgi.ini
