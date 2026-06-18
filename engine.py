import markovify
import os
import json


def build_model(text, state_size=2, newline=False):
    if not text:
        raise ValueError("Input text cannot be empty or None")
    try:
        if newline:
            model = markovify.NewlineText(text, state_size=state_size)
        else:
            model = markovify.Text(text, state_size=state_size)
        return model
    except Exception as e:
        raise RuntimeError(f"Failed to build model: {e}")


def generate_sentences(model, count=5, test_output=True):
    if model is None:
        return []
    sentences = []
    attempts = 0
    max_attempts = count * 10
    while len(sentences) < count and attempts < max_attempts:
        sentence = model.make_sentence(test_output=test_output)
        if sentence:
            sentences.append(sentence)
        attempts += 1
    return sentences


def generate_short_sentences(model, count=3, max_chars=280, test_output=True):
    if model is None:
        return []
    sentences = []
    attempts = 0
    max_attempts = count * 10
    while len(sentences) < count and attempts < max_attempts:
        sentence = model.make_short_sentence(max_chars, test_output=test_output)
        if sentence:
            sentences.append(sentence)
        attempts += 1
    return sentences


def save_model(model, filepath):
    if model is None:
        raise ValueError("Cannot save a None model")
    try:
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath, 'w') as f:
            f.write(model.to_json())
    except Exception as e:
        raise IOError(f"Failed to save model to {filepath}: {e}")


def load_model(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model file not found: {filepath}")
    try:
        with open(filepath, 'r') as f:
            model_json = f.read()
        return markovify.Text.from_json(model_json)
    except Exception as e:
        raise ValueError(f"Failed to load model from {filepath}: {e}")