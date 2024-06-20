import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List

from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from obscure64 import Obscure64

from . import Message, DB

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="templates")
app.mount(
    "/static", StaticFiles(directory="static"), name="static"
)  # Serve static files
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

    async def broadcast(self, websocket, message):
        for connection in self.active_connections:
            if connection != websocket:
                await connection.send_text(message.to_json())


db = DB()
manager = ConnectionManager()


@app.get("/")
async def get(request: Request, rid:str=None):
    room_id = rid or db.DEFAULT_ROOM_ID
    return templates.TemplateResponse(
        request=request, name="index.html", context={"room_id": room_id}
    )


@app.get("/mesage/query")
async def get_message(room_id: str):
    print(db.get_message(room_id))
    return {"data": db.get_message(room_id)}


@app.post("/api/decrypt")
async def decrypt_message(
    body=Body(...),
):
    return {"response": ob64.decode(body.get("message")).decode("utf-8")}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                data = json.loads(data)
                print(data)
                data["msg"] = ob64.encode(data["msg"].encode("utf-8")).decode("utf-8")
                msg = Message(**data)
                db.new_message(msg)
                await manager.broadcast(websocket, msg)
            except Exception as e:
                raise ValueError("Message 数据错误: " + str(e))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
