import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Dict

DB_PATH = Path(os.environ.get("MARKOVIFY_DB_PATH", "markovify.db"))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS models (
            model_id TEXT PRIMARY KEY,
            model_json TEXT NOT NULL,
            state_size INTEGER NOT NULL DEFAULT 2,
            created_at TEXT NOT NULL,
            sentence_split INTEGER NOT NULL DEFAULT 0,
            combined_from TEXT,
            weights TEXT,
            save_as TEXT,
            training_text_preview TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_models_created ON models(created_at DESC);
    """)
    conn.close()


def save_model_to_db(model_id: str, model_json: str, state_size: int,
                     sentence_split: bool, created_at: str,
                     combined_from: Optional[List[str]] = None,
                     weights: Optional[List[float]] = None,
                     save_as: Optional[str] = None,
                     training_text_preview: Optional[str] = None):
    conn = get_connection()
    conn.execute(
        """INSERT INTO models (model_id, model_json, state_size, created_at,
           sentence_split, combined_from, weights, save_as, training_text_preview)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (model_id, model_json, state_size, created_at,
         1 if sentence_split else 0,
         json.dumps(combined_from) if combined_from else None,
         json.dumps(weights) if weights else None,
         save_as,
         training_text_preview[:500] if training_text_preview else None),
    )
    conn.commit()
    conn.close()


def load_model_from_db(model_id: str) -> Optional[str]:
    conn = get_connection()
    row = conn.execute("SELECT model_json FROM models WHERE model_id = ?", (model_id,)).fetchone()
    conn.close()
    return row["model_json"] if row else None


def get_model_meta(model_id: str) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        """SELECT model_id, state_size, created_at, sentence_split,
           combined_from, weights, save_as, training_text_preview
           FROM models WHERE model_id = ?""",
        (model_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "model_id": row["model_id"],
        "state_size": row["state_size"],
        "created_at": row["created_at"],
        "sentence_split": bool(row["sentence_split"]),
        "combined_from": json.loads(row["combined_from"]) if row["combined_from"] else None,
        "weights": json.loads(row["weights"]) if row["weights"] else None,
        "save_as": row["save_as"],
        "training_text_preview": row["training_text_preview"],
    }


def list_models() -> List[Dict]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT model_id, state_size, created_at, sentence_split,
           combined_from, weights, save_as, training_text_preview
           FROM models ORDER BY created_at DESC"""
    ).fetchall()
    conn.close()
    return [
        {
            "model_id": r["model_id"],
            "state_size": r["state_size"],
            "created_at": r["created_at"],
            "sentence_split": bool(r["sentence_split"]),
            "combined_from": json.loads(r["combined_from"]) if r["combined_from"] else None,
            "weights": json.loads(r["weights"]) if r["weights"] else None,
            "save_as": r["save_as"],
            "training_text_preview": r["training_text_preview"],
        }
        for r in rows
    ]


def delete_model_from_db(model_id: str) -> bool:
    conn = get_connection()
    cursor = conn.execute("DELETE FROM models WHERE model_id = ?", (model_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def model_count() -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as cnt FROM models").fetchone()
    conn.close()
    return row["cnt"]
