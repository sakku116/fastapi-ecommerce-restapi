from pymongo import MongoClient
from pymongo.database import Database

from .env import Env

class MongodbClient:
    conn: MongoClient = None
    db: Database = None

    @classmethod
    def init(cls):
        cls.conn = MongoClient(Env.MONGODB_URI)
        cls.db = cls.conn[Env.MONGODB_NAME]

    @classmethod
    def close(cls):
        cls.conn.close()
