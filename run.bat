@echo off
setlocal enabledelayedexpansion

:: Get script directory
cd /d "%~dp0"

:: Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment .venv not found. Please install dependencies first.
    exit /b 1
)

echo Starting Markovify API server...

:: Start browser after a short delay
start "" http://localhost:8000

:: Run uvicorn server
python -m uvicorn api:app --host 127.0.0.1 --port 8000