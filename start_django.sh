#!/bin/bash

# Kill any existing process on port 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null; then
    kill $(lsof -t -i:8000)
fi

# Set environment variables and Python path
export PYTHONPATH="$(dirname "$0")"
export DJANGO_DEBUG=True

# Change to the Django app directory and start server
cd "$(dirname "$0")/src/django_app"
python manage.py runserver
