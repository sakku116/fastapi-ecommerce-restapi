from .base_model import MyBaseModel
from typing import Literal, Optional
from pydantic import BaseModel, field_validator

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

    id: str = ""
    created_at: int = 0
    updated_at: int = 0
    created_by: str = ""
    updated_by: str = ""

    category_id: Optional[str] = None

    name: str
    brand: Optional[str] = None
    description: Optional[str] = None
    tags: list[str] = []
    images: Optional[list[str]] = None  # filenames

class ProductVariantTypeModel(MyBaseModel):
    _coll_name = "product_variant_types"

    id: str = ""
    created_at: int = 0
    updated_at: int = 0
    created_by: str = ""
    updated_by: str = ""

    product_id: str
    name: str

    @field_validator("name")
    def normalize_name(cls, v):
        if v and isinstance(v, str):
            v = v.strip().lower()

        return v

class ProductVariantModel(MyBaseModel):
    """
    product must be at least has one variant for default
    """

    _coll_name = "product_variants"
    _bucket_name = "products"
    _minio_fields = ["image"]

    id: str = ""
    created_at: int = 0
    updated_at: int = 0
    created_by: str = ""
    updated_by: str = ""

    product_id: str
    product_variant_type_id: str = ""
    product_variant_name: str
    is_main: bool = False
    sku: str
    price: float # dollar
    image: Optional[str] = None  # filename
    discount_percentage: Optional[float] = None
    weight: Optional[float] = None
    dimensions: Optional[ProductModel_Dimensions] = None
    stock: int