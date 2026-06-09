import asyncio
import httpx
import json
import time

BASE_URL = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient() as client:
        # Train first model
        resp = await client.post(f"{BASE_URL}/train", json={
            "text": "The quick brown fox jumps over the lazy dog. ",
            "state_size": 2,
            "sentence_split": False
        })
        print("Train 1:", resp.json())
        model1 = resp.json()["model_id"]

        # Train second model
        resp = await client.post(f"{BASE_URL}/train", json={
            "text": "Hello world! This is a test sentence. ",
            "state_size": 2,
            "sentence_split": False
        })
        print("Train 2:", resp.json())
        model2 = resp.json()["model_id"]

        # Combine models
        resp = await client.post(f"{BASE_URL}/combine", json={
            "model_ids": [model1, model2],
            "weights": [0.5, 0.5],
            "save_as": "test"
        })
        print("Combine:", resp.json())
        combined_id = resp.json()["model_id"]

        # Generate from combined model
        resp = await client.post(f"{BASE_URL}/generate", json={
            "model_id": combined_id,
            "count": 3
        })
        print("Generate:", resp.json())

if __name__ == "__main__":
    import uvicorn
    import threading
    import sys

    # Start server in a thread
    config = uvicorn.Config("api:app", host="0.0.0.0", port=8000, log_level="warning")
    server = uvicorn.Server(config)

    def run_server():
        server.run()

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    # Give server time to start
    time.sleep(2)

    asyncio.run(main())