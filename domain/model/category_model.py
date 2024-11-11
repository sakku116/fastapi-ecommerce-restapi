from .base_model import MyBaseModel
from typing import Optional, Literal

SORTABLE_FIELDS_ENUMS = Literal["created_at", "updated_at", "name"]
SORTABLE_FIELDS_ENUMS_DEF = "created_at"

QUERIABLE_FIELDS_ENUMS = Literal["name"]
QUERIABLE_FIELDS_LIST = ["name"]
QUERIABLE_FIELDS_ENUMS_DEF = "name"

class CategoryModel(MyBaseModel):
    _coll_name = "categories"

    name: str
    description: Optional[str] = None
