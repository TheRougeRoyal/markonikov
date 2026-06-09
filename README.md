# Markovify App

A lightweight, single-page application and command-line interface for training, combining, and generating text using Markov chains, built with Python, FastAPI, and `markovify`.

The project includes a web UI styled with a retro terminal theme that connects directly to a FastAPI backend.

---

## Features

- **Training**: Train Markov chain models on raw paragraph corpora or newline-separated sentence corpora with custom `state_size` constraints.
- **Generation**: Generate randomized sentences from saved models, with options to limit sentence count and maximum character length.
- **Combining**: Combine two trained models using custom weights to merge their styles and vocabularies.
- **Management**: Inspect and delete saved models through the UI or the API.
- **CLI Utilities**: Perform training, generation, and combination from the console.

---

## Folder Structure

- `frontend/`: Single-page HTML/CSS/JS application.
- `models/`: Trained model files in JSON format, along with metadata sidecar `.meta.json` files.
- `data/`: Sample input text corpora.
- `engine.py`: Core logic for compiling, saving, and generating sentences.
- `api.py`: FastAPI backend implementing the RESTful web endpoints and serving the static frontend.
- `cli.py`: Command-line interface.

---

## Installation

### Prerequisites
- Python 3.8 or higher.
- `git` (optional, for cloning).

### Steps
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd markovify-app
   ```

2. **Set up the virtual environment & install dependencies**:
   On macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
   On Windows:
   ```cmd
   python -m venv .venv
   call .venv\Scripts\activate
   pip install -r requirements.txt
   ```

---

## Running the Application

For a quick one-step startup that launches both the server and the frontend in your browser:

- **Linux / Mac**:
  ```bash
  ./run.sh
  ```
- **Windows**:
  ```cmd
  run.bat
  ```

Alternatively, run uvicorn manually:
```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```
Then visit `http://localhost:8000` in your web browser.

---

## CLI Usage

You can also interact with the engine directly using the command-line:

### 1. Train a model
```bash
python cli.py train --input data/sample.txt --state-size 2 --save my_model
```

### 2. Generate sentences
```bash
python cli.py generate --model my_model --count 5 --max-chars 280
```

### 3. Combine two models
```bash
python cli.py combine --models model_a model_b --weights 1.5 0.8 --save combined_model
```

---

## API Endpoints Reference

| Method | Endpoint | Description | Request Body Example | Response Example |
|---|---|---|---|---|
| **GET** | `/health` | Server health check and model count | None | `{"status": "ok", "models_count": 5}` |
| **GET** | `/models` | List all saved models with metadata | None | `{"models": [{"model_id": "...", "state_size": 2, ...}]}` |
| **POST** | `/train` | Train a new model from text | `{"text": "...", "state_size": 2, "sentence_split": false}` | `{"model_id": "...", "state_size": 2, ...}` |
| **POST** | `/generate` | Generate sentences from a model | `{"model_id": "...", "count": 5, "max_chars": 280}` | `{"sentences": ["First sentence.", ...]}` |
| **POST** | `/combine` | Combine two models with weights | `{"model_ids": ["id_a", "id_b"], "weights": [1.5, 0.5], "save_as": "name"}` | `{"model_id": "combined_uuid"}` |
| **DELETE** | `/models/{id}` | Permanently delete a model | None | `{"deleted": "model_uuid"}` |

---

## Screen Captures

Below are placeholders for the interface:

#### 1. Train Tab
*Placeholder for training interface*

#### 2. Generate Tab
*Placeholder for generation interface*

#### 3. Combine Tab
*Placeholder for combination interface*

#### 4. Models List Tab
*Placeholder for models list interface*
