from pydantic import BaseModel
from domain.model import category_model
from typing import Optional, Literal

class GetCategoryListReq(BaseModel):
    query: Optional[str] = None
    query_by: Optional[Literal[category_model.QUERIABLE_FIELDS_ENUMS]] = None
    sort_by: Literal[category_model.SORTABLE_FIELDS_ENUMS] = category_model.SORTABLE_FIELDS_ENUMS_DEF
    sort_order: Literal["asc", "desc"] = "desc"
    page: int = 1
    limit: int = 10

class GetCategoryListRespDataItem(category_model.CategoryModel):
    pass
