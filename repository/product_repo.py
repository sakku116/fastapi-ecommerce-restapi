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
        self.product_variant_coll = mongo_db.db[
            product_model.ProductVariantModel.getCollName()
        ]
        self.product_variant_type_coll = mongo_db.db[
            product_model.ProductVariantTypeModel.getCollName()
        ]

    ############# PRODUCT ################

    def create(self, product: product_model.ProductModel) -> product_model.ProductModel:
        self.product_coll.insert_one(product.model_dump())

    def getById(self, id: str) -> Union[product_model.ProductModel, None]:
        product = self.product_coll.find_one({"id": id})
        if not product:
            return None
        return product_model.ProductModel(**product) if product else None

    def getByName(self, name: str) -> Union[product_model.ProductModel, None]:
        filter = {}
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
            Literal["name", "brand", "sku"]
        ] = None,  # sort by all possible fields if none
        skip: Optional[int] = None,
        limit: Optional[int] = 10,
        sort_by: Literal[
            Literal["created_at", "updated_at", "title", "price"]
        ] = "created_at",
        sort_order: Literal[-1, 1] = -1,
        do_count: bool = False,
        lookup_variants: bool = True,  # sorted by is_main:1
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
                        for item in ["created_at", "updated_at", "title", "price"]
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

        if lookup_variants:
            facet__paginated_results.extend(
                [
                    {
                        "$lookup": {
                            "from": self.product_variant_coll.name,
                            "localField": "id",
                            "foreignField": "product_id",
                            "as": "variants_",
                            "pipeline": [
                                {"$sort": {"is_main": -1}},
                                {"$project": {"_id": 0}},
                            ],
                        }
                    }
                ]
            )

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

    ############### PRODUCT VARIANT ###############

    def createVariant(self, product_variant: product_model.ProductVariantModel):
        self.product_variant_coll.insert_one(product_variant.model_dump())

    def getProductVariants(
        self,
        product_id: Optional[str] = None,
        product_variant_type_id: Optional[str] = None,
    ) -> list[product_model.ProductVariantModel]:
        if [None, None] == [product_id, product_variant_type_id]:
            raise ValueError(
                "product_id and product_variant_type_id cannot be both None"
            )

        filter = {}
        if product_id != None:
            filter["product_id"] = product_id

        if product_variant_type_id != None:
            filter["product_variant_type_id"] = product_variant_type_id

        variants = self.product_variant_coll.find(filter).sort(
            "is_main", -1
        )
        return [product_model.ProductVariantModel(**variant) for variant in variants]

    def getProductVariant(self, id: str) -> Union[product_model.ProductVariantModel, None]:
        product_variant = self.product_variant_coll.find_one({"id": id})
        if not product_variant:
            return None
        return product_model.ProductVariantModel(**product_variant)

    def getProductVariantBySku(
        self, product_id: str, sku: str
    ) -> Union[product_model.ProductVariantModel, None]:
        variant = self.product_variant_coll.find_one(
            {"sku": sku, "product_id": product_id}
        )
        if not variant:
            return None
        return product_model.ProductVariantModel(**variant)

    ################## PRODUCT VARIANT TYPE #################

    def createVariantType(
        self, product_variant_type: product_model.ProductVariantTypeModel
    ):
        self.product_variant_type_coll.insert_one(product_variant_type.model_dump())

    def updateVariantType(
        self, id: str, product_variant_type: product_model.ProductVariantTypeModel
    ) -> Optional[product_model.ProductVariantModel]:
        res = self.product_variant_type_coll.find_one_and_update(
            {"id": id},
            {"$set": product_variant_type.model_dump(exclude=["id"])},
            return_document=ReturnDocument.AFTER,
        )
        return product_model.ProductVariantTypeModel(**res) if res else None

    def deleteVariantType(
        self, id: str
    ) -> Optional[product_model.ProductVariantTypeModel]:
        res = self.product_variant_type_coll.find_one_and_delete(
            {"id": id}, return_document=ReturnDocument.AFTER
        )
        return product_model.ProductVariantTypeModel(**res) if res else None

    def getOneVariantType(
        self, id: str
    ) -> Optional[product_model.ProductVariantTypeModel]:
        res = self.product_variant_type_coll.find_one({"id": id})
        return product_model.ProductVariantTypeModel(**res) if res else None

    def getManyVariantType(
        self, product_id: str
    ) -> list[product_model.ProductVariantTypeModel]:
        res = self.product_variant_type_coll.find({"product_id": product_id})
        return [product_model.ProductVariantTypeModel(**item) for item in res]
