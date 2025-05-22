#!/bin/bash

# Kill any existing process on port 5000
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null; then
    kill $(lsof -t -i:5000)
fi

# Set environment variables and Python path
export PYTHONPATH="$(dirname "$0")"

# Change to the script directory and start Flask app
cd "$(dirname "$0")"
python src/meme_web_app.py
