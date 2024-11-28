from domain.model import base_model
from typing import Optional

class TaxModel(base_model.MyBaseModel):
    _coll_name = "taxes"

    id: str
    created_at: int = 0
    updated_at: int = 0
    created_by: str = ""

    name: str
    rate: float
    description: Optional[str] = None
    location: Optional[str] = None