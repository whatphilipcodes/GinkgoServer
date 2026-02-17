from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from ginkgo.connector import manager

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "running"}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            target = "unreal" if client_id == "frontend" else "frontend"
            await manager.send_to(data, target)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
