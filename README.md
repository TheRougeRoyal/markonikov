# Markovify App

A lightweight, single-page application and command-line interface for training, combining, and generating text using Markov chains, built with Python, FastAPI, and `markovify`.

## Features

- **Training**: Train Markov chain models on raw paragraph corpora or newline-separated sentence corpora with custom `state_size` constraints.
- **Generation**: Generate randomized sentences from saved models, with options to limit sentence count and maximum character length.
- **Combining**: Combine two trained models using custom weights to merge their styles and vocabularies.
- **Management**: Inspect and delete saved models through the UI or the API.
- **CLI Utilities**: Perform training, generation, and combination from the console.

## Folder Structure

- `frontend/`: Single-page HTML/CSS/JS application.
- `models/`: Trained model files in JSON format, along with metadata sidecar `.meta.json` files.
- `data/`: Sample input text corpora.
- `engine.py`: Core logic for compiling, saving, and generating sentences.
- `api.py`: FastAPI backend implementing the RESTful web endpoints and serving the static frontend.
- `cli.py`: Command-line interface.

## Installation

### Prerequisites

- Python 3.8 or higher.
- `git` (optional, for cloning).

### Steps

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd markovify-app
   ```

2. **Set up the virtual environment & install dependencies**:
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     ```
   - **Windows**:
     ```cmd
     python -m venv .venv
     call .venv\Scripts\activate
     pip install -r requirements.txt
     ```

## How to Start the Application

### Option 1: Using the provided startup script (recommended)

This launches both the server and opens the frontend in your default browser.

- **Linux / macOS**:
  ```bash
  ./run.sh
  ```
- **Windows**:
  ```cmd
  run.bat
  ```

### Option 2: Manual startup with Uvicorn

If you prefer to start the server manually:

```bash
# Ensure virtual environment is activated
source .venv/bin/activate   # Linux/macOS
# or .venv\Scripts\activate  # Windows

# Start the server
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

Then open your web browser and visit: **http://localhost:8000**

## Usage

### Web Interface

Once the server is running, navigate to `http://localhost:8000` in your browser. The interface includes tabs for:

1. **Train** – Upload or paste text to train a new model.
2. **Generate** – Select a model and generate sentences.
3. **Combine** – Combine two models with adjustable weights.
4. **Models** – View, inspect, and delete saved models.

### Command-Line Interface

You can also interact directly with the engine via `cli.py`:

#### 1. Train a model
```bash
python cli.py train --input data/sample.txt --state-size 2 --save my_model
```

#### 2. Generate sentences
```bash
python cli.py generate --model my_model --count 5 --max-chars 280
```

#### 3. Combine two models
```bash
python cli.py combine --models model_a model_b --weights 1.5 0.8 --save combined_model
```

#### 4. List models
```bash
python cli.py list
```

#### 5. Delete a model
```bash
python cli.py delete --model my_model
```

## API Endpoints Reference

| Method | Endpoint | Description | Request Body Example | Response Example |
|---|---|---|---|---|
| **GET** | `/health` | Server health check and model count | None | `{"status": "ok", "models_count": 5}` |
| **GET** | `/models` | List all saved models with metadata | None | `{"models": [{"model_id": "...", "state_size": 2, ...}]}` |
| **POST** | `/train` | Train a new model from text | `{"text": "...", "state_size": 2, "sentence_split": false}` | `{"model_id": "...", "state_size": 2, ...}` |
| **POST** | `/generate` | Generate sentences from a model | `{"model_id": "...", "count": 5, "max_chars": 280}` | `{"sentences": ["First sentence.", ...]}` |
| **POST** | `/combine` | Combine two models with weights | `{"model_ids": ["id_a", "id_b"], "weights": [1.5, 0.5], "save_as": "name"}` | `{"model_id": "combined_uuid"}` |
| **DELETE** | `/models/{id}` | Permanently delete a model | None | `{"deleted": "model_uuid"}` |

## Troubleshooting

- **Port already in use?** Change the port in the `run.sh`/`.bat` file or when starting uvicorn manually (e.g., `--port 8001`).
- **Virtual environment not activated?** Ensure you run `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows) before installing packages or running commands.
- **Missing dependencies?** Double-check that you ran `pip install -r requirements.txt` inside the activated virtual environment.

## Notes

- The frontend is served statically by the FastAPI application; no separate frontend server is needed.
- Model files are stored in the `models/` directory as JSON, with metadata sidecars.
- Sample training data can be found in the `data/` directory.

Enjoy generating text with Markov chains!