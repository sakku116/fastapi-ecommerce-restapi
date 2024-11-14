from .base_model import MyBaseModel
from typing import Optional
from pydantic import field_validator, ValidationError

class ReviewModel(MyBaseModel):
    _coll_name = "reviews"
    _bucket_name = "reviews"
    _minio_fields = ["attachments"]

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