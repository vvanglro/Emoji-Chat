import time
import json

from tinydb import TinyDB
from dataclasses import dataclass


class DB:
    def __init__(self):
        self.db = TinyDB("./data.json")

    def _insert(self, table_name: str, data: dict):
        try:
            table = self.db.table(table_name)
            table.insert(data)
        except:
            return 1
        else:
            return 0

    def _query(self, table_name: str):
        table = self.db.table(table_name)
        return table.all()


db = DB()


@dataclass
class Message:
    uid: int
    msg: str
    ts: str = None
    room_id: str = "0"

    def to_json(self):
        return json.dumps(self.__dict__)


class MessageManager:
    def __init__(self):
        pass

    def add(self, message: Message):
        if message.ts is None:
            message.ts = int(time.time())

        data = message.__dict__
        room_id = data.pop("room_id")
        return db._insert(room_id, data)

    def query(self, room_id: str):
        return db._query(table_name=room_id)
