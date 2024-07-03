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
    group_id: str
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
        self._group_key: str = "chat:group:"
        self.group_msgs_key: str = f"{self._group_key}msg:"
        self.group_people_num_key: str = f"{self._group_key}num:"

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

    async def into_group(self, group_id):
        # 用户进入房间
        if (num := await self.count_group_members(group_id)) and int(num) >= settings.GROUP_MAX_ONLINE:
            return False
        await self.pool.incr(self.group_people_num_key + group_id)
        return True

    async def leave_group(self, group_id):
        # 用户离开房间
        if await self.pool.decr(self.group_people_num_key + group_id) == 0:
            await self.pool.delete(self.group_people_num_key + group_id)
            await self.pool.delete(self.group_msgs_key + group_id)

    async def get_message(self, group_id: str):
        # 查询房间中的历史消息
        message_list = await self.pool.xrange(self.group_msgs_key + group_id, "-", "+", 30)
        return [msg for _id, msg in message_list]

    async def count_group_members(self, group_id: str):
        # 统计房间在线人数
        return await self.pool.get(self.group_people_num_key + group_id)

    async def get_group_list(self):
        # 获取所有房间
        async with self.pool.pipeline() as pipe:
            await pipe.keys(self.group_people_num_key + "*")
            group_keys = await pipe.execute()
            group_id_list = [group_key.removeprefix(self.group_people_num_key) for group_key in group_keys[0]]
            for group_id in group_keys[0]:
                await pipe.get(group_id)
            return [{"group_id": group_id, "member_count": count} for group_id, count in zip(group_id_list, await pipe.execute())]

    async def new_message(self, group_id, message: Message):
        await self.pool.xadd(self.group_msgs_key + group_id, fields=message.to_dict())


RedisServerObj = RedisServer()
