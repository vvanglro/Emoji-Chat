import time
import json
import random

import redis
from dataclasses import dataclass


@dataclass
class Message:
    uid: str
    msg: str
    room_id: str
    ts: str = None

    def to_json(self):
        return json.dumps(self.__dict__)


class DB:
    def __init__(self):
        self.redis_config = {
            "host": "redis",
            "port": "6379",
            "passwd": None,
            "db": "1",
            "room_max_online": 30,  # 房间最大在线人数
            "room_key": "EmojiChat::room",
        }

        self.db = redis.Redis(
            host=self.redis_config["host"],
            port=self.redis_config["port"],
            password=self.redis_config["passwd"],
            db=self.redis_config["db"],
            decode_responses=True,
        )
        self.DEFAULT_ROOM_ID = "WECHAT@1000"  # 默认房间名

    def __rand_room_id(self):
        # 随机生成搞一个房间 ID
        while True:
            room_id = (
                random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4)
                + "@"
                + random.randint(1000, 9999)
            )
            if self.db.hexists(self.redis_config["room_key"], room_id) == 0:
                break
        return room_id

    def init_room(self):
        # 初始化房间
        room_id = self.__rand_room_id()
        self.db.hset(self.redis_config["room_key"], room_id, 0)  # 房间人数初始为 0

    def into_room(self, uid: str, room_id: str):
        # 用户进入房间
        if (
            self.db.hget(self.redis_config["room_key"], room_id)
            < self.redis_config["room_max_online"]
        ):
            self.db.hincrby(self.redis_config["room_key"], room_id, 1)
            self.db.lpush(f"EmojiChat::{room_id}::users", uid)
            return 1
        else:
            return 0

    def leave_room(self, uid: str, room_id: str):
        # 用户离开房间
        if self.db.hget(self.redis_config["room_key"], room_id) > 0:
            self.db.hincrby(self.redis_config["room_key"], room_id, -1)
            self.db.lrem(self.redis_config["room_key"], 0, uid)

    def get_users(self, room_id: str):
        # 查询房间中全部用户
        users = self.db.lrange(f"EmojiChat::{room_id}::users", 0, -1)
        return users

    def get_message(self, room_id: str):
        # 查询房间中的历史消息
        message_list = self.db.lrange(f"EmojiChat::{room_id}::message", 0, -1)
        return [json.loads(msg) for msg in message_list]

    def new_message(self, message: Message):
        if message.ts is None:
            message.ts = int(time.time())

        data = message.__dict__
        room_id = data.pop("room_id")
        self.db.lpush(f"EmojiChat::{room_id}::message", message.to_json())
