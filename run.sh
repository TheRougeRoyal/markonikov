#!/bin/bash

set -e

cd "$(dirname "$0")"

if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment .venv not found. Please install dependencies first."
    exit 1
fi

echo "Starting Markovify API server..."

open_browser() {
    sleep 2
    URL="http://localhost:8000"
    if command -v xdg-open > /dev/null; then
        xdg-open "$URL"
    elif command -v open > /dev/null; then
        open "$URL"
    else
        echo "Please open $URL in your browser."
    fi
}

open_browser &

python -m uvicorn api:app --host 127.0.0.1 --port 8000
