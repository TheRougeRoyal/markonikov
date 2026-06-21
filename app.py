import os
import sys


def main():
    host = os.environ.get("MARKOVIFY_HOST", "0.0.0.0")
    port = int(os.environ.get("MARKOVIFY_PORT", "8000"))
    print(f"Starting Markovify API on http://{host}:{port}")
    print("Press Ctrl+C to stop.")

    import uvicorn
    uvicorn.run("api:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()