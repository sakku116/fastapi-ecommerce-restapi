from fastapi import Depends
from config.mongodb import MongodbClient
from domain.model import wallet_model
from pymongo import ReturnDocument
from typing import Union


class WalletRepo:
    def __init__(self, mongo_db: MongodbClient = Depends()):
        self.wallet_coll = mongo_db.db[wallet_model.WalletModel.getCollName()]

    def create(self, data: wallet_model.WalletModel):
        self.wallet_coll.insert_one(data.model_dump())

    def getByUserId(self, user_id: str) -> Union[wallet_model.WalletModel, None]:
        wallet = self.wallet_coll.find_one({"user_id": user_id})
        return wallet_model.WalletModel(**wallet) if wallet else None

    def update(self, id: str, data: wallet_model.WalletModel) -> int:
        result = self.wallet_coll.update_one(
            {"id": id},
            {"$set": data.model_dump(exclude=["id"])},
        )

        return result.modified_count
