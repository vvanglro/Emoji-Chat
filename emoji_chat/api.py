from __future__ import annotations
import asyncio
import json
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from obscure64 import Obscure64
from starlette.websockets import WebSocketState

from emoji_chat.db import RedisServerObj, Message


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await RedisServerObj.connect()
    yield
    await RedisServerObj.close()


app = FastAPI(lifespan=lifespan)
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
    @classmethod
    async def connect(cls, room_id, user_id, websocket: WebSocket):
        await websocket.accept()
        if not await RedisServerObj.into_room(room_id, user_id):
            await websocket.send_json({"code": 401, "msg": "人数已满"})
            await websocket.close()
            return False
        return True

    @classmethod
    async def disconnect(cls, room_id, user_id, websocket: WebSocket):
        if websocket.client_state is not WebSocketState.DISCONNECTED:
            await websocket.close()
        await RedisServerObj.leave_room(room_id, user_id)

    @classmethod
    async def broadcast(cls, room_id, websocket, message):
        for user_id, connection in (await RedisServerObj.get_users(room_id)).items():
            if connection != websocket:
                await connection.send_json(message.to_json())


manager = ConnectionManager()


@app.post("/api/newchat")
async def new_chat():
    room_id = uuid.uuid4().hex
    return {"room_id": room_id}


@app.get("/")
async def get_homepage(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/chat")
async def get_chat_page(request: Request, room_id: str):
    return templates.TemplateResponse(
        "chat.html", {"request": request, "room_id": room_id}
    )


@app.get("/mesage/query")
async def get_message(room_id: str):
    return {"data": await RedisServerObj.get_message(room_id)}


@app.post("/api/decrypt")
async def decrypt_message(
    body=Body(...),
):
    return {"response": ob64.decode(body.get("message")).decode("utf-8")}


@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    if not await manager.connect(room_id, user_id, websocket):
        return

    # 订阅 Redis 频道
    pubsub = RedisServerObj.pool.pubsub()
    await pubsub.subscribe(room_id)

    async def receive_messages():
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                receive_data = json.loads(message["data"].decode("utf-8"))
                if (uid := receive_data.get("uid")) and uid.split("#")[1] == user_id:
                    continue
                await websocket.send_text(message["data"].decode("utf-8"))
            await asyncio.sleep(0.5)

    receiver_task = asyncio.create_task(receive_messages())
    try:
        while True:
            data = await websocket.receive_json()
            try:
                data["msg"] = ob64.encode(data["msg"].encode("utf-8")).decode("utf-8")
                msg = Message(**data)
                await RedisServerObj.new_message(room_id, msg)
                await RedisServerObj.pool.publish(room_id, msg.to_json())
                # await manager.broadcast(room_id, websocket, msg)
            except Exception as e:
                raise ValueError("Message 数据错误: " + str(e))

    except WebSocketDisconnect:
        await manager.disconnect(room_id, user_id, websocket)
        receiver_task.cancel()
        await pubsub.unsubscribe(room_id)
        await pubsub.close()
