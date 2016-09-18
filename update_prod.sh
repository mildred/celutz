#!/bin/bash

set -e

# Check if running in a virtualenv
[ -z "$VIRTUAL_ENV" ] && { echo 'Please run this script in a virtualenv!'; exit 1;}

git pull
pip install -r requirements.txt
./manage.py collectstatic

echo
echo
echo "** Update done.  Don't forget to restart gunicorn (e.g. using 'supervisorctl')"
