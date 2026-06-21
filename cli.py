from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

import markovify

from engine import (
    build_model,
    generate_short_sentences,
    load_model,
    save_model,
)


BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"


def resolve_model_path(model_name: str) -> Path:
    model_path = Path(model_name)
    if model_path.suffix != ".json":
        model_path = model_path.with_suffix(".json")
    if not model_path.is_absolute():
        model_path = MODELS_DIR / model_path
    return model_path


def read_text_file(input_path: str) -> str:
    with open(input_path, "r", encoding="utf-8") as file_handle:
        return file_handle.read()


def train_command(args: argparse.Namespace) -> int:
    text = read_text_file(args.input)
    model = build_model(text, state_size=args.state_size, newline=args.newline)
    output_path = resolve_model_path(args.save)
    save_model(model, str(output_path))
    print(f"Saved model to {output_path}")
    return 0


def generate_command(args: argparse.Namespace) -> int:
    model_path = resolve_model_path(args.model)
    model = load_model(str(model_path))
    sentences = generate_short_sentences(
        model,
        count=args.count,
        max_chars=args.max_chars,
        test_output=not args.no_overlap,
    )

    if not sentences:
        print("No sentences could be generated.")
        return 0

    for index, sentence in enumerate(sentences, start=1):
        print(f"{index}. {sentence}")
    return 0


def combine_command(args: argparse.Namespace) -> int:
    if len(args.models) != 2:
        raise ValueError("combine requires exactly two model names")
    if len(args.weights) != 2:
        raise ValueError("combine requires exactly two weights")

    first_model = load_model(str(resolve_model_path(args.models[0])))
    second_model = load_model(str(resolve_model_path(args.models[1])))
    combined_model = markovify.combine([first_model, second_model], args.weights)

    output_path = resolve_model_path(args.save)
    save_model(combined_model, str(output_path))
    print(f"Saved combined model to {output_path}")
    return 0


def list_command(args: argparse.Namespace) -> int:
    if not MODELS_DIR.exists():
        print("No models directory found.")
        return 0

    model_files = sorted(MODELS_DIR.glob("*.json"))
    meta_files = {f.stem.replace(".meta", ""): f for f in MODELS_DIR.glob("*.meta.json")}

    if not model_files:
        print("No models found.")
        return 0

    print(f"{'Model Name':<30} {'State Size':<12} {'Created'}")
    print("-" * 70)

    for model_file in model_files:
        name = model_file.stem
        meta_path = meta_files.get(name)
        state_size = "2"
        created = "unknown"

        if meta_path and meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
                state_size = str(meta.get("state_size", 2))
                created = meta.get("created_at", "unknown")[:19]
            except Exception:
                pass

        print(f"{name:<30} {state_size:<12} {created}")

    print(f"\nTotal: {len(model_files)} model(s)")
    return 0


def delete_command(args: argparse.Namespace) -> int:
    model_path = resolve_model_path(args.model)
    model_json = MODELS_DIR / f"{model_path.stem}.json"
    meta_json = MODELS_DIR / f"{model_path.stem}.meta.json"

    if not model_json.exists():
        print(f"Error: Model '{args.model}' not found.", file=sys.stderr)
        return 1

    model_json.unlink()
    if meta_json.exists():
        meta_json.unlink()

    print(f"Deleted model: {args.model}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Markovify CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser("train", help="Train a model from a text file")
    train_parser.add_argument("--input", required=True, help="Path to the input text file")
    train_parser.add_argument("--state-size", type=int, default=2, help="Markov state size")
    train_parser.add_argument("--save", required=True, help="Model name to save")
    train_parser.add_argument("--newline", action="store_true", help="Use NewlineText instead of Text")
    train_parser.set_defaults(func=train_command)

    generate_parser = subparsers.add_parser("generate", help="Generate sentences from a saved model")
    generate_parser.add_argument("--model", required=True, help="Model name to load")
    generate_parser.add_argument("--count", type=int, default=5, help="Number of sentences to generate")
    generate_parser.add_argument("--max-chars", type=int, default=280, help="Maximum sentence length")
    generate_parser.add_argument("--no-overlap", action="store_true", help="Disable overlap check")
    generate_parser.set_defaults(func=generate_command)

    combine_parser = subparsers.add_parser("combine", help="Combine two saved models")
    combine_parser.add_argument("--models", nargs=2, required=True, help="Two model names to combine")
    combine_parser.add_argument(
        "--weights",
        nargs=2,
        type=float,
        required=True,
        help="Two weights corresponding to the models",
    )
    combine_parser.add_argument("--save", required=True, help="Model name to save")
    combine_parser.set_defaults(func=combine_command)

    list_parser = subparsers.add_parser("list", help="List all saved models")
    list_parser.set_defaults(func=list_command)

    delete_parser = subparsers.add_parser("delete", help="Delete a saved model")
    delete_parser.add_argument("--model", required=True, help="Model name to delete")
    delete_parser.set_defaults(func=delete_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())