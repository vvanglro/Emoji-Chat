from __future__ import annotations
import dataclasses
import time
import json
import redis.asyncio as redis
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool

from emoji_chat.config import settings


@dataclasses.dataclass
class Message:
    uid: str
    msg: str
    emoji_msg: str
    room_id: str
    ts: int | None = None

    def to_json(self):
        if self.ts is None:
            self.ts = int(time.time())
        return json.dumps(dataclasses.asdict(self), ensure_ascii=False)

    def to_dict(self):
        if self.ts is None:
            self.ts = int(time.time())
        return dataclasses.asdict(self)


class RedisServer:
    def __init__(self):
        self._pool = None
        self.room_key: str = "chat:room:"

    @property
    def pool(self) -> Redis:
        return self._pool

    async def close(self) -> None:
        """
        Closes connection and resets pool
        """
        if self._pool is not None:
            await self._pool.close()
        self._pool = None

    async def connect(self):
        pool = ConnectionPool.from_url(url=settings.REDIS_URL, decode_responses=True)
        self._pool = redis.Redis(connection_pool=pool)
        await self._pool.ping()

    async def into_room(self, room_id):
        # 用户进入房间
        if (num := await self.pool.get(self.room_key + room_id)) and int(num) >= settings.ROOM_MAX_ONLINE:
            return False
        await self.pool.incr(self.room_key + room_id)
        return True

    async def leave_room(self, room_id):
        # 用户离开房间
        if await self.pool.decr(self.room_key + room_id) == 0:
            await self.pool.delete(self.room_key + room_id)
            await self.pool.delete(room_id)

    async def get_message(self, room_id: str):
        # 查询房间中的历史消息
        message_list = await self.pool.xrange(room_id, "-", "+", 30)
        return [msg for _id, msg in message_list]

    async def new_message(self, room_id, message: Message):
        await self.pool.xadd(room_id, fields=message.to_dict())


RedisServerObj = RedisServer()
