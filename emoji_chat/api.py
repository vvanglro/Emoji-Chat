from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List

from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from obscure64 import Obscure64

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")  # Serve static files
ob64 = Obscure64(
    b64chars="🙈🙉🙊🐒🐶🐕🐩🐺🐱😹😻😼🙀😿🐈🐯🐅🐴🐎🐮🐂🐃🐄🐷🐖🐗🐽🐑🐐🐪🐘🐭🐀🐹"
             "🐰🐇🐻🐨🐼🐾🐔🐓🐣🐤🐥🐧🐸🐊🐢🐍🐲🐉🐳🐋🐬🐠🐡🐙🐚🐌🐛🐜🐝🐞🦋"
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, websocket, emoji, message):
        for connection in self.active_connections:
            if connection != websocket:
                await connection.send_text(f"{emoji}:{ob64.encode(message.encode('utf-8')).decode('utf-8')}")


manager = ConnectionManager()


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/decrypt")
async def decrypt_message(
        body=Body(...),
):
    return {"response": ob64.decode(body.get('message')).decode('utf-8')}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            emoji, message = data.split(":", 1)
            await manager.broadcast(websocket, emoji, message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
