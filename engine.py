import markovify
import os
import json


def build_model(text, state_size=2):
    """
    Build a markovify.Text model from the given text.

    Args:
        text (str): The input text to build the model from.
        state_size (int): The number of previous words to consider for the next word.

    Returns:
        markovify.Text: The constructed Markov model.

    Raises:
        ValueError: If the input text is empty or None.
    """
    if not text:
        raise ValueError("Input text cannot be empty or None")
    try:
        model = markovify.Text(text, state_size=state_size)
        return model
    except Exception as e:
        raise RuntimeError(f"Failed to build model: {e}")


def generate_sentences(model, count=5):
    """
    Generate a list of sentences from the model.

    Args:
        model (markovify.Text): The trained Markov model.
        count (int): The number of sentences to generate.

    Returns:
        list: A list of generated sentences (strings). May contain fewer than `count` if sentence generation fails.
    """
    if model is None:
        return []
    sentences = []
    attempts = 0
    max_attempts = count * 2  # Avoid infinite loop
    while len(sentences) < count and attempts < max_attempts:
        sentence = model.make_sentence()
        if sentence:
            sentences.append(sentence)
        attempts += 1
    return sentences


def generate_short_sentences(model, count=3, max_chars=280):
    """
    Generate a list of short sentences (within character limit) from the model.

    Args:
        model (markovify.Text): The trained Markov model.
        count (int): The number of sentences to generate.
        max_chars (int): Maximum characters allowed per sentence.

    Returns:
        list: A list of generated short sentences (strings). May contain fewer than `count`.
    """
    if model is None:
        return []
    sentences = []
    attempts = 0
    max_attempts = count * 2  # Avoid infinite loop
    while len(sentences) < count and attempts < max_attempts:
        sentence = model.make_sentence()
        if sentence and len(sentence) <= max_chars:
            sentences.append(sentence)
        attempts += 1
    return sentences


def save_model(model, filepath):
    """
    Save the model as JSON to the specified filepath.

    Args:
        model (markovify.Text): The model to save.
        filepath (str): The path to the file where the model will be saved.

    Raises:
        ValueError: If the model is None.
        IOError: If there is an issue writing to the file.
    """
    if model is None:
        raise ValueError("Cannot save a None model")
    try:
        # Ensure the directory exists
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath, 'w') as f:
            f.write(model.to_json())
    except Exception as e:
        raise IOError(f"Failed to save model to {filepath}: {e}")


def load_model(filepath):
    """
    Load a model from a JSON file.

    Args:
        filepath (str): The path to the JSON file containing the model.

    Returns:
        markovify.Text: The loaded model.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file does not contain a valid model.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model file not found: {filepath}")
    try:
        with open(filepath, 'r') as f:
            model_json = f.read()
        return markovify.Text.from_json(model_json)
    except Exception as e:
        raise ValueError(f"Failed to load model from {filepath}: {e}")