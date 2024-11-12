from fastapi import Depends
from config.mongodb import MongodbClient
from domain.model import category_model
from pymongo import ReturnDocument
from typing import Union, Optional, Literal
from core.logging import logger
from utils import helper
from domain.dto import category_dto


class CategoryRepo:
    def __init__(self, mongo_db: MongodbClient = Depends()):
        self.category_coll = mongo_db.db[category_model.CategoryModel.getCollName()]

    def create(
        self, category: category_model.CategoryModel
    ):
        self.category_coll.insert_one(category.model_dump())

    def getById(
        self, id: str
    ) -> Union[category_model.CategoryModel, None]:
        category = self.category_coll.find_one({"id": id})
        if not category:
            return None
        return category_model.CategoryModel(**category)

    def getByName(
        self, name: str
    ) -> Union[category_model.CategoryModel, None]:
        category = self.category_coll.find_one({"name": name})
        if not category:
            return None
        return category_model.CategoryModel(**category)

    def delete(self, id: str) -> Union[category_model.CategoryModel, None]:
        category = self.category_coll.find_one_and_delete({"id": id})
        if not category:
            return None
        return category_model.CategoryModel(**category)

    def update(
        self, id: str, category: category_model.CategoryModel
    ) -> Union[category_model.CategoryModel, None]:
        category = self.category_coll.find_one_and_update(
            {"id": id},
            {"$set": category.model_dump(exclude=["id"])},
            return_document=ReturnDocument.AFTER,
        )
        return category_model.CategoryModel(**category) if category else None

    def getList(
        self,
        query: Optional[str] = None,
        query_by: Optional[
            Literal[category_model.QUERIABLE_FIELDS_ENUMS]
        ] = None,  # sort by all possible fields if none
        skip: Optional[int] = None,
        limit: Optional[int] = 10,
        sort_by: Literal[
            category_model.SORTABLE_FIELDS_ENUMS
        ] = category_model.SORTABLE_FIELDS_ENUMS_DEF,
        sort_order: Literal[-1, 1] = -1,
        do_count: bool = False,
    ) -> tuple[list[category_dto.GetListResItem], int]:
        pipeline = []
        match1 = {}
        match1_or = []

        if query != None:
            if query_by == None:
                match1_or.extend(
                    [
                        {item: {"$regex": query, "$options": "i"}}
                        for item in category_model.QUERIABLE_FIELDS_LIST
                    ]
                )
            else:
                match1[query_by] = {"$regex": query, "$options": "i"}

        if match1_or:
            match1["$or"] = match1_or

        if match1:
            pipeline.append({"$match": match1})

        pipeline.append({"$sort": {sort_by: sort_order}})

        facet = {}
        facet__paginated_results = []
        if skip != None:
            facet__paginated_results.append({"$skip": skip})

        if limit != None:
            facet__paginated_results.append({"$limit": limit})

        facet["paginated_results"] = facet__paginated_results

        if do_count:
            facet["total"] = [{"$count": "count"}]

        pipeline.extend(
            [
                {"$facet": facet},
                {"$unwind": "$total"},
                {
                    "$project": {
                        "total": "$total.count",
                        "paginated_results": "$paginated_results",
                    }
                },
            ]
        )
        # logger.debug(f"pipeline: {helper.prettyJson(pipeline)}")

        cursor = list(self.category_coll.aggregate(pipeline))

        products = []
        count = 0

        try:
            products = [
                category_dto.GetListResItem(**product)
                for product in cursor[0].get("paginated_results") or []
            ]
        except Exception as e:
            logger.warning(f"cusor is empty: {e}")

        try:
            count = cursor[0].get("total") or 0
        except Exception as e:
            logger.warning(f"cursor is empty: {e}")

        return products, count

