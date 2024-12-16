from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from domain.model import cart_model

class BaseCartItemDetail(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    product_name: str
    quantity: int
    description: Optional[str] = None
    price_per_unit: float
    price_per_unit_currency: str
    localized_price_per_unit: str

class AddToChartReq(BaseModel):
    product_id: str
    product_variant_id: str
    quantity: int

class AddToCartRespData(BaseCartItemDetail):
    pass

class GetUserCartDetailRespData(BaseModel):
    localized_total_price: str
    total_items: int

class UpdateCartItemReq(BaseModel):
    quantity: Optional[int] = None
    description: Optional[str] = None # use string 'null' to set it to null

class UpdateCartItemRespData(BaseCartItemDetail):
    pass

class DeleteCartItemRespData(cart_model.CartItemModel):
    pass

class GetChartItemsRespDataItem(BaseCartItemDetail):
    pass