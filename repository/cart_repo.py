from fastapi import Depends
from config.mongodb import MongodbClient
from domain.model import cart_model
from pymongo import ReturnDocument
from typing import Union, Optional, Literal
from core.logging import logger
from utils import helper
from domain.dto import cart_dto


class CartRepo:
    def __init__(self, mongo_db: MongodbClient = Depends()):
        self.cart_coll = mongo_db.db[cart_model.CartModel.getCollName()]

    def create(self, cart: cart_model.CartModel):
        self.cart_coll.insert_one(cart.model_dump())

    def getById(self, id: str) -> Union[cart_model.CartModel, None]:
        cart = self.cart_coll.find_one({"id": id})
        if not cart:
            return None
        return cart_model.CartModel(**cart)

    def getByUserId(self, user_id: str) -> Union[cart_model.CartModel, None]:
        cart = self.cart_coll.find_one({"user_id": user_id})
        return cart_model.CartModel(**cart) if cart else None

    def delete(self, id: str) -> Union[cart_model.CartModel, None]:
        cart = self.cart_coll.find_one_and_delete({"id": id})
        if not cart:
            return None
        return cart_model.CartModel(**cart)

    def update(
        self, id: str, cart: cart_model.CartModel
    ) -> Union[cart_model.CartModel, None]:
        cart = self.cart_coll.find_one_and_update(
            {"id": id},
            {"$set": cart.model_dump(exclude=["id"])},
            return_document=ReturnDocument.AFTER,
        )
        return cart_model.CartModel(**cart) if cart else None

    def getList(
        self,
        query: Optional[str] = None,
        query_by: Optional[
            Literal["name"]
        ] = None,  # sort by all possible fields if none
        skip: Optional[int] = None,
        limit: Optional[int] = 10,
        sort_by: Literal["created_at", "updated_at", "name"] = "updated_at",
        sort_order: Literal[-1, 1] = -1,
        do_count: bool = False,
    ) -> tuple[list[cart_dto.GetListResItem], int]:
        pipeline = []
        match1 = {}
        match1_or = []

        if query != None:
            if query_by == None:
                match1_or.extend(
                    [{item: {"$regex": query, "$options": "i"}} for item in ["name"]]
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

        cursor = list(self.cart_coll.aggregate(pipeline))

        products = []
        count = 0

        try:
            products = [
                cart_dto.GetListResItem(**product)
                for product in cursor[0].get("paginated_results") or []
            ]
        except Exception as e:
            logger.warning(f"cusor is empty: {e}")

        try:
            count = cursor[0].get("total") or 0
        except Exception as e:
            logger.warning(f"cursor is empty: {e}")

        return products, count

    ############# CART ITEM ##############
    def createCartItem(self, cart_item: cart_model.CartItemModel):
        self.cart_coll.insert_one(cart_item.model_dump())

    def updateCartItem(
        self, id: str, cart_item: cart_model.CartItemModel
    ) -> Optional[cart_model.CartItemModel]:
        cart_item = self.cart_coll.find_one_and_update(
            {"id": id},
            {"$set": cart_item.model_dump(exclude=["id"])},
            return_document=ReturnDocument.AFTER,
        )
        if not cart_item:
            return None
        return cart_model.CartItemModel(**cart_item)

    def getCartItem(
        self,
        cart_id: Optional[str] = None,
        product_id: Optional[str] = None,
        product_variant_id: Optional[str] = None,
    ) -> Union[cart_model.CartItemModel, None]:
        if [None, None, None] == [cart_id, product_id, product_variant_id]:
            raise ValueError(
                "cart_id, product_id and product_variant_id cannot be all None"
            )

        filter = {}
        if cart_id != None:
            filter["cart_id"] = cart_id
        if product_id != None:
            filter["product_id"] = product_id
        if product_variant_id != None:
            filter["product_variant_id"] = product_variant_id

        cart_item = self.cart_coll.find_one(filter)
        if not cart_item:
            return None
        return cart_model.CartItemModel(**cart_item)

    def getCartItemById(self, id: str) -> Union[cart_model.CartItemModel, None]:
        cart_item = self.cart_coll.find_one({"id": id})
        if not cart_item:
            return None
        return cart_model.CartItemModel(**cart_item)

    def getCartItemsByCartId(self, cart_id: str) -> list[cart_model.CartItemModel]:
        cart_items = self.cart_coll.find({"cart_id": cart_id})
        return [cart_model.CartItemModel(**cart_item) for cart_item in cart_items]

    def deleteCartItem(self, id: str) -> Optional[cart_model.CartItemModel]:
        cart_item = self.cart_coll.find_one_and_delete({"id": id})
        if not cart_item:
            return None
        return cart_model.CartItemModel(**cart_item)
