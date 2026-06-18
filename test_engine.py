import os
from engine import build_model, generate_sentences, generate_short_sentences, save_model, load_model

def main():
    input_file = 'data/sample.txt'
    model_file = 'models/sample.json'

    print(f"--- Training model on {input_file} ---")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()

        model = build_model(text)
        print("Model trained successfully.")

        print("\n--- Generating 5 sentences ---")
        sentences = generate_sentences(model, count=5)
        for i, s in enumerate(sentences, 1):
            print(f"{i}: {s}")

        print(f"\n--- Saving model to {model_file} ---")
        save_model(model, model_file)
        print("Model saved.")

        print(f"\n--- Loading model back from {model_file} ---")
        loaded_model = load_model(model_file)
        print("Model loaded.")

        print("\n--- Generating 3 short sentences (< 280 chars) ---")
        short_sentences = generate_short_sentences(loaded_model, count=3, max_chars=280)
        for i, s in enumerate(short_sentences, 1):
            print(f"{i}: {s}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
