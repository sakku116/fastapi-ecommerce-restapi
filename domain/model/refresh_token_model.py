from .base_model import MyBaseModel
from datetime import datetime

class RefreshTokenModel(MyBaseModel):
    _coll_name = "refresh_tokens"

    id: str = ""
    created_at: datetime
    created_by: datetime

    # use id for the token
    expired_at: datetime