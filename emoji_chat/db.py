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
    room_id: str
    ts: int | None = None

    def to_json(self):
        return json.dumps(dataclasses.asdict(self), ensure_ascii=False)


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
        pool = ConnectionPool.from_url(url=settings.REDIS_URL)
        self._pool = redis.Redis(connection_pool=pool)
        await self._pool.ping()

    async def into_room(self, room_id, user_id):
        # 用户进入房间
        if (
            len(await self.pool.hgetall(self.room_key + room_id)) + 1
            > settings.ROOM_MAX_ONLINE
        ):
            return False
        else:
            await self.pool.hset(self.room_key + room_id, user_id, "1")
            return True

    async def leave_room(self, room_id, user_id):
        # 用户离开房间
        await self.pool.hdel(self.room_key + room_id, user_id)
        if len(await self.pool.hgetall(self.room_key + room_id)) == 0:
            await self.pool.delete(self.room_key + "msgs:" + room_id)

    async def get_users(self, room_id: str) -> dict:
        # 查询房间中全部用户
        return await self.pool.hgetall(self.room_key + room_id)

    async def get_message(self, room_id: str):
        # 查询房间中的历史消息
        message_list = await self.pool.lrange(self.room_key + "msgs:" + room_id, 0, -1)
        return [json.loads(msg) for msg in message_list]

    async def new_message(self, room_id, message: Message):
        if message.ts is None:
            message.ts = int(time.time())

        await self.pool.rpush(self.room_key + "msgs:" + room_id, message.to_json())


RedisServerObj = RedisServer()
