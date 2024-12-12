from .base_model import MyBaseModel, _MyBaseModel_Index
from typing import Optional, Literal
from datetime import datetime
from pydantic import field_validator

SORTABLE_FIELDS_ENUMS = Literal["created_at", "updated_at", "name"]
SORTABLE_FIELDS_ENUMS_DEF = "created_at"

QUERIABLE_FIELDS_ENUMS = Literal["name"]
QUERIABLE_FIELDS_LIST = ["name"]
QUERIABLE_FIELDS_ENUMS_DEF = "name"

class CategoryModel(MyBaseModel):
    _coll_name = "categories"
    _bucket_name = "categories"
    _minio_fields = ["img"]
    _custom_indexes = [
        _MyBaseModel_Index(keys=[("created_at", -1)]),
        _MyBaseModel_Index(keys=[("updated_at", -1)]),
        _MyBaseModel_Index(keys=[("name", -1)]),
    ]

    id: str = ""
    created_at: datetime
    updated_at: datetime
    created_by: str = ""
    updated_by: str = ""

    name: str
    description: Optional[str] = None
    img: Optional[str] = None # filename

    @field_validator("name")
    def normalize_name(cls, v):
        if v and isinstance(v, str):
            v = v.strip().lower()

        return v