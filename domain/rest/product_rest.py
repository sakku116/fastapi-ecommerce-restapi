from pydantic import BaseModel
from typing import Optional, Literal
from domain.model import product_model

class GetProductListReq(BaseModel):
    category_id: Optional[str] = None
    query: Optional[str] = None
    query_by: Optional[Literal[product_model.QUERIABLE_FIELDS_ENUMS]] = None
    sort_by: Literal[product_model.SORTABLE_FIELDS_ENUMS] = product_model.SORTABLE_FIELDS_ENUMS_DEF
    sort_order: Literal["asc", "desc"] = "desc"
    page: int = 1
    limit: int = 10

class GetProductListRespDataItem(BaseModel):
    name: str = ""
    price: float = 0
    localized_price: str = ""
    img: Optional[str] = None