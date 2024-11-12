import mimetypes
from datetime import timedelta
from typing import Literal

from bson.int64 import Int64
from minio import Minio
from pydantic import BaseModel, PrivateAttr
from pydantic.fields import ModelPrivateAttr

from core.logging import logger


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

    _default_indexes: list[_MyBaseModel_Index] = [
        _MyBaseModel_Index(keys=[("id", 1)], unique=True)
    ]
    _custom_indexes: list[_MyBaseModel_Index] = []

    _default_int64_fields: list[str] = ["created_at", "updated_at"]
    _custom_int64_fields: list[str] = []

    _bucket_name: ModelPrivateAttr = PrivateAttr("")
    _minio_fields: list[str] = []

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

    def urlizeMinioFields(
        self, minio_client: Minio, mode: Literal["download", "view"] = "view"
    ):
        if not self._bucket_name or not self._minio_fields:
            logger.warning(f"urlizeMinioFields: skip. _bucket_name: {self._bucket_name}, _minio_fields: {self._minio_fields}")

        else:
            for field in self._minio_fields:
                if field in self.model_dump():
                    try:
                        setattr(
                            self,
                            field,
                            minio_client.presigned_get_object(
                                bucket_name=self._bucket_name,
                                object_name=getattr(self, field),
                                expires=timedelta(days=1),
                                response_headers=(
                                    {
                                        "response-content-disposition": "inline",
                                        "response-content-type": mimetypes.guess_type(
                                            getattr(self, field)
                                        )[0],
                                    }
                                    if mode == "view"
                                    else None
                                ),
                            ),
                        )
                    except Exception as e:
                        logger.warning(e)

        return self

    @classmethod
    def getCollName(cls) -> str:
        return cls._coll_name.get_default()

    @classmethod
    def getBucketName(cls) -> str:
        return cls._bucket_name.get_default()

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
