from typing import Union, Optional

from fastapi import Depends
from pymongo import ReturnDocument

from config.mongodb import MongodbClient
from core.logging import logger
from domain.model import review_model
from utils import helper


class ReviewRepo:
    def __init__(self, mongo_db: MongodbClient = Depends()):
        self.review_coll = mongo_db.db[review_model.ReviewModel.getCollName()]

    def create(self, review: review_model.ReviewModel):
        self.review_coll.insert_one(review.model_dump())

    def getById(self, id: str) -> Union[review_model.ReviewModel, None]:
        review = self.review_coll.find_one({"id": id})
        return review_model.ReviewModel(**review) if review else None

    def delete(self, id: str) -> Union[review_model.ReviewModel, None]:
        review = self.review_coll.find_one_and_delete({"id": id})
        return review_model.ReviewModel(**review) if review else None

    def update(
        self, id: str, review: review_model.ReviewModel
    ) -> Union[review_model.ReviewModel, None]:
        review = self.review_coll.find_one_and_update(
            {"id": id},
            {"$set": review.model_dump()},
            return_document=ReturnDocument.AFTER,
        )
        return review_model.ReviewModel(**review) if review else None

    def getRatingAverage(self, product_id: str) -> float:
        pipeline = [
            {"$match": {"product_id": product_id}},
            {"$group": {"_id": "$product_id", "average_rating": {"$avg": "$rating"}}},
        ]
        result = list(self.review_coll.aggregate(pipeline))
        if result:
            return result[0]["average_rating"]
        else:
            return 0

    def get(
        self,
        user_id: Optional[str] = None,
        product_id: Optional[str] = None,
        rating: Optional[int] = None,
    ) -> Union[review_model.ReviewModel, None]:
        if [user_id, product_id, rating].count(None) == 3:
            raise ValueError(
                "at least one of user_id, product_id, rating must be provided"
            )

        filter = {}
        if user_id:
            filter["user_id"] = user_id
        if product_id:
            filter["product_id"] = product_id
        if rating:
            filter["rating"] = rating

        logger.debug(f"filter: {filter}")

        review = self.review_coll.find_one(filter)
        logger.debug(f"review: {review}")
        return review_model.ReviewModel(**review) if review else None
