from domain.model import base_model
from typing import Optional, Literal

ORDER_STATUS_ENUMS = Literal["pending", "completed", "canceled"]
ORDER_STATUS_ENUMS_DEF = "pending"

class OrderModel(base_model.MyBaseModel):
    _coll_name = "orders"
    _custom_indexes = [
        base_model._MyBaseModel_Index(keys=[("user_id", -1)]),
    ]

    id: str
    created_at: int = 0
    updated_at: int = 0
    created_by: str = ""

    user_id: str
    total_price: float
    status: Literal[ORDER_STATUS_ENUMS] = ORDER_STATUS_ENUMS_DEF

class OrderItemModel(base_model.MyBaseModel):
    _coll_name = "order_items"
    _custom_indexes = [
        base_model._MyBaseModel_Index(keys=[("created_at", -1)]),
        base_model._MyBaseModel_Index(keys=[("updated_at", -1)]),
        base_model._MyBaseModel_Index(keys=[("order_id", -1)]),
        base_model._MyBaseModel_Index(keys=[("product_id", -1)]),
        base_model._MyBaseModel_Index(keys=[("product_variant_id", -1)]),
    ]

    id: str
    created_at: int = 0
    updated_at: int = 0
    created_by: str = ""

    order_id: str
    product_id: str
    product_variant_id: Optional[str] = None
    price: float
    quantity: int
    discount_precentage: Optional[float] = None

    def calculate_final_price(self) -> float:
        final_price = self.price * self.quantity
        if self.discount_precentage:
            final_price = final_price - (final_price * self.discount_precentage)

        return final_price