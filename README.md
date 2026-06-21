# Markovify

A Markov chain text generation API with a modern web interface, built with Python and FastAPI.

## Overview

Markovify trains Markov chain models on text corpora and generates randomized sentences that mimic the style and vocabulary of the original text. The application provides both a REST API and a single-page web interface.

**Key capabilities:**
- Train models on any text with configurable state size
- Generate sentences with optional character limits
- Combine multiple models with weighted blending
- SQLite-backed persistence with integrity validation
- Docker-ready deployment

## Quick Start

### Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:8000` in your browser.

### Docker

```bash
docker compose up
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check with model integrity validation |
| `GET` | `/models` | List all saved models |
| `POST` | `/train` | Train a new model from text |
| `POST` | `/generate` | Generate sentences from a model |
| `POST` | `/combine` | Combine two models with weights |
| `DELETE` | `/models/{id}` | Delete a model |

### Example Usage

```bash
# Train a model
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{"text": "Your training text here...", "state_size": 2}'

# Generate sentences
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"model_id": "<model-id>", "count": 5}'

# Check health
curl http://localhost:8000/health
```

## CLI

```bash
# Train a model
python cli.py train --input data/sample.txt --state-size 2 --save my_model

# Generate sentences
python cli.py generate --model my_model --count 5

# Combine two models
python cli.py combine --models model_a model_b --weights 1.0 1.0 --save combined

# List all models
python cli.py list

# Delete a model
python cli.py delete --model my_model
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `MARKOVIFY_HOST` | `0.0.0.0` | Server host |
| `MARKOVIFY_PORT` | `8000` | Server port |
| `MARKOVIFY_DB_PATH` | `./markovify.db` | SQLite database path |
| `MARKOVIFY_API_KEY` | (empty) | API key for authentication |
| `MARKOVIFY_CORS_ORIGINS` | `http://localhost:8000` | Allowed CORS origins |
| `WEB_CONCURRENCY` | `2` | Gunicorn worker count |
| `LOG_LEVEL` | `info` | Logging level |

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Gunicorn
- **ML**: markovify (Markov chain text generation)
- **Database**: SQLite with WAL mode
- **Frontend**: Single-page HTML/CSS/JS
- **Infrastructure**: Docker, GitHub Actions CI

## Project Structure

```
.
├── api.py              # FastAPI application and routes
├── app.py              # Development server launcher
├── cli.py              # Command-line interface
├── database.py         # SQLite database layer
├── engine.py           # Core Markov chain logic
├── seed.py             # Sample model seeding
├── frontend/
│   └── index.html      # Web interface
├── data/
│   └── sample.txt      # Sample training corpus
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/
    └── ci.yml          # CI/CD pipeline
```

## License

MIT
