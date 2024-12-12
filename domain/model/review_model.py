from .base_model import MyBaseModel, _MyBaseModel_Index
from typing import Optional
from pydantic import field_validator, ValidationError
from datetime import datetime

class ReviewModel(MyBaseModel):
    _coll_name = "reviews"
    _bucket_name = "reviews"
    _minio_fields = ["attachments"]
    _custom_indexes = [
        _MyBaseModel_Index(keys=[("created_at", -1)]),
        _MyBaseModel_Index(keys=[("updated_at", -1)]),
        _MyBaseModel_Index(keys=[("product_id", -1)]),
        _MyBaseModel_Index(keys=[("rating", -1)]),
    ]

    id: str = ""
    created_at: datetime
    updated_at: datetime
    created_by: str = ""
    updated_by: str = ""

    user_id: str = ""
    product_id: str
    rating: int
    comment: Optional[str] = None
    attachments: Optional[list] = None # filenames

    @field_validator("rating", mode="before")
    def rating_validator(cls, v):
        if v < 1 or v > 5:
            raise ValidationError("rating is not valid")

        return v