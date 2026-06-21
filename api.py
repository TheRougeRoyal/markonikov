import os
import re
import uuid
import json
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

import markovify
import engine
import database

LOG_LEVEL = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("markovify")

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = Path(os.environ.get("MARKOVIFY_FRONTEND_DIR", str(BASE_DIR / "frontend")))
API_KEY = os.environ.get("MARKOVIFY_API_KEY", "")

MODEL_ID_RE = re.compile(r"^[a-f0-9\-]{36}$")

app = FastAPI(title="Markovify API")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("MARKOVIFY_CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(key: Optional[str] = Security(api_key_header)):
    if not API_KEY:
        return
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")


def validate_model_id(model_id: str) -> str:
    if not MODEL_ID_RE.match(model_id):
        raise HTTPException(status_code=400, detail="Invalid model id format")
    return model_id


class TrainRequest(BaseModel):
    text: str
    state_size: int = 2
    sentence_split: bool = False

class TrainResponse(BaseModel):
    model_id: str
    state_size: int
    created_at: str
    sentence_split: bool

class GenerateRequest(BaseModel):
    model_id: str
    count: int = 5
    max_chars: Optional[int] = None

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
    save_as: Optional[str] = None

class CombineResponse(BaseModel):
    model_id: str

FRONTEND_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    database.init_db()
    from seed import seed_models
    seed_models()
    logger.info("Application started, database initialized, models seeded")


def _build_model_from_request(text: str, state_size: int, sentence_split: bool):
    if sentence_split:
        return markovify.NewlineText(text, state_size=state_size)
    return engine.build_model(text, state_size=state_size)


@app.post("/train", response_model=TrainResponse, dependencies=[Depends(verify_api_key)])
@limiter.limit("5/minute")
async def train(request: Request, body: TrainRequest):
    try:
        model = _build_model_from_request(
            body.text, body.state_size, body.sentence_split
        )
        model_id = str(uuid.uuid4())
        model_json = model.to_json()
        created_at = datetime.now(timezone.utc).isoformat()
        preview = body.text[:200] if body.text else None
        database.save_model_to_db(
            model_id, model_json, body.state_size, body.sentence_split,
            created_at, training_text_preview=preview,
        )
        return TrainResponse(
            model_id=model_id,
            state_size=body.state_size,
            created_at=created_at,
            sentence_split=body.sentence_split,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@app.post("/generate", response_model=GenerateResponse, dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
async def generate(request: Request, body: GenerateRequest):
    validate_model_id(body.model_id)
    model_json = database.load_model_from_db(body.model_id)
    if not model_json:
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        model = markovify.Text.from_json(model_json)
        if body.max_chars and body.max_chars > 0:
            sentences = engine.generate_short_sentences(
                model, count=body.count, max_chars=body.max_chars
            )
        else:
            sentences = engine.generate_sentences(model, count=body.count)
        return GenerateResponse(sentences=sentences)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Model corrupted: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@app.get("/health")
@limiter.limit("30/minute")
async def health(request: Request):
    count = database.model_count()
    integrity = {"total": count, "valid": 0, "corrupted": []}

    models = database.list_models()
    for m in models:
        model_json = database.load_model_from_db(m["model_id"])
        if not model_json:
            integrity["corrupted"].append(m["model_id"])
            continue
        try:
            markovify.Text.from_json(model_json)
            integrity["valid"] += 1
        except Exception:
            integrity["corrupted"].append(m["model_id"])

    status = "ok" if not integrity["corrupted"] else "degraded"
    return {
        "status": status,
        "models_count": count,
        "integrity": integrity,
    }


@app.get("/models", response_model=ModelsResponse, dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
async def list_models(request: Request):
    models = database.list_models()
    return ModelsResponse(models=[
        ModelInfo(
            model_id=m["model_id"],
            state_size=m["state_size"],
            created_at=m["created_at"],
            sentence_split=m["sentence_split"],
        )
        for m in models
    ])


@app.delete("/models/{model_id}", dependencies=[Depends(verify_api_key)])
@limiter.limit("5/minute")
async def delete_model(request: Request, model_id: str):
    validate_model_id(model_id)
    deleted = database.delete_model_from_db(model_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"deleted": model_id}


@app.post("/combine", response_model=CombineResponse, dependencies=[Depends(verify_api_key)])
@limiter.limit("3/minute")
async def combine(request: Request, body: CombineRequest):
    if len(body.model_ids) != len(body.weights):
        raise HTTPException(
            status_code=400,
            detail="model_ids and weights must be the same length",
        )
    if len(body.model_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="Need at least two models to combine",
        )

    models = []
    for mid in body.model_ids:
        validate_model_id(mid)
        model_json = database.load_model_from_db(mid)
        if not model_json:
            raise HTTPException(status_code=404, detail=f"Model not found: {mid}")
        try:
            models.append(markovify.Text.from_json(model_json))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load model {mid}: {e}")

    try:
        combined = markovify.combine(models, body.weights)
        combined_state_size = combined.state_size

        new_id = str(uuid.uuid4())
        model_json = combined.to_json()
        created_at = datetime.now(timezone.utc).isoformat()
        database.save_model_to_db(
            new_id, model_json, combined_state_size, False, created_at,
            combined_from=list(body.model_ids),
            weights=list(body.weights),
            save_as=body.save_as,
        )
        return CombineResponse(model_id=new_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Combine failed: {e}")


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("MARKOVIFY_HOST", "0.0.0.0")
    port = int(os.environ.get("MARKOVIFY_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
