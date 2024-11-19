from .base_model import MyBaseModel

class RefreshTokenModel(MyBaseModel):
    _coll_name = "refresh_tokens"
    _custom_int64_fields = ["expired_at"]

    id: str = ""
    created_at: int = 0
    created_by: str = ""

    # use id for the token
    expired_at: int = 0