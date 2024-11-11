from fastapi import Depends
from config.mongodb import MongodbClient
from domain.model import product_model
from pymongo import ReturnDocument
from typing import Union, Optional, Literal
from domain.dto import product_dto
from core.logging import logger
from utils import helper


class ProductRepo:
    def __init__(self, mongo_db: MongodbClient = Depends()):
        self.product_coll = mongo_db.db[product_model.ProductModel.getCollName()]

    def create(self, product: product_model.ProductModel) -> product_model.ProductModel:
        self.product_coll.insert_one(product.model_dump())

    def getById(self, product_id: str) -> Union[product_model.ProductModel, None]:
        product = self.product_coll.find_one({"id": product_id})
        if not product:
            return None
        return product_model.ProductModel(**product)

    def get(
        self, sku: str = None, name: str = None
    ) -> Union[product_model.ProductModel, None]:
        if [sku, name].count(None) == 2:
            return ValueError("parameters needed")

        filter = {}
        if sku != None:
            filter["sku"] = sku
        if name != None:
            filter["name"] = name
        product = self.product_coll.find_one(filter)
        if not product:
            return None

        return product_model.ProductModel(**product)

    def delete(self, id: str) -> Union[product_model.ProductModel, None]:
        product = self.product_coll.find_one_and_delete({"id": id})
        if not product:
            return None
        return product_model.ProductModel(**product)

    def update(
        self, id: str, product: product_model.ProductModel
    ) -> Union[product_model.ProductModel, None]:
        product = self.product_coll.find_one_and_update(
            {"id": id},
            {"$set": product.model_dump(exclude=["id"])},
            return_document=ReturnDocument.AFTER,
        )
        return product_model.ProductModel(**product) if product else None

    def getList(
        self,
        category_id: Optional[str] = None,
        query: Optional[str] = None,
        query_by: Optional[
            Literal[product_model.QUERIABLE_FIELDS_ENUMS]
        ] = None,  # sort by all possible fields if none
        skip: Optional[int] = None,
        limit: Optional[int] = 10,
        sort_by: Literal[
            product_model.SORTABLE_FIELDS_ENUMS
        ] = product_model.SORTABLE_FIELDS_ENUMS_DEF,
        sort_order: Literal[-1, 1] = -1,
        do_count: bool = False,
    ) -> tuple[list[product_dto.GetProductListResItem], int]:
        pipeline = []
        match1 = {}
        match1_or = []

        if category_id != None:
            match1["category_id"] = category_id

        if query != None:
            if query_by == None:
                match1_or.extend(
                    [
                        {item: {"$regex": query, "$options": "i"}}
                        for item in product_model.QUERIABLE_FIELDS_LIST
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
        logger.debug(f"pipeline: {helper.prettyJson(pipeline)}")

        cursor = list(self.product_coll.aggregate(pipeline))

        products = []
        count = 0

        try:
            products = [
                product_dto.GetProductListResItem(**product)
                for product in cursor[0].get("paginated_results") or []
            ]
        except Exception as e:
            logger.warning(f"cusor is empty: {e}")

        try:
            count = cursor[0].get("total") or 0
        except Exception as e:
            logger.warning(f"cursor is empty: {e}")

        return products, count