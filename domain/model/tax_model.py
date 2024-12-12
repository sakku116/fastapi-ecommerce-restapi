from domain.model import base_model
from typing import Optional
from datetime import datetime

class TaxModel(base_model.MyBaseModel):
    _coll_name = "taxes"

    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str = ""

    name: str
    rate: float
    description: Optional[str] = None
    location: Optional[str] = None