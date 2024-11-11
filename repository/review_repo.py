from fastapi import Depends
from config.mongodb import MongodbClient
from domain.model import review_model
from pymongo import ReturnDocument
from core.logging import logger
from utils import helper


class ReviewRepo:
    def __init__(self, mongo_db: MongodbClient = Depends()):
        self.review_coll = mongo_db.db[review_model.ReviewModel.getCollName()]