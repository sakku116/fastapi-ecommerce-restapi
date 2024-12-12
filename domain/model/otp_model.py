from .base_model import MyBaseModel, _MyBaseModel_Index
from datetime import datetime

class OtpModel(MyBaseModel):
    _coll_name = "otps"
    _custom_indexes = [
        _MyBaseModel_Index(keys=[("user_id", -1)]),
    ]

    id: str = ""
    created_at: datetime
    updated_at: datetime
    created_by: str = ""

    verified: bool = False
    code: str = ""