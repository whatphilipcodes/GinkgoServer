import asyncio

import uvicorn
from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Client connected!")

    try:
        counter = 0
        while True:
            # Try to receive a message (non-blocking)
            try:
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=2.0
                )
                print(f"📥 Received from client: {message}")
            except asyncio.TimeoutError:
                # No problem — after 2 seconds timeout we just send anyway
                pass

            # Send a string every 2 seconds
            server_message = f"Hello from Python Server! Count: {counter}"
            await websocket.send_text(server_message)
            print(f"📤 Sent: {server_message}")

            counter += 1

    except Exception as e:
        print(f"❌ Connection closed: {e}")
    finally:
        print("👋 Client disconnected")

if __name__ == "__main__":
    print("🚀 Starting WebSocket Server on ws://127.0.0.1:8000/ws")
    uvicorn.run(app, host="127.0.0.1", port=8000)