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
    _bucket_name = "products"
    _minio_fields = ["images"]

    category_id: Optional[str] = None

    name: str
    brand: Optional[str] = None
    description: Optional[str] = None
    tags: list[str] = []
    images: Optional[list[str]] = None  # filenames

class ProductVariantModel(MyBaseModel):
    """
    product must be at least has one variant for default
    """

    _coll_name = "product_variants"
    _bucket_name = "products"
    _minio_fields = ["image"]

    is_main: bool = False
    product_id: str
    image: Optional[str] = None  # filename
    sku: str
    price: float # dollar
    discount_percentage: Optional[float] = None
    weight: Optional[float] = None
    dimensions: Optional[ProductModel_Dimensions] = None
    stock: int

    # variant type (all empty means default)
    size: Optional[int] = None
    model: Optional[str] = None
    color: Optional[str] = None