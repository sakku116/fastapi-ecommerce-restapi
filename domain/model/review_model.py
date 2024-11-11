from .base_model import MyBaseModel
from typing import Optional
from pydantic import field_validator, ValidationError

class ReviewModel(MyBaseModel):
    _coll_name = "reviews"

    user_id: str = ""
    product_id: str
    rating: int
    comment: Optional[int] = None

    @field_validator("rating", mode="before")
    def rating_validator(cls, v):
        if v < 1 or v > 5:
            raise ValidationError("rating is not valid")

        return v