from .base_model import MyBaseModel
from typing import Optional, Literal
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

    id: str = ""
    created_at: int = 0
    updated_at: int = 0
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