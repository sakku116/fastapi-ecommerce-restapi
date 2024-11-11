from .base_model import MyBaseModel
from typing import Literal, Optional
from pydantic import BaseModel

SORTABLE_FIELDS_ENUMS = Literal["created_at", "updated_at", "title", "price"]
SORTABLE_FIELDS_ENUMS_DEF = "created_at"

QUERIABLE_FIELDS_ENUMS = Literal["name", "brand", "sku"]
QUERIABLE_FIELDS_LIST = ["name", "brand"]
QUERIABLE_FIELDS_ENUMS_DEF = "name"


class ProductModel_Dimensions(BaseModel):
    depth: float = 0
    width: float = 0
    height: float = 0

class ProductModel(MyBaseModel):
    _coll_name = "products"

    category_id: Optional[str] = None

    sku: str
    name: str
    stock: int
    price: float  # dollar
    tags: list[str] = []
    description: Optional[str] = None
    discount_percentage: Optional[float] = None
    brand: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[ProductModel_Dimensions] = None
    img: Optional[str] = None  # filename