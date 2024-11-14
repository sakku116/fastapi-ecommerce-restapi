from domain.model import product_model
from typing import Optional


class GetProductListResItem(product_model.ProductModel):
    variants_: Optional[list[product_model.ProductVariantModel]] = None
