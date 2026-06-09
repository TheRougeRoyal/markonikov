import os
import uuid
import json
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import markovify
import engine

app = FastAPI(title="Markovify API")

# Add CORS middleware to support local testing and different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class TrainRequest(BaseModel):
    text: str
    state_size: int = 2
    sentence_split: bool = False  # True = newline-separated sentences, False = paragraph

class TrainResponse(BaseModel):
    model_id: str
    state_size: int
    created_at: str
    sentence_split: bool

class GenerateRequest(BaseModel):
    model_id: str
    count: int = 5
    max_chars: Optional[int] = None  # Optional character limit per sentence

class GenerateResponse(BaseModel):
    sentences: List[str]

class ModelInfo(BaseModel):
    model_id: str
    state_size: int
    created_at: str
    sentence_split: bool

class ModelsResponse(BaseModel):
    models: List[ModelInfo]

class CombineRequest(BaseModel):
    model_ids: List[str]
    weights: List[float]
    save_as: Optional[str] = None  # Optional logical name (unused for storage today)

class CombineResponse(BaseModel):
    model_id: str

# Configuration
MODELS_DIR = "models"
FRONTEND_DIR = "frontend"

# Ensure directories exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(FRONTEND_DIR, exist_ok=True)


def _read_meta(model_id: str) -> dict:
    """Read sidecar metadata for a model, returning empty dict if missing/corrupt."""
    meta_path = os.path.join(MODELS_DIR, f"{model_id}.meta.json")
    if not os.path.exists(meta_path):
        return {}
    try:
        with open(meta_path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_meta(model_id: str, meta: dict) -> None:
    meta_path = os.path.join(MODELS_DIR, f"{model_id}.meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f)


def _build_model_from_request(text: str, state_size: int, sentence_split: bool):
    """Construct a markovify model, optionally treating each line as a sentence."""
    if sentence_split:
        # Newline-separated sentences: use markovify.NewlineText to treat each line
        # as a separate sentence.
        return markovify.NewlineText(text, state_size=state_size)
    return engine.build_model(text, state_size=state_size)


@app.post("/train", response_model=TrainResponse)
async def train(request: TrainRequest):
    try:
        model = _build_model_from_request(
            request.text, request.state_size, request.sentence_split
        )
        model_id = str(uuid.uuid4())
        filepath = os.path.join(MODELS_DIR, f"{model_id}.json")
        engine.save_model(model, filepath)
        created_at = datetime.now(timezone.utc).isoformat()
        _write_meta(model_id, {
            "state_size": request.state_size,
            "created_at": created_at,
            "sentence_split": request.sentence_split,
        })
        return TrainResponse(
            model_id=model_id,
            state_size=request.state_size,
            created_at=created_at,
            sentence_split=request.sentence_split,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    filepath = os.path.join(MODELS_DIR, f"{request.model_id}.json")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        model = engine.load_model(filepath)
        if request.max_chars and request.max_chars > 0:
            sentences = engine.generate_short_sentences(
                model, count=request.count, max_chars=request.max_chars
            )
        else:
            sentences = engine.generate_sentences(model, count=request.count)
        return GenerateResponse(sentences=sentences)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Model corrupted: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@app.get("/health")
async def health():
    if not os.path.exists(MODELS_DIR):
        count = 0
    else:
        count = len([
            fname for fname in os.listdir(MODELS_DIR)
            if fname.endswith(".json") and not fname.endswith(".meta.json")
        ])
    return {"status": "ok", "models_count": count}


@app.get("/models", response_model=ModelsResponse)
async def list_models():
    if not os.path.exists(MODELS_DIR):
        return ModelsResponse(models=[])

    out: List[ModelInfo] = []
    for fname in os.listdir(MODELS_DIR):
        if not fname.endswith(".json") or fname.endswith(".meta.json"):
            continue
        model_id = os.path.splitext(fname)[0]
        meta = _read_meta(model_id)
        out.append(ModelInfo(
            model_id=model_id,
            state_size=meta.get("state_size", 2),
            created_at=meta.get("created_at", "unknown"),
            sentence_split=meta.get("sentence_split", False),
        ))
    # newest first
    out.sort(key=lambda m: m.created_at, reverse=True)
    return ModelsResponse(models=out)


@app.delete("/models/{model_id}")
async def delete_model(model_id: str):
    # Basic safety: only accept uuid-like ids to avoid path traversal.
    if "/" in model_id or "\\" in model_id or ".." in model_id:
        raise HTTPException(status_code=400, detail="Invalid model id")

    filepath = os.path.join(MODELS_DIR, f"{model_id}.json")
    meta_path = os.path.join(MODELS_DIR, f"{model_id}.meta.json")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Model not found")
    try:
        os.remove(filepath)
        if os.path.exists(meta_path):
            os.remove(meta_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete: {e}")
    return {"deleted": model_id}


@app.post("/combine", response_model=CombineResponse)
async def combine(request: CombineRequest):
    if len(request.model_ids) != len(request.weights):
        raise HTTPException(
            status_code=400,
            detail="model_ids and weights must be the same length",
        )
    if len(request.model_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="Need at least two models to combine",
        )

    # Load each model, then combine them using markovify.combine
    models = []
    for mid in request.model_ids:
        if "/" in mid or "\\" in mid or ".." in mid:
            raise HTTPException(status_code=400, detail="Invalid model id")
        fp = os.path.join(MODELS_DIR, f"{mid}.json")
        if not os.path.exists(fp):
            raise HTTPException(status_code=404, detail=f"Model not found: {mid}")
        try:
            models.append(engine.load_model(fp))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load model {mid}: {e}")

    try:
        combined = markovify.combine(models, request.weights)
        combined_state_size = combined.state_size

        new_id = str(uuid.uuid4())
        new_path = os.path.join(MODELS_DIR, f"{new_id}.json")
        engine.save_model(combined, new_path)
        created_at = datetime.now(timezone.utc).isoformat()
        _write_meta(new_id, {
            "state_size": combined_state_size,
            "created_at": created_at,
            "sentence_split": False,
            "combined_from": list(request.model_ids),
            "weights": list(request.weights),
            "save_as": request.save_as,
        })
        return CombineResponse(model_id=new_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Combine failed: {e}")


# Serve frontend statically at "/"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
