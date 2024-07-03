from __future__ import annotations
import asyncio
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from obscure64 import Obscure64
from starlette.websockets import WebSocketState

from emoji_chat.db import RedisServerObj, Message
from emoji_chat.emoji import get_emoji


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
app.mount("/static", StaticFiles(directory="static"), name="static")  # Serve static files


class ConnectionManager:
    @classmethod
    async def connect(cls, group_id, websocket: WebSocket):
        await websocket.accept()
        if not await RedisServerObj.into_group(group_id):
            await websocket.send_json({"code": 10401, "msg": "人数已满"})
            await websocket.close()
            return False
        return True

    @classmethod
    async def disconnect(cls, group_id, websocket: WebSocket):
        if websocket.client_state is not WebSocketState.DISCONNECTED:
            await websocket.close()
        await RedisServerObj.leave_group(group_id)


manager = ConnectionManager()


@app.post("/api/newchat")
async def new_chat():
    # 以后可以在这里进行房间的初始化信息
    group_id = uuid.uuid4().hex
    return {"group_id": group_id}


@app.get("/")
async def get_homepage(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/group/chat")
async def get_group_page(request: Request):
    return templates.TemplateResponse(request=request, name="group.html")


@app.get("/chat")
async def get_chat_page(request: Request, group_id: uuid.UUID):
    return templates.TemplateResponse("chat.html", {"request": request, "group_id": group_id})


@app.get("/mesage/query")
async def get_message(group_id: uuid.UUID):
    return {"data": await RedisServerObj.get_message(group_id.hex)}


@app.get("/group/query")
async def get_group_list():
    return {"data": await RedisServerObj.get_group_list()}


@app.websocket("/ws/{group_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, group_id: str, user_id: str):
    if not await manager.connect(group_id, websocket):
        return

    async def receive_messages():
        while True:
            try:
                response = await RedisServerObj.pool.xread({RedisServerObj.group_msgs_key + group_id: "$"}, block=0)
                if response:
                    for stream, messages in response:
                        for message_id, message_data in messages:
                            if (uid := message_data.get("uid")) and uid.split("#")[1] == user_id:
                                continue
                            await websocket.send_json(message_data)
            except Exception as e:
                logging.error(e, exc_info=True)

    receiver_task = asyncio.create_task(receive_messages())
    try:
        while True:
            data = await websocket.receive_json()
            try:
                data["emoji_msg"] = Obscure64(b64chars=get_emoji()).encode(data["msg"].encode("utf-8")).decode("utf-8")
                msg = Message(**data)
                await RedisServerObj.new_message(group_id, msg)
            except Exception as e:
                logging.error("消息处理错误: " + str(e), exc_info=True)

    except WebSocketDisconnect:
        await manager.disconnect(group_id, websocket)
        receiver_task.cancel()
