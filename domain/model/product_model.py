from .base_model import MyBaseModel, _MyBaseModel_Index
from typing import Literal, Optional
from pydantic import BaseModel, field_validator, model_validator
from utils import helper

class ProductModel_Dimensions(BaseModel):
    depth: float = 0
    width: float = 0
    height: float = 0

class ProductModel(MyBaseModel):
    _coll_name = "products"
    _bucket_name = "products"
    _minio_fields = ["images"]
    _custom_indexes = [
        _MyBaseModel_Index(keys=[("created_at", -1)]),
        _MyBaseModel_Index(keys=[("updated_at", -1)]),
        _MyBaseModel_Index(keys=[("category_id", -1)]),
    ]

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
    _custom_indexes = [
        _MyBaseModel_Index(keys=[("product_id", -1)]),
    ]

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
    _custom_indexes = [
        _MyBaseModel_Index(keys=[("created_at", -1)]),
        _MyBaseModel_Index(keys=[("updated_at", -1)]),
        _MyBaseModel_Index(keys=[("product_variant_type_id", -1)]),
    ]

    id: str = ""
    created_at: int = 0
    updated_at: int = 0
    created_by: str = ""
    updated_by: str = ""

    product_id: str
    product_variant_type_id: str = ""
    product_variant_value: str = ""
    is_main: bool = False
    sku: str
    price: float # dollar
    price_currency: str
    price_currency_lang: str
    image: Optional[str] = None  # filename
    discount_percentage: Optional[float] = None
    weight: Optional[float] = None
    dimensions: Optional[ProductModel_Dimensions] = None
    stock: int

    @model_validator(mode="after")
    def validate(self):
        print(self)
        if not helper.isLanguageCodeValid(self.price_currency_lang):
            raise ValueError("price_currency_lang is not valid")

        if not helper.isCurrencyCodeValid(self.price_currency, self.price_currency_lang):
            raise ValueError("price_currency is not valid")

        return self