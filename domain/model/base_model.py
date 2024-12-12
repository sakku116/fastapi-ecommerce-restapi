import mimetypes
from datetime import timedelta
from typing import Literal, Optional, Union

from bson.int64 import Int64
from minio import Minio
from pydantic import BaseModel, PrivateAttr
from pydantic.fields import ModelPrivateAttr

from core.logging import logger
from utils import helper


class _MyBaseModel_Index(BaseModel):
    """
    this attributes is same as pymongo.collection.Collection.create_index() args
    """

    keys: list[tuple] = []
    unique: bool = False


class MinioUtil(BaseModel):
    _bucket_name: ModelPrivateAttr = PrivateAttr("")
    _minio_fields: ModelPrivateAttr = PrivateAttr([])

    @classmethod
    def getBucketName(cls) -> str:
        return cls._bucket_name.get_default()

    @classmethod
    def getMinioFields(cls) -> list[str]:
        return cls._minio_fields.get_default()

    def urlizeMinioFields(
        self, minio_client: Minio, mode: Literal["download", "view"] = "view"
    ):
        if not self._bucket_name or not self._minio_fields:
            logger.warning(
                f"urlizeMinioFields: skip. self._bucket_name: {self._bucket_name}, self._minio_fields: {self._minio_fields}"
            )

        else:
            for field_name in self._minio_fields:
                if getattr(self, field_name, None):
                    raw_value: Union[list[str], str] = getattr(self, field_name, None)

                    if raw_value:
                        value: Union[list[str], str, None] = None

                        if isinstance(raw_value, list):
                            value = [
                                minio_client.presigned_get_object(
                                    bucket_name=self._bucket_name,
                                    object_name=getattr(self, item),
                                    expires=timedelta(days=1),
                                    response_headers=(
                                        {
                                            "response-content-disposition": "inline",
                                            "response-content-type": mimetypes.guess_type(
                                                getattr(self, item)
                                            )[
                                                0
                                            ],
                                        }
                                        if mode == "view"
                                        else None
                                    ),
                                )
                                for item in raw_value
                            ]

                        elif isinstance(raw_value, str):
                            value = minio_client.presigned_get_object(
                                bucket_name=self._bucket_name,
                                object_name=raw_value,
                                expires=timedelta(days=1),
                                response_headers=(
                                    {
                                        "response-content-disposition": "inline",
                                        "response-content-type": mimetypes.guess_type(
                                            raw_value
                                        )[0],
                                    }
                                    if mode == "view"
                                    else None
                                ),
                            )

                        if value:
                            try:
                                setattr(self, field_name, value)
                            except Exception as e:
                                logger.warning(e)

        return self

class MyBaseModel(MinioUtil):
    """
    id field already indexed by default, but it need to be indexed manually if you set the _indexes field.
    """

    _coll_name: ModelPrivateAttr = PrivateAttr("")

    _default_indexes: list[_MyBaseModel_Index] = [
        _MyBaseModel_Index(keys=[("id", 1)], unique=True)
    ]
    _custom_indexes: list[_MyBaseModel_Index] = []

    _custom_int64_fields: list[str] = []

    id: str

    @classmethod
    def getCollName(cls) -> str:
        return cls._coll_name.get_default()

    @classmethod
    def getDefaultIndexes(cls):
        return cls._default_indexes.get_default()

    @classmethod
    def getCustomIndexes(cls):
        return cls._custom_indexes.get_default()