from pydantic import BaseModel, PrivateAttr
from pydantic.fields import ModelPrivateAttr
from bson.int64 import Int64


class _MyBaseModel_Index(BaseModel):
    """
    this attributes is same as pymongo.collection.Collection.create_index() args
    """

    keys: list[tuple] = []
    unique: bool = False


class MyBaseModel(BaseModel):
    """
    id field already indexed by default, but it need to be indexed manually if you set the _indexes field.
    """
    _coll_name: ModelPrivateAttr = PrivateAttr("")
    _bucket_name: ModelPrivateAttr = PrivateAttr("")
    _default_indexes: list[_MyBaseModel_Index] = [
        _MyBaseModel_Index(keys=[("id", 1)], unique=True)
    ]
    _custom_indexes: list[_MyBaseModel_Index] = []
    _default_int64_fields: list[str] = ["created_at", "updated_at"]
    _custom_int64_fields: list[str] = []

    id: str = ""
    created_at: int = 0
    updated_at: int = 0
    created_by: str = ""
    updated_by: str = ""

    def model_dump(self, **kwargs) -> dict:
        data = super().model_dump(**kwargs)
        for field in self._custom_int64_fields + self._default_int64_fields:
            if field in data:
                data[field] = Int64(data[field])
        return data


    @classmethod
    def getCollName(cls):
        return cls._coll_name.get_default()

    @classmethod
    def getDefaultIndexes(cls):
        return cls._default_indexes.get_default()

    @classmethod
    def getCustomIndexes(cls):
        return cls._custom_indexes.get_default()

    @classmethod
    def getDefaultInt64Fields(cls):
        return cls._default_int64_fields.get_default()

    @classmethod
    def getCustomInt64Fields(cls):
        return cls._custom_int64_fields.get_default()