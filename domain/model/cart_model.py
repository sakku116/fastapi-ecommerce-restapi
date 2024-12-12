from domain.model import base_model
from typing import Optional
from datetime import datetime

class CartModel(base_model.MyBaseModel):
    _coll_name = "carts"

    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str = ""

    user_id: str


class CartItemModel(base_model.MyBaseModel):
    _coll_name = "cart_items"

    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str = ""

    cart_id: str
    product_id: str
    product_variant_id: Optional[str] = None
    quantity: int